#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from rest_framework.authentication import SessionAuthentication, TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ObjectDoesNotExist
from .models import VClientListUnit
from .serializers import ClientCollectionSerializer, SendemUserSerializer, RegisterSendemUserSerializer
import json
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import logging
LOGGER = logging.getLogger('coasterx.request')


class CustomUserCreate(APIView):
    permission_classes = [AllowAny]

    @csrf_exempt
    def post(self, request, format='json'):
        """
        curl -i -v -b cooker.txt -X POST -H 'Accept: application/json'         -H 'Content-Type: application/json'         --data '{"email":"jannes112@gmail.com","first_name":"Johannes","last_name":"Engelbrecht","password":"jannes110","csrfmiddlewaretoken":"dU6NN0yCUcNyJkuRrmJgE0RUDpNHty7h5ziGinRh5m9UAMvzo3GWUeb92edYC0La"}' "http://localhost:8000/sendem-rest-auth/api/custom-user-create/"

        curl -i -v -b cooker.txt -X POST -H 'Accept: application/json' \
        -H 'Content-Type: application/json' \
        --data '{"email":"jannes111@gmail.com",\
        "first_name":"Johannes",\
        "last_name":"Engelbrecht",\
        "password":"jannes110",\
        "csrfmiddlewaretoken":"dU6NN0yCUcNyJkuRrmJgE0RUDpNHty7h5ziGinRh5m9UAMvzo3GWUeb92edYC0La"}' \
        "http://localhost:8000/sendem-rest-auth/api/custom-user-create/"
        """
        serializer = RegisterSendemUserSerializer(data=request.data)
        LOGGER.debug(request.data)
        LOGGER.debug(request.user.__dict__)
        LOGGER.debug(request.__dict__)
        if serializer.is_valid():
            # should call custom create method on serializer
            user = serializer.save() # does this even return the obj
            if user:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):
    #fails on init of django.  has to be loaded once entire system is up and running.
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        """
        current usage:
        curl -i -v -X POST -u $username:$password -H 'Accept: application/json' -H 'Content-Type: application/json' --data '{"username":"tester@gmail.com","password":"jannes123", "id": 1}' "http://{$hostname}/sendem-rest-auth/login/"

        """
        next_page = reverse('contactlist', urlconf='sendemauth.urls')
        LOGGER.debug('LOGIN POST')
        LOGGER.debug(request.data)
        LOGGER.debug(request.user.__dict__)
        LOGGER.debug(request.__dict__)
        LOGGER.debug('next page:\n' + next_page)
        if not request.data:
            return Response({'Error': "Please provide username/password"}, status="400")

        username = request.data['email']
        password = request.data['password']
        LOGGER.debug(password)
        user = get_user_model()
        try:
            user = user.objects.get(email=username, password=password)
            LOGGER.debug(user)
        except user.DoesNotExist:
            return Response({'Error': "Invalid username/password"}, status="400")
        if user:
            payload = {
                'id': user.id,
                'email': user.email,
            }
            # redirect to base view or just auth?
            login(request, user, backend='sendemauth.SendemAdminBackend') # Badly named SendemAdminBackend is custom Modelbackend
            return Response(
                json.dumps({'message':'authenticated'}),
                status=200,
                content_type="application/json"
            )
        else:
            return Response(
                json.dumps({'Error': "Invalid credentials"}),
                status=400,
                content_type="application/json"
            )


class Logout(APIView):

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        LOGGER.debug('LOGOUT POST')
        if not request.data:
            return Response({'Error': "Please provide username/password"}, status="400")

        username = request.data['username']
        password = request.data['password']

        User = get_user_model()
        try:
            user = User.objects.get(email=username, password=password)
        except User.DoesNotExist:
            return Response({'Error': "Invalid username/password"}, status="400")
        if user:
            payload = {
                'id': user.id,
                'email': user.email,
            }
            logout(request)
            # redirect to base view or just auth?
            return Response(
                json.dumps({'message':'logged-out'}),
                status=200,
                content_type="application/json"
            )
        else:
            return Response(
                json.dumps({'Error': "Invalid credentials"}),
                status=400,
                content_type="application/json"
            )

    def get(self, request):
        """json logout view"""
        LOGGER.debug('LOGOUT GET')
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
            logout(request)
            # redirect to base view or just auth?
            return Response(
                json.dumps({'message': 'logged out'}),
                status=200,
                content_type="application/json"
            )
        else:
            return Response(
                json.dumps({'Error': "Invalid credentials"}),
                status=400,
                content_type="application/json"
            )


class SendemAdminBackend(ModelBackend):
    """
    Not a view
    for a custom user model to work:
    override authenticate method in BaseBackend Class of auth module.
    extend default User model in models.py
    specify AUTH_USER_MODEL in settings.py
    """

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
            LOGGER.debug('--user already authenticated. correct--')
            return user
        elif user.check_password(password) and self.user_can_authenticate(user):
            LOGGER.debug('--password correct--')
            # success is returning a user object
            return user
        else:
            LOGGER.debug('User authentication not implemented')


def specific_list_from_user_id(idofuser):
    """
    static
    :@param idofuser: gets appropriate user
    """
    sendem_list = VClientListUnit.objects.filter(sendemuserofclientlist__appcontact__id=idofuser)
    LOGGER.debug('type of sendem_list:')
    LOGGER.debug(str(type(sendem_list)))
    return sendem_list


class ClientCollectionSetView(APIView):
    """show all app contacts related to authenticated user"""
    # @TODO: encryption setup?? jwt.encode and jwt.decode signing and header
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]  # [AllowAny, Login]
    renderer_classes = [JSONRenderer]
    def get(self, request, format=None):
        # compiles list of contacts for current user
        UserModel = get_user_model()
        user = UserModel._default_manager.get_by_natural_key(request.user)
        client_list = user.appcontact.get_queryset()
        # deserializer
        try:
            serializer = ClientCollectionSerializer(client_list, many=True)
        except serializers.ValidationError:
            LOGGER.debug("validation error")
            content = {'please report': 'nothing found'}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            payload = Response(serializer.data)
        except serializers.ValidationError:
            LOGGER.debug('serializer class validation error:')

        return payload

    def put(self, request, format=None):
        # find user first if exist add to contact list
        LOGGER.debug('inserting new contact')
        LOGGER.debug(request.__dict__)
        UserModel = get_user_model()
        juser = UserModel._default_manager.get_by_natural_key(request.user)
        LOGGER.debug(request.data)
        data = request.data
        data['juser'] = juser
        serializer = ClientCollectionSerializer(data=request.data)
        # inverse deserialize into python datatype
        if serializer.is_valid():
            LOGGER.debug('data is valid')
            serializer.save()# save calls serializer create method if new entry
            LOGGER.debug('views saved.')
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        LOGGER.debug('inserting new contact')
        LOGGER.debug(request.__dict__)
        UserModel = get_user_model()
        juser = UserModel._default_manager.get_by_natural_key(request.user)
        LOGGER.debug(request.data)
        data = request.data
        data['juser'] = juser
        serializer = ClientCollectionSerializer(data=request.data)
        # inverse deserialize into python datatype
        if serializer.is_valid():
            LOGGER.debug('data is valid')
            serializer.save()# save calls serializer create method if new entry
            LOGGER.debug('views saved.')
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlacklistTokenUpdateView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = ()

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

