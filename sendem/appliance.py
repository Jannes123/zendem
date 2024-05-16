#!/usr/bin/env python3
# -*- coding: utf-8 -*-
class Appliance():

    def __init__(self):
        self.__FORMAT__= 'utf-8'
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

