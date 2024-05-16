import logging
from multiprocessing import Queue, Lock, Process
import contextlib
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(BASE_DIR)
abc = Lock()


class DeadReckoningLogHandler(logging.FileHandler):
    """reentrant preventing lock.
    Not sure if default lock does similar but this works in testing.
    """
    def __init__(self, filename, *args, **kwargs):
        self.lock = kwargs['lock']
        del kwargs['lock']
        super().__init__(filename, mode='a', *args, **kwargs)


LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {'name_one': {'format': '%(process)s %(thread)s:%(asctime)s - - %(message)s'},
                       'name_two': {'format': '>> %(process)s %(thread)s:%(asctime)s ---- %(message)s'}},
        'handlers': {
            'fileserver': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': '/home/edna/bow/chatshredder/backup/normal.log',
                'formatter': 'name_two',
            },
            'locked_file':{
                'level': 'DEBUG',
                'class': 'dict_conf_logging_multiprocessing.DeadReckoningLogHandler',
                'filename': BASE_DIR + '/custom.log',
                'lock': 'dict_conf_logging_multiprocessing.abc',
                'formatter': 'name_two'
            }
        },
        'loggers': {
            'network': {
                'handlers': ['fileserver'],
                'level': 'DEBUG',
            },
            'locked_multiprocessing': {
                'handlers': ['locked_file'],
                'level': 'DEBUG',
            },
            'root': {
                    "handlers": ["fileserver"],
                    "level": "DEBUG",
            }
        },
}

from logging import config
config.dictConfig(LOGGING)
LOGGER = logging.getLogger('locked_multiprocessing')
from time import sleep
from threading import Thread, active_count


def log_some_more(*args, **kwargs):
    """this functions runs in daemon thread.
        It logs from the same LOGGER object as main program
    """
    number_id = kwargs['i']
    LOGGER.debug(number_id)
    for i in range(0,3):
        x = '       log_some_more Thread number {number_id}'.format(number_id=number_id)
        LOGGER.debug(x)
        LOGGER.debug('      log_some_more counter: ' + str(i))
        LOGGER.debug('      log_some_more  ' + str(abc))
        if abc.acquire(timeout=2):
            LOGGER.debug('      log_some_more: lock acquired and timeout done.')
            abc.release()
        else:
            LOGGER.debug('      log_some_more: timeout done lock NOT acquired.') #  should never execute.


def continuous(lockie, any_name, pipo):
    """keep logging messages"""
    i = 0
    ert = []
    while True:
        i += 1
        LOGGER.debug('---' + str(any_name) + '--MAIN '+ str(i) + '------')
        LOGGER.debug(str(i) + ' from ' + str(any_name))
        LOGGER.debug(abc)
        LOGGER.error(str(i) + ' from  ' + str(any_name) + ' err')
        if i>3:
            kwargs = {'i':i}
            thread = Thread(
                target=log_some_more,
                kwargs=kwargs,
                daemon=True
            )
            thread.start()
            ert.append(thread)
            count = (active_count() - 1)
            LOGGER.debug('in continuous :  ' + str(count))
            LOGGER.debug(abc)
            with lockie:
                pipo.put(i)
                if not pipo.empty():
                    tghy = str(pipo.get())
                    LOGGER.debug('pipo: ' + tghy)
        if i>6:
            break
    for z in ert:
        z.join()
        count = (active_count() - 1)
        LOGGER.debug('closing in continuos :' + str(count))
        LOGGER.debug(abc)
import os
import sys
import inspect


def stack_inspect_j():
    print ('Module/Function : ' + os.path.basename(__file__) + ' ' + sys._getframe().f_code.co_name +'()')
    print ('Called from     : ' + os.path.basename(inspect.stack()[1][1]) + ' ' + inspect.stack()[1][3] + '()' )


# test if locks work with pipes in different proc and diff threads
if __name__ == '__main__':
    print(abc)
    LOGGER.debug('unlocked: ')
    if abc.acquire():
        LOGGER.debug('This should not execute. Although lock is acquired, loggerHandler is equipped with the same lock')
    LOGGER.debug('Lock not acquired.  Unlocked.')
    bf = Queue()
    printer = Process(target=continuous, name='Dunder', args=(abc, 'PROCESS ONE', bf))
    printer_two = Process(target=continuous, name='Mifflin', args=(abc, 'PROCESS TWO', bf))

    printer.start()
    printer_two.start()

    print('started')

    printer.join()
    print('joined')
    printer_two.join()

    print('stack inspection: ')
    stack_inspect_j()





