from fastapi import Depends
from elasticsearch import Elasticsearch
from utils.cache import CVCache
from search_engine.service import PersonalizedEngine
import os
import dotenv
from utils.misc import BASE_DIR 


dotenv.load_dotenv(f"{BASE_DIR}/sub.env")
password = os.getenv("ELASTIC_PASSWORD")
GEMINI_API = os.getenv("GOOGLE_GEMINI_API")
ELASTIC_HOST = os.getenv("ELASTICSEARCH_HOST")
ELASTIC_SCHEME = os.getenv("ELASTICSEARCH_SCHEME")
CA_CERT = os.getenv('ELASTICSEARCH_CERTIFICATE_PATH')

# Initialize core services
es = Elasticsearch(
    hosts=[{"host": ELASTIC_HOST, "port": 9200, "scheme": ELASTIC_SCHEME}], 
    basic_auth=("elastic", password),
    ca_certs=CA_CERT
)
cache = CVCache(expiration=10)
engine = PersonalizedEngine(es=es, cache=cache, GEMINI_API_KEY=GEMINI_API)

# Dependency provider
def inject_engine():
    return engine