#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
import datetime
import socket
from threading import Thread, Timer
from threading import Lock as t_lock
from sys import path
import os
import time
import uuid
from PyQt6 import QtCore, QtGui, QtWidgets
from multiprocessing import Lock
from messageunitsendem import MessageUnit
from appliance import Appliance
from contact_item import ContactItem
import logging
from logging import config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
widget_log_lock = Lock()
network_log_lock = Lock()
runnable_logs_lock = Lock()

namespace_from_dir = os.environ['PWD'].split(r"/")[-1]

LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {'name_one': {'format': '%(process)s %(thread)s:%(asctime)s - - %(message)s'},
                       'name_two': {'format': '>>%(process)s %(thread)s: %(asctime)s ---- %(message)s'}},
        'handlers': {
            'network': {
                'level': 'DEBUG',
                'class': 'custom_logging.DeadReckoningLogHandler',
                'filename': '/var/log/coaster/network_client_custom_debug.log',
                'lock': '.network_log_lock',
                'formatter': 'name_one',
            },
            'widget': {
                'level': 'DEBUG',
                'class': 'custom_logging.DeadReckoningLogHandler',
                'filename': '/var/log/coaster/widget_custom_debug.log',
                'lock': '.widget_log_lock',
                'formatter': 'name_one',
            },
            'runnable': {
                'level': 'DEBUG',
                'class': 'custom_logging.DeadReckoningLogHandler',
                'filename': '/var/log/coaster/q_runnable_debug.log',
                'formatter': 'name_two',
                'lock': '.runnable_logs_lock',
            },
        },
        'loggers': {
            'central.sendem_widget': {
                'handlers': ['widget'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'central.sendem_network_client': {
                'handlers': ['network'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'central.sendem_qt_runnable_class':{
                'handlers': ['runnable'],
                'level': 'DEBUG',
                'propagate': True,
            }
        },
}


cp1 = QtGui.QColor.fromRgba64(40, 90, 85, 1)
cp2 = QtGui.QColor.fromRgba64(112, 149, 145, 1)
cp3 = QtGui.QColor.fromRgba64(108, 143, 139, 1)
cp4 = QtGui.QColor.fromRgba64(0, 43, 39, 1)
cp5 = QtGui.QColor.fromRgba64(2, 42, 38, 1)

gradient = QtGui.QRadialGradient(20, 20, 20, 20, 20)
gradient.setColorAt(0, cp3)
gradient.setColorAt(1, QtGui.QColor.fromRgbF(0, 0, 0, 0))
brush1 = QtGui.QBrush(gradient)

LOG_DIR = os.path.join(BASE_DIR, '../logs')
config.dictConfig(LOGGING)
LOGGER = logging.getLogger('central.sendem_network_client')
LOGGER.debug(path)
LOGGER.debug('__name__: ' + str(__name__))
LOGGER.debug(BASE_DIR)
LOGGER.debug(str(LOGGER.handlers))


class Client(Appliance):
    """
    Network Client.
    """
    def __init__(self, data, queuey, lck):
        super().__init__()
        config.dictConfig(LOGGING)
        self.CLIENT_LOGGER = logging.getLogger('central.sendem_network_client')
        self.CLIENT_LOGGER.debug('client logging setup.')
        self.CLIENT_LOGGER.debug(namespace_from_dir)
        self.options = []
        if data['Options:']:
            for n in data:
                if n.startswith('--'):
                    self.options = self.options.append(n)
            self.index = len(data)
        # LOGGER.debug('Client with options {r}'.format(r=self.options))
        self.__RUN__ = True
        self.__PORT__ = 7788
        self.__SERVER__ = "127.0.0.1"
        self.__CLIENT_DEVICE_ADDR__ = (self.__SERVER__, self.__PORT__)
        self.__no_server__ = False
        self.__xbuffy__ = []
        self.buffer_lock = t_lock()
        # id, vname, vdescription, vuser_number, vtimestamp_last_online
        self.directory = []
        self.__jqueue_to_gui__ = queuey
        self.__to_gui_lock__ = lck
        self.__fn_fal__ = -1
        self.__DEFAULT_TIMEOUT__ = 100
        self.__client_socket__ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.__client_socket__.setblocking(True)
        # self.__client_socket__.settimeout(5200)
        try:
            self.__client_socket__.connect(self.__CLIENT_DEVICE_ADDR__)
        except ConnectionRefusedError as ce:
            self.CLIENT_LOGGER.debug(ce)
            self.__no_server__ = True

    def sendem(self):
        """
        only sending via one socket for now.
        :return:
        """
        data1 = None
        ret_num = None
        while True:
            if self.__xbuffy__.__len__() > 0:
                with self.buffer_lock:
                    self.CLIENT_LOGGER.debug('buffer locked')
                    for h in self.__xbuffy__:
                        hmsg = h.get_message()
                        self.CLIENT_LOGGER.debug(hmsg)
                        data1 = self.change_to_bytes(hmsg)
                        if self.__client_socket__.fileno() == -1:
                            try:
                                # reset/create socket connection if fd -1
                                self.CLIENT_LOGGER.debug('disconnecting ... client resetting socket')
                                self.__client_socket__.shutdown(socket.SHUT_RDWR)
                                self.__client_socket__.close()
                                self.__client_socket__ = socket.socket(
                                    socket.AF_INET,
                                    socket.SOCK_STREAM,  # fileno=self.__fn_fal__  # | socket.SOCK_NONBLOCK
                                    )
                                self.__client_socket__.connect(self.__CLIENT_DEVICE_ADDR__)
                            except TimeoutError:
                                self.CLIENT_LOGGER.debug(TimeoutError)
                                raise TimeoutError
                            except OSError:
                                self.CLIENT_LOGGER.debug(OSError)
                                raise OSError
                        try:
                            ret_num = self.__client_socket__.send(data1)
                            self.CLIENT_LOGGER.debug(str(ret_num))
                        except TimeoutError:
                            self.CLIENT_LOGGER.debug(TimeoutError)
                        except BrokenPipeError:
                            self.CLIENT_LOGGER.debug('Client socket cannot send:')
                            self.CLIENT_LOGGER.debug(BrokenPipeError.__doc__)
                    self.CLIENT_LOGGER.debug('buffer un-locked')
                    if ret_num is not None and ret_num > 0:
                        self.__xbuffy__.remove(h)
            else:
                time.sleep(0.5)

    def calliope1(self):
        """
        Process incoming widget data.
        """
        queue_id = str(id(self.__jqueue_to_gui__))
        self.CLIENT_LOGGER.debug(queue_id)
        while True:
            data_in = self.__jqueue_to_gui__.get()  # bytes coming in. must convert to string obj.
            with self.buffer_lock:
                self.CLIENT_LOGGER.debug('creating mu')
                mu = MessageUnit(data_in)  # Class MessageUnit init convert from bytes to obj
                self.__xbuffy__.append(mu)

    def zcalliope2(self):
        """
        Tag messages with uuid etc.
        """
        while True:
            time.sleep(0.1)

    def start(self):
        time.sleep(2)
        gpidstr = 'pid: ' + str(os.getpid())
        self.CLIENT_LOGGER.debug(gpidstr)
        mu = MessageUnit('starting comms..')
        with self.buffer_lock:
            self.__xbuffy__.append(mu)
        c1 = None
        try:
            c1 = Thread(target=self.calliope1, name='Calliope1', daemon=True)
            c1.start()
        except OSError:
            self.CLIENT_LOGGER.debug(OSError)

        c2 = Thread(target=self.zcalliope2, name='ZCalliope2', daemon=True)
        c2.start()

        s = Thread(target=self.sendem, name='Sendem', daemon=True)
        s.start()

        active_threads_watched_and_monitored = {'c1': c1, 'c2': c2, 's': s}
        function_map_threads = {'c1': self.calliope1, 'c2': self.zcalliope2, 's': self.sendem}
        vxi = 0.0
        while self.__RUN__:
            vxi += 1
            time.sleep(1)
            for x in active_threads_watched_and_monitored.keys():
                if not active_threads_watched_and_monitored[x].is_alive():
                    self.CLIENT_LOGGER.debug('thread is dead...')
                    temp_th = Thread(
                        target=function_map_threads[x],
                        daemon=True)
                    active_threads_watched_and_monitored[x].join()
                    active_threads_watched_and_monitored[x] = temp_th
                    temp_th.start()
                    self.CLIENT_LOGGER.debug('client thread restarted.' + temp_th.name)


class SendWorker(QtCore.QRunnable):
    """
    Sendem GUI Worker thread, not real threads or threadpools.  QT framework!!
    """

    def __init__(self, *args):
        super().__init__()
        config.dictConfig(LOGGING)
        self.CLIENT_LOGGER = logging.getLogger('central.sendem_qt_runnable_class')
        queue_to_network_client, send_text = args
        self.queue_to_network_client = queue_to_network_client
        self.send_text = send_text
        self.CLIENT_LOGGER.debug('init finished sendworker')

    @QtCore.pyqtSlot()
    def run(self):
        """
        """
        send_b = bytes(self.send_text, 'utf-8')
        # assert(type(send_b), bytes)
        self.CLIENT_LOGGER.debug('putting ..')
        self.queue_to_network_client.put(send_b)
        self.CLIENT_LOGGER.debug('finished put')


class ClientWidget(QtWidgets.QWidget):
    def __init__(self, pipet, lck):
        super().__init__()
        config.dictConfig(LOGGING)
        self.WIDGET_LOGGER = logging.getLogger('central.sendem_widget')
        self.WIDGET_LOGGER.debug('QT widget logging setup.')
        self.threadpool = QtCore.QThreadPool()
        #  and-engine
        self.__queue_to_network_client__ = pipet
        self.buttonx = QtWidgets.QPushButton("STUUR")  # ("WYV974GP")("CA 800 162")
        self.buttonx.setStyleSheet('QPushButton {background:#6C8F8B}')
        self.button_contact = QtWidgets.QPushButton("contact IDs")

        nunchucks_icon = QtGui.QPixmap("../artwork/nunchucks.bmp")
        cardsIcon = QtGui.QPixmap("../artwork/list_circle_bigger_64.png")
        self.buttonx.setIcon(QtGui.QIcon(nunchucks_icon))

        self.button_contact.setIcon(QtGui.QIcon(cardsIcon))
        self.button_contact.setStyleSheet('QPushButton {background:#6C8F8B}')

        self.jtext = QtWidgets.QLabel(text="SENDEM", alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.jtext.setFont(QtGui.QFont("Sanserif", 15))
        self.inner_label_text_data = "Sendem start..."
        self.inner_label = QtWidgets.QLabel(text=self.inner_label_text_data, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.editor_of_shredder = QtWidgets.QTextEdit()
        self.editor_of_shredder.setStyleSheet('QWidget {background:#709591}')

        self.setStyleSheet('QWidget {background:#285A55}')

        self.line_in = QtWidgets.QLineEdit()
        self.list_of_contacts = QtWidgets.QListWidget()
        self.list_of_contacts.alternatingRowColors()
        self.list_of_contacts.setStyleSheet('QListWidget {background:#002B27}')
        self.list_of_contacts.itemClicked.connect(self.activate_contact)
        # self.list_of_contacts.setAutoFillBackground(True)# ?
        self.outer_frame_layout = QtWidgets.QVBoxLayout()
        self.j_layout = QtWidgets.QVBoxLayout()
        # rack'em Bob
        self.inner_edit_layout = QtWidgets.QVBoxLayout()
        self.j_layout.addWidget(self.jtext)
        self.j_layout.addWidget(self.buttonx)
        self.j_layout.addWidget(self.button_contact, alignment=QtCore.Qt.AlignmentFlag.AlignBottom)
        self.inner_edit_layout.addWidget(self.inner_label)

        self.inner_edit_layout.addWidget(self.editor_of_shredder)
        self.j_layout.addWidget(self.line_in)
        self.j_layout.addWidget(self.list_of_contacts)
        self.line_in.hide()
        self.list_of_contacts.hide()

        self.buttonx.clicked.connect(self.send_chat_text_from_gui)
        self.button_contact.clicked.connect(self.contact_list_show)
        #  self.editor_of_shredder.textChanged.connect(self.typing_now)
        self.line_in.editingFinished.connect(self.input_for_contact_create)

        self.outer_frame_layout.addLayout(self.j_layout)
        self.outer_frame_layout.addLayout(self.inner_edit_layout)
        self.setLayout(self.outer_frame_layout)

        self.directory = []
        self.__queue_lock__ = lck
        self.__typing_flag__ = False
        self.__timer_short__ = None

    def input_for_contact_create(self):
        """inxup"""
        username_from_gui = self.line_in.text()
        self.WIDGET_LOGGER.debug('creating contact')
        self.WIDGET_LOGGER.debug(username_from_gui)
        woodwork = '{vname:' + username_from_gui + ',vdescription:"old guy", vuser_number:0792217404,\
        vtimestamp_last_online:' + datetime.datetime.now().isoformat() + '}'
        # send to client

        send_str = bytes('{app_data:true, new_contact:true, contact_data:' + woodwork + '}', 'uft-8')
        try:
            self.__queue_to_network_client__.put(send_str, timeout=1)
        except self.__queue_to_network_client__.Full:
            self.WIDGET_LOGGER.debug('Widget sending: Queue is full')

    def contact_list_show(self):
        # if already visible
        if self.list_of_contacts.isVisibleTo(self):
            self.list_of_contacts.hide()
            self.line_in.hide()

            self.buttonx.show()
            self.inner_label.show()
            self.editor_of_shredder.show()
        else:
            self.WIDGET_LOGGER.debug('show contacts')
            # test account for gui testing
            t1 = datetime.datetime.now()
            c1 = ContactItem(uuid.uuid4(), 'asdfasdf', 'adefawef', 'asdsadfawfe', t1)
            c1.set_list_mode_artwork()
            self.directory.append(c1)
            # end test account
            for contact_item in self.directory:
                self.list_of_contacts.addItem(contact_item)
                # print('item added')
            self.list_of_contacts.show()
            self.line_in.show()
            self.j_layout.addWidget(self.list_of_contacts)

            self.buttonx.hide()
            self.editor_of_shredder.hide()
            self.inner_label.hide()

    def get_json_from_contacts(self):
        woodwork = ''
        for line in self.directory:
            woodwork += line.contact_dump()
        return '{app_data:true, contact_list:[' + woodwork + ']}'

    def send_contact_from_gui(self):
        # package as JSON object and send possibly to be saved in dj server
        text_from_contacts = self.get_json_from_contacts()
        # directory maintenance is done. Do update of timer or hash data or whatever
        with self.__queue_lock__:
            self.__queue_to_network_client__.put(text_from_contacts)

    def send_chat_text_from_gui(self):
        self.WIDGET_LOGGER.debug(' send_chat_text_from_gui ')
        text_from_gui = self.editor_of_shredder.document()
        send_text_from_gui = str(text_from_gui.toRawText()) + ' '  # trailing slash issue
        self.WIDGET_LOGGER.debug('got text from gui ')
        send_text = copy.deepcopy(send_text_from_gui)
        self.WIDGET_LOGGER.debug('deepcopied text from gui ')
        try:
            self.editor_of_shredder.clear()
        except BaseException as e:
            self.WIDGET_LOGGER.debug('editor Error ')
            self.WIDGET_LOGGER.debug(e)
        try:
            sw = SendWorker(self.__queue_to_network_client__, send_text)
            self.threadpool.start(sw)
            self.WIDGET_LOGGER.debug('sw sent to threadpool ')
        except BaseException as e:
            self.WIDGET_LOGGER.debug('SendWorker Error ')
            self.WIDGET_LOGGER.debug(OSError.__doc__)
        self.WIDGET_LOGGER.debug('SendWorker created ')

        self.WIDGET_LOGGER.debug(' QRunnable threadpool started ')

    def send_typing_alert(self):
        if self.__typing_flag__:
            self.__queue_to_network_client__.put(b'typing')
        self.WIDGET_LOGGER.debug(' typing alert sent ')

    def typing_now_flag_on(self):
        """
        Callback only runs if timer was triggered.
        :return:
        """
        self.__typing_flag__ = True
        del self.__timer_short__
        self.__timer_short__ = None
        self.WIDGET_LOGGER.debug('flag on')

    def timer_typing_now(self):
        """
        Start and Reset typing alert timer as necessary.
        :return:
        """
        if self.__timer_short__ is None:  # starting
            self.send_typing_alert()
            self.__timer_short__ = Timer(3, self.typing_now_flag_on)
            self.__timer_short__.start()
            # Before timer triggers flag must be down
            self.__typing_flag__ = False
        elif self.__timer_short__ is not None and self.__typing_flag__:  # reset
            self.send_typing_alert()
            self.__typing_flag__ = False

    def typing_now(self):
        self.timer_typing_now()
        # until timer triggers flag must be down

    def activate_contact(self):
        lysie_item = self.list_of_contacts.currentItem()
        # @TODO: check if lysie is of type ContactItem
        self.active_contact = lysie_item
        self.WIDGET_LOGGER.debug(self.active_contact)
        self.inner_label.setText(self.active_contact.display_name())
        self.inner_label.show()

    def login(self):
        username = 'joe123'
        password = 'joepassword123#'
        
