import multiprocessing
import os
import socket
import sys
import time
import unittest
from server import Server

sys.path.append(os.path.abspath('..'))
print(sys.path)
from sendem.zsendem import d_start_server


class TestServerSocketMethods(unittest.TestCase):
    """
    setup multiprocessing queue and run parallel process
    NOTE: python setsid method from os lib does NOT spawn/fork a new proc or pid.
    """

    def setUp(self):
        self.data = {'--help': False, '--now': False, '--time': False,
                     '--version': False,
                     '-h': False,
                     '<ip>': '127.0.0.1',
                     '<message>': None,
                     '<port>': '8899',
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
        self.raw_socket_object = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mothership = multiprocessing.get_context('fork')
        self.queue_in = self.mothership.Queue()
        self.queue_out = self.mothership.Queue()
        self.server_proc = None
        time.sleep(1)

    def daemonize_test_server(self):
        """
        fork and set new sid before forking the child process which runs the server
        :return:
        """
        if os.fork() != 0:
            return
        os.setsid()

        kiwis = {'q_out': self.queue_in, 'q_in': self.queue_out}
        self.server_proc = self.mothership.Process(
            target=d_start_server,
            name='TestApp',
            args=(Server, self.data),
            kwargs=kiwis,
            daemon=True)
        self.server_proc.start()
        self.server_proc.join()

    def test_messaging(self):
        """
        send message from vanilla socket to and check contents of server message-list.
        """
        self.daemonize_test_server()
        time.sleep(1)
        try:
            self.raw_socket_object.connect(('127.0.0.1', 8899))
        except OSError:
            print(OSError)

        __HEADER__ = 128
        data_message_en = 'abcdefg'
        data_message_length = len(data_message_en)
        xzero_add = ' ' * (__HEADER__ - data_message_length)
        dx = data_message_en + xzero_add
        data_raw = bytes(dx, 'utf-8')

        msg_data = data_raw
        self.raw_socket_object.send(msg_data)
        time.sleep(4)

        server_msg_list_last = None
        if self.queue_in.qsize() > 0:
            server_msg_list_last = self.queue_in.get()
        self.queue_out.put('!TERMINATE')
        time.sleep(1)
        self.assertEqual(server_msg_list_last, 'abcdefg', 'Messaging to server over AF_INET socket broken.')

    def tearDown(self):
        time.sleep(1)
        self.raw_socket_object.close()
        del self.raw_socket_object


if __name__ == '__main__':
    unittest.main()
