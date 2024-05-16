#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Usage:
    zsendem.py
    zsendem.py [options]
    zsendem.py [--time] [--now] server run <ip> <port>
    zsendem.py client <ip> <port>
    zsendem.py [options] send <message>
    zsendem.py [options] reset
Options:
  --time  Show local time in output
  -h  --help  Show this help text
  --version  Show version
  --now  Testing docopt conf
"""


# @TODO: Prototype pattern creates server instances.
# https://medium.com/@liams_o/gang-of-four-fundamental-design-patterns-41a85a562954
# @TODO: Builder pattern creates client


import multiprocessing
from server import Server
from docopt import docopt, DocoptExit
import os
from PyQt6 import QtWidgets
from multiprocessing import Lock
import contextlib
import sys
from client_of_sendem import Client, ClientWidget
import logging
from logging import config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
abc = Lock()
xyz = Lock()
server_log_lock = Lock()
network_log_lock = Lock()

LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {'name_one': {'format': '%(process)s %(thread)s:%(asctime)s - - %(message)s'},
                       'name_two': {'format': '>>%(process)s %(thread)s: %(asctime)s ---- %(message)s'}},
        'handlers': {
            'r_file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': '/var/log/coaster/main.log',
                'formatter': 'name_one',
            },
            'central_file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': '/var/log/coaster/debug.log',
                'formatter': 'name_one',
            },
            'server_custom_file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': '/var/log/coaster/server_custom_debug.log',
                'formatter': 'name_two',
            },
        },
        'loggers': {
            'central': {
                'handlers': ['central_file'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'sendem_server': {
                'handlers': ['server_custom_file'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'root': {
                'handlers': ['r_file'],
                'propagate': False,
                'level': 'DEBUG',
                },
        },
}

PID_FILE = 'sendemissmokin'
PID_FILE_CLIENT = PID_FILE + 'client'
PID_FILE_WIDGET = PID_FILE + 'widget'
PID_FILE_WIDGET_FORK = PID_FILE + 'widgetfork'
PID_FILE_NETWORK_CLIENT = PID_FILE + 'networkclientfork'
LOG_DIR = os.path.join(BASE_DIR, '../logs')
config.dictConfig(LOGGING)
LOGGER = logging.getLogger('central')


class StandardStreamLogger:

    def __init__(self, name='central', jlevel='DEBUG'):
        self.stream_logger = logging.getLogger(name)
        self.name = self.stream_logger.name
        self.level = getattr(self.stream_logger, 'level')
        if jlevel == 'ERROR':
            self._redirector = contextlib.redirect_stderr(self.stream_logger)

        elif jlevel == 'INFO' or jlevel == 'DEBUG':
            self._redirector = contextlib.redirect_stdout(self.stream_logger)

    def get_obj_logger(self):
        return self.stream_logger

    def write(self, data):
        self.stream_logger.log(self.level, data)

    def flush(self):
        pass

    def __enter__(self):
        self._redirector.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._redirector.__exit__(exc_type, exc_value, traceback)


def setup_streams(name):
    sendem_stdout = StandardStreamLogger(name=name, jlevel='INFO')
    sendem_stderr = StandardStreamLogger(name=name, jlevel='ERROR')

    sys.stdout = sendem_stdout
    sys.stderr = sendem_stderr


def command_parser(xgrey_args):
    """
    Build class according to commands and options.
    @:param xrgs: parsed dict representing user input.
    """
    # LOGGER.debug('parsing..')
    if xgrey_args['client']:
        c = Client
        command = (c, xgrey_args)
    elif xgrey_args['server']:
        c = Server
        command = (c, xgrey_args)
        # LOGGER.debug(command)
    else:
        # LOGGER.debug('no commands')
        return None, xgrey_args
    return command


def d_start_server(*smokin_server, q_in=None, q_out=None):
    """Instantiates and start object from parameters."""
    smoke, parsed_args = smokin_server
    smokey = smoke(data=parsed_args, q_in=q_in, q_out=q_out)
    setup_streams('central')
    print('d_start_server just  forked again')
    print("pid: " + str(os.getpid()))
    print("sid: " + str(os.getsid(os.getpid())))
    print("gid: " + str(os.getgid()))
    smokey.start()


def daemonize_server(*app_details):
    """Creates a new environment by running a new process for running the app."""
    if os.fork() != 0:
        return
    print("pid: " + str(os.getpid()))
    print("sid: " + str(os.getsid(os.getpid())))
    print("gid: " + str(os.getgid()))
    os.setsid()
    print("after os.setsid ... sid: " + str(os.getsid(os.getpid())))
    print("after os.setsid ... still same pid ?  " + str(os.getpid()))
    print("after os.setsid .. .gid: " + str(os.getgid()))
    setup_streams('central')
    mothership = multiprocessing.get_context('fork')
    server_proc = mothership.Process(
        target=d_start_server,
        name='ServerApp',
        args=app_details,
        daemon=True)
    server_proc.start()
    server_proc.join()


def jdaemonize_widget(wgui_queue, w_lock, smokin_client):
    if os.fork() != 0:
        return
    os.setsid()
    setup_streams('central')
    print('daemonize_widget')
    print("__name__:" + __name__)
    print("wd: " + str(os.getcwd()))
    print("pid: " + str(os.getpid()))
    print("gid: " + str(os.getgid()))
    print("sid: " + str(os.getsid(os.getpid())))
    ospid = '+fork 1.1 daemonize client os pid: ' + str(os.getpid())
    print(ospid)
    app = QtWidgets.QApplication([])
    widget = ClientWidget(wgui_queue, w_lock)
    widget.resize(400, 300)
    widget.show()
    print('COMPLETED: daemonize_widget')
    sys.exit(app.exec())
    # tear_down_streams()


def daemonize_network_client(client_queue, ellie_di_lock, smokin_client):
    if os.fork() != 0:
        return
    os.setsid()
    setup_streams('central')
    print('daemonize_network_client.  blowing smoke : ')
    print(str(smokin_client))
    print("__name__:" + __name__)
    print("wd: " + str(os.getcwd()))
    print("pid: " + str(os.getpid()))
    print("gid: " + str(os.getgid()))
    print("sid: " + str(os.getsid(os.getpid())))
    smoke, parsed_args = smokin_client
    smokey_client = smoke(data=parsed_args, queuey=client_queue, lck=ellie_di_lock)
    smokey_client.start()
    ospid = '+fork 1.2 daemonize client os pid: ' + str(os.getpid())
    print(ospid)
    print('COMPLETED: daemonize_network_client')


def run_daemon_job_start_client(smokin_client):
    """Takes the object starts and runs basic process operations in daemon mode
        Starts another separate process for widget.
    """
    mothership = multiprocessing.get_context('fork')
    client_queue = mothership.Queue(maxsize=500)
    # strings_stashed_buffer = multiprocessing.Array('u', 128, lock=True)
    ellie_di_lock = mothership.Lock()
    ospid = '1 daemonize client os pid: ' + str(os.getpid())
    LOGGER.debug(ospid)
    widg_proc = mothership.Process(
        target=jdaemonize_widget,
        name='SendemWidget',
        args=(client_queue, ellie_di_lock, smokin_client), daemon=True)
    network_client_proc = mothership.Process(
        target=daemonize_network_client,
        name='SendemNetworkClient',
        args=(client_queue, ellie_di_lock, smokin_client), daemon=True)
    widg_proc.start()
    network_client_proc.start()

    widg_proc.join()
    network_client_proc.join()


def daemonize_client(app_details):
    """Runs app_details as distinct process in specified environment."""
    ospid = 'daemonize client os pid: ' + str(os.getpid())
    LOGGER.debug(ospid)
    run_daemon_job_start_client(app_details)
    LOGGER.debug('COMPLETED: daemonize_client')


if __name__ == "__main__":
    print("__name__:" + __name__)
    print("wd: " + str(os.getcwd()))
    print("pid: " + str(os.getpid()))
    print("sid: " + str(os.getsid(os.getpid())))
    arguments = None
    try:
        arguments = docopt(__doc__, options_first=True, version='0.1', help=True)
    except DocoptExit as err:
        print(err)

    LOGGER = logging.getLogger('central')
    if arguments is not None:
        #  LOGGER.debug(arguments)
        selected = command_parser(arguments)
        app_types, r_args = selected
        #  LOGGER.debug(app_types)
        #  LOGGER.debug(r_args)
        if app_types == Client:
            LOGGER.debug('setup client...')
            daemonize_client((app_types, r_args))
            LOGGER.debug('main process.  this should execute')
        elif app_types == Server:
            LOGGER.debug('server... r_args:')
            LOGGER.debug(r_args)
            daemonize_server(app_types, r_args)
        else:

            LOGGER.debug("Undetected command")
