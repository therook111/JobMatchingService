from datetime import datetime as dt
from dateutil import parser
import math
import numpy as np
import torch 
from transformers import AutoTokenizer, AutoModel
import pandas as pd
import torch.nn.functional as F
import os 
import json 
import ast
from elasticsearch_dsl import Q
from elasticsearch import Elasticsearch, helpers
from typing import List, Dict, Any
from datetime import datetime as dt
from fastapi import UploadFile, File
import shutil


from utils.logging import database_logger
from utils.text_reader import TextExtractor


with open('python_api/assets/sector_lookup.json', 'r') as f:
    lookup_table_sectors = json.load(f)

def process_cv(CV: UploadFile = File(...), destination='temp.pdf'):
    '''
    Utility function for processing a CV, assuming PDF file.
    '''
    if CV.content_type != "application/pdf":
        raise Exception("PDF file only.")
    else:
        try:
            with open(destination, "wb") as buffer:
                shutil.copyfileobj(CV.file, buffer)

            content = TextExtractor(destination).extract_file()
                
            os.remove(destination)
            return content
        except Exception as e:
            print(f'{e} Error processing CV.')
            return 

def make_clickable(url):
    """
    Creates an HTML link that will render as clickable
    Parameters:
    url (str): The URL to convert into a clickable link
    
    Returns:
    str: HTML formatted string with an anchor tag
    """
    if url:
        return f'<a href="{url}" target="_blank">{url}</a>'
    else:
        return ""
def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm_a = np.linalg.norm(vec1)
    norm_b = np.linalg.norm(vec2)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)

def convert_to_iso(date_str: str, utc=True):
    if utc:
        return parser.parse(date_str).isoformat() + 'Z'
    else:
        return parser.parse(date_str).isoformat()


def check_for_nan(document):
    for field in document:
        try:
            if math.isnan(document[field]):
                document[field] = None
        except:
            continue

    return document

def handle_null_embedding(document):
    for field in ['Candidate_Experience_Requirements_embedding',
                  'Candidate_soft_skill_Requirements_embedding',  
                  'Candidate_technical_skill_Requirements_embedding', 
                  'Candidate_degree_Requirements_embedding']:
        try:
            document[field] = ast.literal_eval(document[field])
            if type(document[field]) != list:
                document[field] = [1e-7 for _ in range(768)]
            else:
                document[field] = document[field][0]
        except:
            document[field] = [1e-7 for _ in range(768)]

    return document

def handle_embedding_cv(document):
    for field in document['job information']:
        document['job information'][field] = document['job information'][field][0]
    return document


def last_token_pool(last_hidden_states: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])  
    if left_padding:
        return last_hidden_states[:, -1]
    else:
        sequence_lengths = attention_mask.sum(dim=1) - 1
        batch_size = last_hidden_states.shape[0]
        return last_hidden_states[torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths]

def embed_text(text):
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    tokenizer = AutoTokenizer.from_pretrained("BAAI/llm-embedder")
    model_embed = AutoModel.from_pretrained("BAAI/llm-embedder")
    model_embed.eval()
    if text == '':
        return [1e-7 for _ in range(768)]
    inputs = tokenizer(str(text), return_tensors='pt', truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        out = model_embed(**inputs)
        embeddings = last_token_pool(out.last_hidden_state, inputs['attention_mask'])
    embeddings = F.normalize(embeddings, p=2, dim=1)
    return embeddings.tolist()

def result_to_html(df: pd.DataFrame, cv_id: str):

    df['Link'] = df['Link'].apply(make_clickable)

    recommendation_html = df.to_html(classes=[
        'dataframe' 
    ], escape=False)

    final_table = f"""
        <input type="hidden" id="cv_id" value="{cv_id}">
        {recommendation_html}
    """
    return final_table

def validate_start_end_date(start_date, end_date):
    if start_date and end_date:
        start_date = convert_to_iso(start_date)
        end_date = convert_to_iso(end_date)
        return start_date, end_date
    
    elif start_date and not end_date:
        start_date = convert_to_iso(start_date)
        deadline = (dt.fromisoformat(start_date) + pd.Timedelta('30 days')).replace(tzinfo=None).isoformat() + 'Z'
        return start_date, deadline
    
    return start_date, end_date

def clean_nan_values(obj):
    if isinstance(obj, float) and math.isnan(obj):
        return None
    elif isinstance(obj, dict):
        return {k: clean_nan_values(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan_values(v) for v in obj]
    return obj
    
    
def validate_salary(min_salary, max_salary):
    try:
        min_salary = int(min_salary)
    except:
        min_salary = None
    
    try:
        max_salary = int(max_salary)
    except:
        max_salary = None

    return min_salary, max_salary
    
    
def parse_query(query_params: dict):
    '''
    Utility function that converts a dictionary of query into Elasticsearch-DSL query for filtering.
    '''

    if not query_params:
        raise ValueError("Query dictionary is empty. Please check the query dictionary.")
    
    # Check whether the dictionary query has unexpected keywords outside allowed ones
    for key in query_params:
        if key not in ['province', 'cv_id', 'district', 'salary', 'filter_salary_mode', "salary_min", "salary_max"]:
            raise ValueError(f"Unexpected keyword '{key}' found in query dictionary. Please check again.")
        
    must_conditions = [] # [Q('range', deadline={'gte': dt.now().isoformat(timespec='seconds') + 'Z'})]
                        # Deadline must be later than the query time.


    if query_params.get('province'):
        province_id = query_params['province']
        
        with open('python_api/assets/province_lookup.json') as f:
            table = json.load(f)
        try:
            province = table[province_id]
            must_conditions.append(Q('match', location_primary=f"*{province}*"))
        except ValueError:
            raise ValueError(f"Unexpected province ID '{province_id}' found in query dictionary")
        
    if query_params.get('district'):
        district_id = query_params['district']

        with open('python_api/assets/district_lookup.json') as f:
            table = json.load(f)
        try:
            district = table[district_id]
            must_conditions.append(Q('match', location_secondary=f"*{district}*"))
        except ValueError:
            raise ValueError(f"Unexpected district ID '{district_id}' found in query dictionary")
        
    salary_mode = query_params.get('filter_salary_mode')
    if salary_mode:
        if salary_mode == 'min':
            should_conditions = [
                Q('range', salary_min={'gte': query_params['salary']}),
                Q('range', salary_max={'gte': query_params['salary']})
            ]
            must_conditions.append(Q('bool', should=should_conditions))
            
        elif salary_mode == 'max':
            should_conditions = [
                Q('range', salary_max={'lte': query_params['salary']}),
                Q('range', salary_min={'lte': query_params['salary']})
            ]
            must_conditions.append(Q('bool', should=should_conditions))
            
        elif salary_mode == 'range':
            salary_conditions = []
            
            if query_params.get('salary_min'):
                should_conditions = [
                    Q('range', salary_min={'gte': query_params['salary_min']}),
                    Q('range', salary_max={'gte': query_params['salary_min']})
                ]
                salary_conditions.append(Q('bool', should=should_conditions))
                
            if query_params.get('salary_max'):
                should_conditions = [
                    Q('range', salary_max={'lte': query_params['salary_max']}),
                    Q('range', salary_min={'lte': query_params['salary_max']})
                ]
                salary_conditions.append(Q('bool', should=should_conditions))
                
            if salary_conditions:
                must_conditions.append(Q('bool', must=salary_conditions))


    if must_conditions:
        return Q('bool', must=must_conditions)
    else:
        return None

def bulk_insert_documents(client: Elasticsearch,
    documents: List[Dict[Any, Any]],
    index_name: str,
    batch_size: int = 256, **kwargs
) -> tuple[int, List[Dict]]:
    """
    Bulk insert documents into Elasticsearch.
    
    Args:
        client: Elasticsearch client instance
        documents: List of documents to insert
        index_name: Name of the index to insert into
        batch_size: Number of documents per batch
        
    Returns:
        tuple containing:
            - Number of successfully inserted documents
            - List of failed documents
    """

    actions = [{"_index": index_name, "_source": document} for document in documents]
    
    request_id = kwargs.get('request_id', 'N/A')

    extra = {'service': 'database_bulk_insert', 'request_id': request_id}
    success_count = 0
    failed_documents = []
    
    try:
        for success, info in helpers.parallel_bulk(
            client,
            actions,
            chunk_size=batch_size,
            raise_on_error=False,
            raise_on_exception=False
        ):
            if success:
                success_count += 1
                if success_count % batch_size == 0:
                    database_logger.info(f"Successfully processed {success_count} documents", extra=extra)
            else:
                failed_documents.append(info)
                database_logger.error(f"Failed to insert document: {info}", extra=extra)
            
    except Exception as e:
        database_logger.error(f"Bulk insertion error: {str(e)}", exc_info=True, extra=extra)
        raise
    
    finally:
        database_logger.info("Finished bulk indexing all valid jobs in the database.", extra=extra)
        
    return success_count, failed_documents    
            
def parse_API_response_for_CV(response):
    try:
        choices = response.choices
        if not choices:
            return None

        first_choice = choices[0]
        if not hasattr(first_choice, 'message'):
            return None 
        
        message = first_choice.message
        if not hasattr(message, 'tool_calls') and not hasattr(message, 'toolCalls'):
            return None 
        
        call = message.tool_calls[0] if hasattr(message, 'tool_calls') else message.toolCalls[0]
        try:
            args = json.loads(call.function.arguments)
        except:
            args = json.loads(call['function']['arguments'])

        return {
                'degree': args.get('degree', ''),
                'technical_skill': args.get('technical_skill', ''),
                'soft_skill': args.get('soft_skill', ''),
                'experience': args.get('experience', '')
            }
        
    except (json.JSONDecodeError, AttributeError, IndexError) as e:
        print(f"Error parsing response: {e}")
        return None\
        
