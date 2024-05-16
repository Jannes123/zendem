#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.shortcuts import render
from rest_framework.authentication import SessionAuthentication, TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import ObjectDoesNotExist
from sys import path
from chatshredder.sendemdj.sendemauth.models import VClientListUnit
from chatshredder.sendemdj.sendemauth.serializers import ClientCollectionSerializer
import jws
import jwt
import json

import logging
LOGGER = logging.getLogger('coasterx.request')
LOGGER.debug(path)


def to_jwt(claim, algo, key):

    header = {'typ': 'JWT', 'alg': algo}
    return '.'.join([
        jws.utils.encode(header),
        jws.utils.encode(claim),
        jws.sign(header, claim, key)
    ])

def from_jwt(jwt, key):
    "Returns the decoded claim on success, or throws exception on error"
    (header, claim, sig) = jwt.split('.')
    header = jws.utils.from_base64(header)
    claim = jws.utils.from_base64(claim)
    jws.verify(header, claim, sig, key, is_json=True)
    return jws.utils.from_json(claim)


class Login(APIView):

    def post(self, request, *args, **kwargs):
        if not request.data:
            return Response({'Error': "Please provide username/password"}, status="400")

        username = request.data['username']
        password = request.data['password']
        try:
            user = User.objects.get(username=username, password=password)
        except User.DoesNotExist:
            return Response({'Error': "Invalid username/password"}, status="400")
        if user:
            payload = {
                'id': user.id,
                'email': user.email,
            }
            jwt_token = {'token': jwt.encode(payload, "SECRET_KEY")}

            return Response(
                json.dumps(jwt_token),
                status=200,
                content_type="application/json"
            )
        else:
            return Response(
                json.dumps({'Error': "Invalid credentials"}),
                status=400,
                content_type="application/json"
            )


class SendemAdminBackend(BaseBackend):
    """
    Not a view
    for a custom user model to work:
    override authenticate method in BaseBackend Class of auth module.
    extend default User model in models.py
    specify AUTH_USER_MODEL in settings.py
    """
    def has_perm(self, user_obj, perm, obj=None):
        return user_obj.username == settings.ADMIN_LOGIN

    def authenticate(self, request, username=None, password=None, **kwargs):
        LOGGER.debug(username)
        LOGGER.debug(request.META)
        LOGGER.debug("SendemAdminBackend")
        UserModel = get_user_model()
        if username is None:
            username = None
            try:
                username = kwargs.get(UserModel.USERNAME_FIELD)
            except ObjectDoesNotExist:
                LOGGER.debug(ObjectDoesNotExist)

        if username is None or password is None:
            return

        try:
            # use username to get user db-object
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            # Run the default password hasher
            # difference between an existing and a nonexistent user (#20760)
            UserModel().set_password(password)
        # now only you gots the user phew!
        if user.is_authenticated:
            return user
        elif user.check_password(password) and self.user_can_authenticate(user):
            LOGGER.debug('--password correct--')
            # success is returning a user object
            return user
        else:
            LOGGER.debug('User authentication not implemented')


class TokenView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, AllowAny]
    def get(self, request, format=None):

        # password auth used to get token followed by encrypted communication from here on
        LOGGER.debug("get -- get token")
        LOGGER.debug(request.META)
        UserModel = get_user_model()
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        user = UserModel._default_manager.get_by_natural_key(request.user)
        #token = Token.objects.create_or_(user=user)
        #content['token'] = token.key
        return Response(content)

# get token
# refresh token views
# JWS https://pypi.org/project/jws/  for access from apps and pages

class RefreshTokenView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
# curl --trace - --trace-time http://127.0.0.1:8000/rest-auth/tryfirst
    def get(self, request, format=None):
        LOGGER.debug("get -- refresh token")
        LOGGER.debug(request.META)
        UserModel = get_user_model()
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        user = UserModel._default_manager.get_by_natural_key(request.user)
        # token = Token.objects.create(user=user)
        # content['token'] = token.key
        return Response(content)


def specific_list_from_user_id(idofuser):
    sendem_list = VClientListUnit.objects.filter(vuser_object_id=idofuser)
    LOGGER.debug(sendem_list)
    return sendem_list


class ClientCollectionSetView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, format=None):
        # compiles list of contacts for current user
        UserModel = get_user_model()
        user = UserModel._default_manager.get_by_natural_key(request.user)
        response = specific_list_from_user_id(user.id)
        # serializer
        serializer = ClientCollectionSerializer(response, many=True)
        LOGGER.debug("get list for " + str(user.username))
        payload = Response(serializer.data)
        # @TODO: encryption setup?? jwt.encode and jwt.decode signing and header
        return payload

    def create(self, request, format=None):
        # find user first if exist add to contact list
        UserModel = get_user_model()
        user = UserModel._default_manager.get_by_natural_key(request.user)
        pass