from Decorators.log import logging_setup,SYS_LOGS,logging

DJANGO_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'info': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'log/Info.log',
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'log/Errors.log',
        },
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'warning':{
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'log/Warning.log',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console','info'],
            'level':'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['error'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['info'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}

logging_config={
    "version": 1,
    "formatters":{
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        "simple":{
            "format": '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        }
    },
    "handlers":{
        "console":{
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "verbose",
            "stream": "ext://sys.stdout"
        },
        "info_file_handler":{
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "verbose",
            "filename": "log/info.log",
            "maxBytes": 10485760,
            "backupCount": 3,
            "encoding": "utf8"
        },
        "error_file_handler":{
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "verbose",
            "filename": "log/error.log",
            "maxBytes": 10485760,
            "backupCount": 3,
            "encoding": "utf8"
        },
        'warning_file_handler':{
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            "formatter": "verbose",
            'filename': 'log/Warning.log',
            "maxBytes": 10485760,
            "backupCount": 3,
            "encoding": "utf8"
        }
    },
    "loggers":{

    },
    "root":{
        "level": "DEBUG",
        "handlers": ["console", "info_file_handler", "error_file_handler", "warning_file_handler"]
    }
}

logging_setup(logging_config)
'''
@SYS_LOGS
class A():
    def __init__(self, *args, **kwargs):
    
        pass

    def out(self,*args):
        logging.info("A out.")

aa= A()
aa.out((1,2,3))
'''