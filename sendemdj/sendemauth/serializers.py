#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime

from rest_framework import serializers
from .models import VClientListUnit, SendemUser
import logging
LOGGER = logging.getLogger('coasterx.request')


class SendemUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    #password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = SendemUser
        fields = ('first_name', 'email', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}


class ClientCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VClientListUnit
        fields = ['vname',
                  'vdescription',
                  'vuser_number',
                  'vtimestamp_last_online']


class RegisterSendemUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendemUser
        fields = ('email', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        LOGGER.debug('serializer - create')
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
