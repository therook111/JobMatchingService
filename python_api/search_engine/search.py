
from elasticsearch_dsl import Search, Q

from utils.misc import cosine_similarity, bulk_insert_documents
from utils.logging import system_logger, database_logger
from search_engine.database import get_sector_weights
import pandas as pd 
import time

def create_tmp(es):
    try:
        es.indices.create(index='tempo', body={
            "mappings": {
                "properties": {
                    "JOB_ID": {"type": "keyword"},
                    "userID": {"type": "keyword"},
                    "score": {"type": "float"},
                    "location_primary": {"type": "text"},
                    "location_secondary": {"type": "text"},
                    "salary_min": {"type": "integer"},
                    "salary_max": {"type": "integer"},
                    "deadline": {"type": "date", "format": "yyyy-MM-dd'T'HH:mm:ss'Z'"},
                }
            }
        })
    except:
        pass
def delete_tmp(es):
    try:
        response = es.delete_by_query(
        index="tempo",
        body={"query": {"match_all": {}}}
) 
        print("Deleted %d documents" % response['deleted'])
    except:
        pass
def calculate_and_insert_similarities(es, user_document, top_k = 50, temp_index='tempo', index='jobs'):
    documents = []

    request_id = user_document[1]

    user_document = user_document[0]

    if es.count(index=temp_index)['count'] > 0:
        delete_tmp(es)

    # Get all weights of sectors
    sector_weights = get_sector_weights(es)

    query_vectors = {
        'experience_embedding': user_document['CV_information']['experience_embedding'],
        'soft_skill_embedding': user_document['CV_information']['soft_skill_embedding'],
        'technical_skill_embedding': user_document['CV_information']['technical_skill_embedding'],
        'degree_embedding': user_document['CV_information']['degree_embedding']
    }

    knn_queries = [
        {
            "field": f"job_information.{embedding}",
            "query_vector": query_vectors[f'{embedding}'],
            "k": top_k,
            "num_candidates": top_k * 3
        }
        for embedding in query_vectors.keys()
    ]
    
    body = {
        "knn": knn_queries,
        "size": top_k
    }


    result = es.search(index='jobs', body=body)

    for hit in result['hits']['hits']:
        doc = hit['_source']
        
        # Get similarity scores
        experience = cosine_similarity(query_vectors['experience_embedding'], doc['job_information']['experience_embedding'])
        soft_skill = cosine_similarity(query_vectors['soft_skill_embedding'], doc['job_information']['soft_skill_embedding'])
        technical_skill = cosine_similarity(query_vectors['technical_skill_embedding'], doc['job_information']['technical_skill_embedding'])
        degree = cosine_similarity(query_vectors['degree_embedding'], doc['job_information']['degree_embedding'])


        # Get weights
        sector_id = doc['sectorID']
        weights = [entry for entry in sector_weights if entry['sectorID'] == sector_id]

        if weights:
            weights = weights[0]['weights']
        else:
            weights = {
                'experienceWeight': 0.3,
                'softWeight': 0.3,
                'technicalWeight': 0.3,
                'degreeWeight': 0.1
            }

        # Final steps
        score = weights['experienceWeight'] * experience + weights['softWeight'] * soft_skill + weights['technicalWeight'] * technical_skill + weights['degreeWeight'] * degree

        document = { 
            'JOB_ID': doc['JOB_ID'], 
            'userID': user_document['userID'], 
            'score': score,
            'location_primary': doc['location_primary'],
            'location_secondary': doc['location_secondary'],
            'salary_min': doc['salary_min'],
            'salary_max': doc['salary_max'],
            'deadline': doc['deadline']
        }
        documents.append(document)
    
    bulk_insert_documents(es, documents, temp_index, batch_size=1024, request_id=request_id)

def retrieve_top_results(es, query = None, temp_index='tempo', top_k=50, index='jobs'):

    if not query:
        top_entries = Search(using=es, index=temp_index).sort('-score').extra(size=top_k).execute()
    else:
        top_entries = Search(using=es, index=temp_index).query(query).sort('-score').extra(size=top_k).execute()

    top_results = []

    for hit in top_entries:
        hit = hit.to_dict()
        
        job_id = hit['JOB_ID']
        score = hit['score']
        user_id = hit['userID']

        s = Search(using=es, index="jobs").query("match", JOB_ID=job_id).execute()
        link_s = Search(using=es, index="job_link").query("match", JOB_ID=job_id).execute()

        for hit in s:
            result = hit.to_dict()

        job_title = result['title']
        city = result['location_primary']
        district = result['location_secondary']
        deadline = result['deadline']
        working_time = result['workingTime']
        min_salary = result['salary_min']
        max_salary = result['salary_max']

        for hit in link_s:
            result = hit.to_dict()

        link = result['link']

        if isinstance(score, list):
            score = score[0]

        top_results.append({
                'job_id': job_id,
                'user_id': user_id,
                'score': score,
                'job_title': job_title,
                'link': link,
                'city': city,
                'district': district,
                'deadline': deadline,
                'working_time': working_time,
                'min_salary': min_salary,
                'max_salary': max_salary,
            })

    return top_results

def search(es, user_document, query=None, temp_index='tempo', index='jobs'):

    create_tmp(es)
    calculate_and_insert_similarities(es, user_document, temp_index=temp_index, index=index)
    time.sleep(1.5)
    result = retrieve_top_results(es, query, temp_index=temp_index, index=index)
    
    delete_tmp(es)
    return result
        
def full_pipeline_search(es, user_document, query=None, temp_index='tempo', index='jobs'):

    result = search(es, user_document, query, temp_index, index)

    df = pd.DataFrame(result)
    try:
        df = df[['job_title', 'link', 'city', 'district', 'deadline', 'working_time', 'min_salary', 'max_salary', 'score']]
        df.columns = ['Title', 'Link', 'City/Province', 'District', 'Deadline', 'Working Time', 'Minimum Salary', 'Maximum Salary', 'Score']

    except:
        df = pd.DataFrame(columns=['Title', 'Link', 'City/Province', 'District', 'Deadline', 'Working Time', 'Minimum Salary', 'Maximum Salary', 'Score'])

    if len(df) <= 20:
        return df 
    else:
        return df.head(20)
    # raise Exception("This is a bug for testing")
        
