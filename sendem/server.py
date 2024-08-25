#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import socket
import time
from logging import config
from multiprocessing import Lock
from threading import Thread, active_count, enumerate

from appliance import Appliance
from messageunitsendem import MessageUnit

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


class Server(Appliance):

    def __init__(self, data, q_in=None, q_out=None):
        """
        Construct server object.
        :param data: dict of possible parameters, like example below.
                {'--help': False,
         '--now': False,
         '--time': False,
         '--version': False,
         '-h': False,
         '<ip>': '127.0.0.1',
         '<message>': None,
         '<port>': '7788',
         'Options:': False,
         'Show': 0,
         'Testing': False,
         'client': False,
         'conf': False,
         'docopt': False,
         'help': False,
         'in': False,
         'local': False,
         'output': False,
         'reset': False,
         'run': True,
         'send': False,
         'server': True,
         'text': False,
         'this': False,
         'time': False,
         'version': False}
        """
        super().__init__()
        # from logging import config
        config.dictConfig(LOGGING)
        self.SERVER_LOGGER = logging.getLogger('sendem_server')
        self.__client_list__ = []
        self.__options__ = []
        self.__xflags__ = []
        self.SERVER_LOGGER.debug('---------------------------------')
        self.SERVER_LOGGER.debug(data)
        if data['Options:']:
            # doesn't work with docopt since option tag not mark in dict reliable?
            for n in data:
                if n.startswith('--'):
                    # self.SERVER_LOGGER.debug(n)
                    # self.SERVER_LOGGER.debug(self.__options__)
                    self.__options__ = self.__options__.append(n)
            self.index = len(data)
        if ('--time' in data) and (data['--time']):
            # self.SERVER_LOGGER.debug("---TIME FLAG---")
            self.__xflags__.append('time')
        if ('--now' in data) and (data['--now']):
            # self.SERVER_LOGGER.debug("---NOW FLAG---")
            self.__xflags__.append('now')
        if '<port>' in data and not data['<port>'] is None:
            self.SERVER_LOGGER.debug("not data['<port>'] is None")
            self.__PORT__ = int(data['<port>'])
        else:
            self.__PORT__ = 7788
        if '<ip>' in data and data['<ip>'] is not None:
            self.__SERVER__ = data['<ip>']
        else:
            self.__SERVER__ = '127.0.0.1'
        self.__HOSTNAME__ = socket.gethostname()
        self.__ADDR__ = (self.__SERVER__, self.__PORT__)
        self.__RUN__ = True
        self.__inet_shredder_server_socket__ = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        self.__inet_shredder_server_socket__.setblocking(True)
        self.__inet_shredder_server_socket__.bind(self.__ADDR__)
        # self.__inet_shredder_server_socket__.settimeout(5500)
        self.SERVER_LOGGER.debug(
            'Finished setup. Server with options {r}  and flags {f}'.format(r=self.__options__, f=self.__xflags__)
        )
        self.mu_list = []
        self.connected = False
        self.q_in = q_in
        self.q_out = q_out

    def mu_count(self):
        return self.mu_list.count()

    def get_mu_list(self):
        return self.mu_list

    def receiver_of_handle(self, conn, addr):
        """
        Returns None if there is nothing received.
        """
        try:
            msg = conn.recv(self.__HEADER__).decode(self.__FORMAT__).strip()
        except socket.error:
            self.SERVER_LOGGER.debug("socket error.  tried to read. all OK.")
            errmsg = str(socket.error)
            self.SERVER_LOGGER.debug(errmsg)
            return None

        if msg is None:
            time.sleep(0.1)
            return None
        else:
            msg = str(msg).strip()
            self.SERVER_LOGGER.debug(type(msg))
            self.SERVER_LOGGER.debug('received:                     ' + msg)
            msg_length = int(len(msg))
            if msg_length > 0:
                self.SERVER_LOGGER.debug(" non zero payload ")
                if msg == self.__DISCONNECT__:
                    self.SERVER_LOGGER.debug(" controlled disconnect ")
                    self.__RUN__ = True  # Keep running server but bike this connection.
                    self.connected = False
                    conn.shutdown(socket.SHUT_RDWR)
                elif msg == self.__SHUTDOWN__:
                    self.SERVER_LOGGER.debug('shutdown')
                    self.__RUN__ = False
                    self.connected = False
                    # close listening sockets
                    conn.shutdown(socket.SHUT_RDWR)
                    conn.close()
                    if conn is not None:
                        conn.shutdown(socket.SHUT_RDWR)
                        del conn

                else:
                    log_msg = "{addr} -- {mseg}".format(addr=addr, mseg=msg)
                    self.SERVER_LOGGER.debug(log_msg)

            return msg

    def handle_client(self, *handle_args):
        """
        Short-lived conn manager.
        Receive and send based on MessageUnit objects.
        """
        conn, addr = handle_args
        messagej = "new conn ... {addr}, {conn}".format(addr=addr, conn=conn)
        self.SERVER_LOGGER.debug(messagej)
        self.connected = True
        msg = None
        while self.connected:  # only executes if nothing closed socket
            msg = self.receiver_of_handle(conn, addr)
            if msg:
                mu = MessageUnit(msg)
                self.mu_list.append(mu)
                if self.q_in and self.q_in.qsize() > 0:
                    x = self.q_in.get()
                    if x == '!TERMINATE':
                        self.SERVER_LOGGER.debug('received terminate')
                        self.connected = False
                        self.__RUN__ = False
                if self.q_out and self.q_out.qsize() == 0:
                    self.q_out.put(msg)
                    ## !!!
                if self.authenticated_incoming(msg):
                        self.send_now(conn, msg='debug--ACK')
            msg = None

    def start(self):
        """create a new connection for every incoming request.
            Create a new thread for each connection to live in and setup callbacks.
        """
        self.SERVER_LOGGER.debug(' start server function ')
        try:
            self.__inet_shredder_server_socket__.listen()
        except OSError:
            self.SERVER_LOGGER.debug(OSError)
        conn = None
        addr = None
        while self.__RUN__:
            try:
                conn, addr = self.__inet_shredder_server_socket__.accept()
            except OSError as se:
                self.SERVER_LOGGER.debug(se)

            thread = Thread(target=self.handle_client, args=(conn, addr))
            try:
                thread.start()
            except OSError:
                self.SERVER_LOGGER.debug('Start Thread issue.')
                self.SERVER_LOGGER.debug(OSError)

            count = (active_count() - 1)
            self.SERVER_LOGGER.debug("ACTIVE CONNECTS {cnt:d}".format(cnt=count))
        self.connected = False
        self.SERVER_LOGGER.debug(' exit ')
        self.__inet_shredder_server_socket__.shutdown(socket.SHUT_RDWR)
        # maybe receive until close??
        self.__inet_shredder_server_socket__.close()
        x = enumerate()
        for i in x:
            try:
                self.__inet_shredder_server_socket__.shutdown(socket.SHUT_RDWR)
                self.__inet_shredder_server_socket__.close()
            except OSError:
                self.SERVER_LOGGER.info('socket already down. Skipping to next.')
            i.join()
            self.SERVER_LOGGER.debug('server-thread joined.')
            del i
            self.SERVER_LOGGER.debug('deleted ')

    def authenticated_incoming(self, data_message: str):
        """check if mu origin is authenticated and is authentic."""
        # check db or cache
        self.SERVER_LOGGER.debug('checking if mu origin is authenticated')
        return True

    def send_now(self, conn, msg: str):
        """
        visible message ACK-like message for debugging only
        """
        try:
            sendbytes = msg.encode(self.__FORMAT__)
            conn.sendall(sendbytes)
        except socket.error:
            self.SERVER_LOGGER.debug("socket error.  tried to send.")
            errmsg: str = str(socket.error)
            self.SERVER_LOGGER.debug(errmsg)