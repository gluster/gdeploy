import logging
import logging.config
import os
import datetime
import time

def logger(f, name=None):
    '''
    This is a decorator function to log method calls
    '''
    log_dir = os.path.expanduser('~/.gdeploy/logs/')
    log_file = os.path.expanduser('~/.gdeploy/logs/gdeploy.log')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    try:
       if logger.fhwr:
          pass
    except:
       logger.fhwr = open(log_file,"a")
    if name is None:
        name = f.func_name
    def wrapped(*args, **kwargs):
        now = str(datetime.datetime.now())
        logger.fhwr.write(now +' - gdeploy - INFO - Calling ' +name+" "+str(f))
        result = f(*args, **kwargs)
        return result
    wrapped.__doc__ = f.__doc__
    return wrapped


def log_event():
    '''
    This method helps in logging the messages
    '''
    log_dir = os.path.expanduser('~/.gdeploy/logs/')
    log_file = os.path.expanduser('~/.gdeploy/logs/gdeploy.log')
    rotate_log_file(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logger = logging.getLogger("gdeploy")
    logger.setLevel(logging.INFO)

    # create the logging file handler
    fh = logging.FileHandler(log_file)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # add handler to logger object
    logger.addHandler(fh)

    return logger


def rotate_log_file(log):
    created= creation_date(log)
    now = datetime.datetime.now().date()
    days = (created - now).days
    #If the log file is more than a month old, we rotate it.
    if days > 30:
        try:
            os.remove(log)
        except:
            pass

def creation_date(filename):
    t = os.path.getctime(filename)
    return datetime.datetime.fromtimestamp(t).date()
