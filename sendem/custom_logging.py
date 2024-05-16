#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging


class DeadReckoningLogHandler(logging.FileHandler):
    """reentrant preventing lock.
    Not sure if default lock does similar but this works in testing.
    Assign e-paper device by name.
    """
    def __init__(self, filename, *args, **kwargs):
        self.lock = kwargs['lock']
        self.noreturn = kwargs.pop('lock')
        super().__init__(filename, mode='a', *args, **kwargs)

