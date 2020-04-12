import functools
import logging
import logging.config

logging.basicConfig(level= logging.INFO)

def logging_setup(config_json):
    logging.config.dictConfig(config= config_json)

def SYS_LOGS(func):
    def wapper(*args, **kwargs):
        try:
            logging.info("start...")
            ret= func(*args, **kwargs)
            logging.info("end...")
            return ret
        except Exception:
            logging.exception("System Faild.",exc_info= True)
    return wapper