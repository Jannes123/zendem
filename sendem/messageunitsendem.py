#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import uuid


class MessageUnit():
    def __init__(self, message, profile_id=None):
        if type(message)==bytes:
            self.__message__ = message.decode("utf-8")
        else:
            self.__message__ = message
        self.__read__ = False
        self.__admin_id__ = uuid.uuid4() # used to id the message
        self.__sendem_profile__ = profile_id # uuid.uuid4()# sendem profile id retreived from direct webcall by GUI

    def get_message(self):
        return self.__message__

    def get_read(self):
        """check if the message has been read."""
        return self.__read__

    def get_admin_id(self):
        return self.__admin_id__

    def set_read(self, read=True):
        """the message has been read."""
        self.__read__ = read
