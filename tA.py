from Decorators.log import logging_setup,SYS_LOGS,logging

MY_LOGGING = {
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

logging_setup(MY_LOGGING)

@SYS_LOGS
class A():
    def __init__(self, *args, **kwargs):
    
        pass

    def out(self,*args):
        logging.info("A out.")

aa= A()
aa.out((1,2,3))
