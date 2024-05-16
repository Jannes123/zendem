#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from ...serializers import SendemUserSerializer

import logging
LOGGER = logging.getLogger('coasterx.request')

UserModel = get_user_model()
user1 = UserModel.objects.create_user(email='jan101@gmail.com',
                                      first_name='Johannes',
                                      last_name='Engelbrecht',
                                      password='asdfasfd234')


class Command(BaseCommand):
    help = 'Writes out ambiguous serializer behaviour.'

    def setup(self):
        """
        setup for serializers
        :return:
        """
        self.ss = SendemUserSerializer(user1)
        self.stdout.write(str(self.ss))
        LOGGER.debug(user1)

    def output_serialized(self):
        msg = str(self.ss.data)
        LOGGER.debug(msg)
        self.stdout.write(msg=msg, ending='--\n')

    def handle(self, *args, **kwargs):
        time = timezone.now().strftime('%X')
        self.stdout.write("It's now %s" % time)
        self.stdout.write(str(kwargs.items()))
        self.stdout.write(str(args))
        self.setup()
        self.output_serialized()

