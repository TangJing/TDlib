import functools
import logging
import logging.config

logging.basicConfig(level= logging.INFO)

def logging_setup(config_json):
    logging.config.dictConfig(config= config_json)

def SYS_LOGS(func):
    def wapper(*args, **kwargs):
        try:
            ret= func(*args, **kwargs)
            return ret
        except Exception:
            logging.exception("System Faild.",exc_info= True)
    return wapper