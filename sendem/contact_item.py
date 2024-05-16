#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import json
from PyQt6 import QtWidgets, QtGui


class ContactItem(QtWidgets.QListWidgetItem):
    """contact list entry items"""
    def __init__(self, sendem_id, vname, vdescription, vuser_number, vtimestamp_last_online):
        super().__init__()
        self.__id__ = sendem_id
        self.__vname__ = vname  # normal username
        self.__vdescription__ = vdescription  # describe user or daily message
        self.__vuser_number__ = vuser_number  # telephone nr
        self.__vtimestamp_last_online__ = vtimestamp_last_online  # last time user opened the app.
        self.setText(self.display_name())

    def contact_dump(self):
        if isinstance(self.__vtimestamp_last_online__, datetime.datetime):
            # convert to text in iso format
            timestamp = self.__vtimestamp_last_online__.isoformat()
        else:
            # print('timestamp different type not  implemented', flush=True)
            timestamp = None
        data_contact = {
            'vname': self.__vname__,
            'vdescription': self.__vdescription__,
            'vuser_number': self.__vuser_number__,
            'vtimestamp_last_online': timestamp
            # t1 = datetime.datetime.now()  and t1.isoformat() '2023-10-25T15:42:34.965131'
            # datetime.strptime() to parse text and create datetime object
        }
        return json.dumps(data_contact)

    def display_text(self):
        return str(self.__vname__) + str(self.__vdescription__) + str(self.__vuser_number__) \
               + str(self.__vtimestamp_last_online__)

    def text(self):
        return self.display_text()

    def set_list_mode_artwork(self):
        self.setBackground(QtGui.QColor("green"))
        pass

    def set_detail_mode_artwork(self):
        pass

    def display_name(self):
        return str(self.__vname__)
