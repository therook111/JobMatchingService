from fastapi import Depends
from elasticsearch import Elasticsearch
from utils.cache import CVCache
from search_engine.service import PersonalizedEngine
import os
import dotenv

dotenv.load_dotenv("python_api/sub.env")
password = os.getenv("ELASTIC_PASSWORD")
GEMINI_API = os.getenv("GOOGLE_GEMINI_API")
ROOT_DIR = os.getenv("ROOT_DIR")
# Initialize core services
es = Elasticsearch(
    hosts=[{"host": "localhost", "port": 9200, "scheme": "http"}], 
    basic_auth=("elastic", password)
)
cache = CVCache(expiration=10)
engine = PersonalizedEngine(es=es, cache=cache, GEMINI_API_KEY=GEMINI_API)

# Dependency provider
def inject_engine():
    return engine