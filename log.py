"""
logging handler
"""
import logging
import utils

LOGFILENAME = utils.get_config('log', 'LOG_FILE_NAME')


def get_logger():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=LOGFILENAME,
                        filemode='a')
    return logging
