import logging
from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime as dt
import os
import logging.handlers

class BaseLogger(ABC):
    @abstractmethod
    def setup(self, service_name: str) -> logging.Logger:
        pass  
    @abstractmethod
    def _log(self, level: int, message: str, extra: Dict[str, Any] = None):
        pass

    def info(self, message: str, extra: Dict[str, Any] = {}):
        self._log(logging.INFO, message, extra)

    def warning(self, message: str, extra: Dict[str, Any] = {}):
        self._log(logging.WARNING, message, extra)

    def error(self, message: str, extra: Dict[str, Any] = {}):
        self._log(logging.ERROR, message, extra)


class DatabaseLogger(BaseLogger):
    def __init__(self, service_name: str = 'database') -> None:
        self.logger = self.setup(service_name)
        self.name = service_name

    def setup(self, service_name: str) -> logging.Logger:
        if not os.path.exists('service_logs/database'):
            os.makedirs('service_logs/database')
        
        if not os.path.exists('service_logs/database/errors'):
            os.makedirs('service_logs/database/errors')
            
        logger = logging.getLogger(service_name)
        logger.setLevel(logging.INFO)

        if logger.handlers:
            return logger
        
        formatter = logging.Formatter(
            fmt='%(asctime)s %(levelname)-5s [%(service)s] [%(request_id)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        main_handler = logging.handlers.TimedRotatingFileHandler(
            filename='service_logs/database/database.log',
            when='midnight',
            interval=1,
            backupCount=30, 
            encoding='utf-8')

        main_handler.setFormatter(formatter)
        main_handler.setLevel(logging.INFO)
        logger.addHandler(main_handler)


        error_handler = logging.handlers.RotatingFileHandler(
            filename='service_logs/database/errors/database_errors.log',
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8')

        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        logger.addHandler(error_handler)

        return logger

    def _log(self, level: int, message: str, extra: Dict[str, Any] = None) -> None:
        if extra is None:
            extra = {}
        
        id = extra.get('request_id', 'N/A')
        extra.update({'service': self.name, 'request_id': id})
        self.logger.log(level, message, extra=extra)
        


class SystemLogger(BaseLogger):
    def __init__(self, service_name: str = 'system'):
        self.logger = self.setup(service_name)
        self.name = service_name

    def setup(self, service_name: str) -> logging.Logger:
        if not os.path.exists('service_logs/system'):
            os.makedirs('service_logs/system')
        
        if not os.path.exists('service_logs/system/errors'):
            os.makedirs('service_logs/system/errors')
            
        logger = logging.getLogger(service_name)
        logger.setLevel(logging.INFO)

        if logger.handlers:
            return logger
        
        formatter = logging.Formatter(
            fmt='%(asctime)s %(levelname)-5s [%(service)s] [%(request_id)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        main_handler = logging.handlers.TimedRotatingFileHandler(
            filename='service_logs/system/system.log',
            when='midnight',
            interval=1,
            backupCount=30, 
            encoding='utf-8')

        main_handler.setFormatter(formatter)
        main_handler.setLevel(logging.INFO)
        logger.addHandler(main_handler)


        error_handler = logging.handlers.RotatingFileHandler(
            filename='service_logs/system/errors/system_errors.log',
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8')

        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        logger.addHandler(error_handler)

        return logger

    def _log(self, level: int, message: str, extra: Dict[str, Any] = None):
        if extra is None:
            extra = {}
        
        id = extra.get('request_id', 'N/A')
        extra.update({'service': self.name, 'request_id': id})
        self.logger.log(level, message, extra=extra) 

database_logger = DatabaseLogger().setup('database')
system_logger = SystemLogger().setup('system')
    