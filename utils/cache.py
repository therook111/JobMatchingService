from threading import Lock 
from typing import Dict, List, Optional 
from datetime import datetime as dt
from datetime import timedelta
import uuid

class CVCache:
    def __init__(self, expiration: int=2):
        '''
        A class that caches the processed CV for filtering data.

        Args:
            - expiration: int: The number of minutes to keep the cache.
        '''
        self._cache: Dict[str, tuple] = {}
        self._lock = Lock()
        self._expiration = timedelta(minutes=expiration)

    def store(self, cv_data: dict, cv_id: uuid.UUID):
        '''
        Store the processed CV in the cache.

        Args:
            - key: UUID: The key to store the value under.
            - cv_data: The processed CV.
        '''
        with self._lock:
            self._cache[cv_id] = (cv_data, dt.now())

        return cv_id

    def get(self, cv_id: str) -> Optional[str]:
        with self._lock:
            if cv_id not in self._cache:
                return None

            # check if expired
            cv_data, timestamp = self._cache[cv_id]
            if dt.now() - timestamp < self._expiration:
                return cv_data
            else:
                del self._cache[cv_id]
                return None

    def clean(self):
        with self._lock:
            expired_caches = [cv_id for cv_id, (cv_data, timestamp) in self._cache.items() if dt.now() - timestamp > self._expiration]
            for id in expired_caches:
                del self._cache[id]
    
    def clear(self):
        with self._lock:
            self._cache.clear()