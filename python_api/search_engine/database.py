import os
from openai import OpenAI
import dotenv
import json
from datetime import datetime as dt
from uuid import uuid4
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

from utils.misc import embed_text, parse_API_response_for_CV
from utils.tools import cv_tools
from utils.logging import system_logger, database_logger
from utils.misc import (result_to_html, handle_null_embedding, validate_start_end_date, 
                        validate_salary, lookup_table_sectors, clean_nan_values, bulk_insert_documents)

with open('python_api/assets/mappings.json', 'r') as f:
    mappings = json.load(f)
name_to_mappings = {
                "jobs": mappings[0],
                "job_link": mappings[1],
                "company": mappings[2],
                "location": mappings[3],
                "sector": mappings[4],
                "user": mappings[5]
            }
class FeatureExtractor:
    '''
    Utility wrapper class for extracting features from a piece of text (location and resume for now.) using Google's GEMINI API

    Input:
    - GEMINI_API_KEY: str -  API key for Google's GEMINI API
    '''
    def __init__(self, GEMINI_API_KEY=None):
        if GEMINI_API_KEY is None:
            raise Exception("Please provide a valid API key for Google's GEMINI API")
        
        self.client = OpenAI(
            api_key=GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
    def fields_from_resume(self, text):
        request_id = uuid4()
        extra_info = {'service': 'feature_extraction', 'request_id': request_id}
        try:
            chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant that only has access to tools to respond to user queries, so you should use the available tools."},
                {"role": "user", "content": text}
            ],
            tools = cv_tools,
            model="gemini-2.0-flash",
            stream=False
        )
            information = parse_API_response_for_CV(chat_completion)
            database_logger.info(f"Extracted information from the resume.", extra=extra_info)
            return information, request_id
        except Exception as e:
            database_logger.error(f"An error occurred while extracting features from the resume: {e}", extra=extra_info, exc_info=True)
            return None, request_id
class DatabaseManager:
    '''
    Utility wrapper class for managing the database of the application

    Input:
    - GEMINI_API_KEY: str -  API key for Google's GEMINI API
    - database_client: Elasticsearch - An instance of the Elasticsearch class
    '''
    def __init__(self, GEMINI_API_KEY=None, database_client: Elasticsearch | None = None):
        if GEMINI_API_KEY is None:
            raise Exception("Please provide a valid API key for Google's GEMINI LLM")
        
        self._feature_extractor = FeatureExtractor(GEMINI_API_KEY)
        self._database_client = database_client
    def prepare_user_profile(self, text=None, push=False):
        '''
        Method for preparing a user profile from a resume text, with optional push to the database

        Parameters:
            - text: str - The resume text
            - push: bool - Whether to push the user profile to the database
        '''
        if not text: 
            document = {
                'userID': -1,
                'dateUploaded': dt.now().isoformat(timespec="seconds") + 'Z',
                'CV_information': None
            }
            return document, None
    
        information, request_id = self._feature_extractor.fields_from_resume(text)

        current_id = self._database_client.count(index='user')['count'] + 1

        embedded_information = {
            'experience_embedding': embed_text(information['experience'])[0],
            'soft_skill_embedding': embed_text(information['soft_skill'])[0],
            'technical_skill_embedding': embed_text(information['technical_skill'])[0],
            'degree_embedding': embed_text(information['degree'])[0]
        }

        document = {
            'userID': current_id,
            'dateUploaded': dt.now().isoformat(timespec="seconds") + 'Z',
            'CV_information': embedded_information
        }
        if push:
            self._database_client.index(index='user', body=document)
        else:
            pass

        return document, request_id
    def setup(self, extra_info=None):
        for key in name_to_mappings:
            if self._database_client.indices.exists(index=key):
                database_logger.info(f"Index {key} already exists. Skipping creation.")
            else:
                response = self._database_client.indices.create(index=key, body=name_to_mappings[key])
                if response:
                    database_logger.info(f"Index {key} created successfully.", extra=extra_info)
                else:
                    database_logger.error(f"Error occurred while creating index {key}.", extra=extra_info)
                
        # Setting up locations in the database.
        documents = _prepare_locations()
        for document in documents:
            self._database_client.index(index='location', document=document)
        database_logger.info("Finished adding initial locations to the database, down to district level.", extra=extra_info)
        
        # Setting up sectors in the database
        documents = _prepare_sectors()
        for document in documents:
            self._database_client.index(index='location', document=document)
        database_logger.info("Finished adding initial criteria weights for 12 GICS sectors.", extra=extra_info)

    def push_jobs(self, jobs_df):
        '''
        Method for pushing jobs to the database

        Parameters:
        - jobs_df: DataFrame - A DataFrame containing the jobs to be pushed to the database
        '''
        job_docs = []
        job_link_docs = []
        for i in range(len(jobs_df)):
            row = jobs_df.iloc[i].to_dict()

            row = handle_null_embedding(row)
            
            city = row.get('City', '')
            district = row.get('District', '')

            try:
                start, end = validate_start_end_date(row['Job_Date-open'], row['Job_Date-end'])
            except:
                continue

            try:
                sec_id = lookup_table_sectors[row['Job_Sector']]
            except:
                sec_id = -1

            min_salary, max_salary = validate_salary(row['Min_Salary'], row['Max_Salary'])

            job_entry = {
                "JOB_ID": row['Job ID'],
                "location_primary": city,
                "location_secondary": district,
                "date_opened": start,
                "deadline": end,
                "title": row['Title'],
                "description": row['Main_Job_Description'],
                "companyID": None,
                "job_information": {
                        "experience_embedding": row['Candidate_Experience_Requirements_embedding'],
                        "soft_skill_embedding": row['Candidate_soft_skill_Requirements_embedding'],
                        "technical_skill_embedding": row['Candidate_technical_skill_Requirements_embedding'],
                        "degree_embedding": row['Candidate_degree_Requirements_embedding'] 
                },
                "workingTime": row['Job_Type'],
                "salary_min": min_salary,
                "salary_max": max_salary,
                "sectorID": sec_id,
                "additional_notes": str(row['Additional_Notes']) + ' ' + str(row['Sex_Requirement']),
                "date_processed": dt.now().isoformat(timespec='seconds') + 'Z'
            }

            job_link_entry = {
                        "joblink_id": i,
                        "JOB_ID": row['Job ID'],
                        "link": row['Link'],
                        "date_processed": dt.now().isoformat(timespec='seconds') + 'Z'
                   }
            
            job_entry = clean_nan_values(job_entry)
            job_link_entry = clean_nan_values(job_link_entry)
            job_docs.append(job_entry)
            job_link_docs.append(job_link_entry)

        bulk_insert_documents(self._database_client, job_docs, 'jobs')
        bulk_insert_documents(self._database_client, job_link_docs, 'job_link')
def _prepare_locations():

    documents = []

    with open('python_api/assets/provinces_eng.json', encoding='utf-8') as f:
        location = json.load(f)

    location['Hanoi'] = location['Hanoi City']
    location.pop('Hanoi City')

    result = []

    for key in location.keys():
        if key != 'Ho Chi Minh City':
            if 'province' in key or 'Province' in key or 'City' in key or 'city' in key:
                key = ' '.join(key.split(' ')[:-1])
        result.append(key)
    new_location = dict(zip(result, location.values()))

    for key in new_location.keys():
        province_id = list(new_location[key].keys())[0]
        
        for item in new_location[key][province_id]:
            document = dict()
            document['provinceID'] = int(province_id)
            document['provinceName'] = key
            document['districtID'] = item['District code']
            document['districtName'] = item['District']

            documents.append(document)

    return documents
def _prepare_sectors():
    id = 0
    documents = []
    with open('python_api/assets/sectors.json') as f:
        sectors = json.load(f)['sectors']

    for sector in sectors:
        document = dict()
        document['sectorID'] = id
        document['name'] = sector['name']
        document['weights'] = dict()
        document['weights']["experienceWeight"] = sector['weights']['Experience']
        document['weights']["degreeWeight"] = sector['weights']['Degree']
        document['weights']["softWeight"] = sector['weights']['Soft Skills']
        document['weights']["technicalWeight"] = sector['weights']['Technical Skills']
        documents.append(document)
        id += 1
    
    return documents

def get_sector_weights(es: Elasticsearch):
    '''
    Method for getting the weights of the sectors from the database

    Parameters:
    - es: Elasticsearch - An instance of the Elasticsearch class
    '''
    weights = []

    s = Search(using=es, index='sector').extra(size=20).execute()

    for hit in s:
        weights.append(hit.to_dict())
    
    return weights