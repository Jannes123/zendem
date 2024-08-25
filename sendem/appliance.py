#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Abstracting network elements of same system for conforming them into same settings as far as possible.
"""
class Appliance():
    """
    Network appliance base class.
    Network settings and defaults home.
    """
    def __init__(self):
        self.__FORMAT__ = 'utf-8'
        self.__HEADER__ = 128
        self.__DISCONNECT__ = '!TERMINATE'
        self.__SHUTDOWN__ = '!SHUTDOWN'

    def change_to_bytes(self, data_message: str):
        # check size and fragment if necessary
        data_message_en = str(data_message)
        data_message_length = len(data_message_en)
        xzero_add = ' '*(self.__HEADER__ - data_message_length)
        dx = data_message_en + xzero_add
        data1_bytes = bytes(dx, 'utf-8')
        return data1_bytes

    def authenticated_incoming(self, data_message: str):
        """Try auth to database credentials."""
        return data_message
