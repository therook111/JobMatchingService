from search_engine.database import DatabaseManager
from utils.misc import result_to_html
from utils.cache import CVCache


from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from typing import List
from utils.logging import database_logger, system_logger
from search_engine.search import full_pipeline_search

class PersonalizedEngine:
    '''
    A class that implements an Elasticsearch job matching engine using cosine similarity.

    Arguments:
    - es: The ElasticSearch client. Clean one is fine. Run .setup to initialize.
    - cache: A cache of type `CVCache` used to efficiently store and retrieve the users' CV for filtering.

    '''
    def __init__(self, es: Elasticsearch | None = None, cache: CVCache | None = None, GEMINI_API_KEY: str = None):
        if es is None:
            raise Exception("Elasticsearch client is not provided.")
        else:
            self.__es = es
            self.cache = cache
            self.manager = DatabaseManager(GEMINI_API_KEY, self.__es)

    def _match_jobs(self, CV: str, query = None, push=True, store=True):

        document = self.manager.prepare_user_profile(CV, push=push)

        if store:
            self.cache.store(document, document[1])
            _logger_info = {'service': 'caching', 'request_id': document[1]}
            system_logger.info(f"Cached CV of ID {document[1]}.", extra=_logger_info)

        try:
            df = full_pipeline_search(self.__es, document, query=query, index='jobs')

            extra_info = {'service': 'recommend_jobs', 'request_id': document[1]}
            system_logger.info(f"Finished searching for jobs.", extra=extra_info)

            return result_to_html(df, document[1]), document[1]
        except Exception as e:
            _logger_info = {'service': 'job_matching', 'request_id': document[1]}
            system_logger.error(f"Error occurred while searching for jobs: {e}", exc_info=True, extra=_logger_info)
            return 


    def setup(self):
        extra_info = {'service': 'Elasticsearch', 'request_id': 'ADMIN_setup'}
        self.manager.setup(extra_info=extra_info)
                
    def GetBestJobs(self, CV: str, query = None, push=True, store=True):
        extra_info = {'service': 'Elasticsearch', 'request_id': 'recommend_jobs'}
        try:
            result = self._match_jobs(CV, query, push, store)
            return result
        except Exception as e:
            system_logger.error(f"Error occurred while recommending jobs: {e}", exc_info=True, extra=extra_info)
            return
    
    def GetFilteredJobs(self, cached_document, query: Q, push=False, store=False):
        extra_info = {'service': 'Elasticsearch', 'request_id': 'filter_jobs'}
        try:
            df = full_pipeline_search(self.__es, cached_document, query=query, index='jobs')
            return result_to_html(df, cached_document[1]), cached_document[1]
        except Exception as e:
            system_logger.error(f"Error occurred while filtering for jobs: {e}", exc_info=True, extra=extra_info)
            return

    def push_jobs(self, jobs_df):
        self.manager.push_jobs(jobs_df)

    def delete_index(self, index):
        extra_info = {'service': 'Elasticsearch', 'request_id': 'ADMIN_delete_index'}
        if self.__es.indices.exists(index=index):
            self.__es.indices.delete(index=index)
            database_logger.info(f"Index {index} deleted successfully.", extra=extra_info)
        else:
            database_logger.error(f"Index {index} does not exist.", extra=extra_info)
    

    
