#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.test import TestCase
from .models import VClientListUnit
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.test import TestCase


class ClientListUnitTestCase(TestCase):
    def setUp(self):
        # create user
        UserModel = get_user_model()
        user1 = UserModel._default_manager.create_user('impact', password='busy123')
        # user1 = User.objects.create_user('foo', password='bar')
        # create client-list
        x = VClientListUnit.objects.create(
            vname = "Client1Contact1",
            vdescription = "Very short descriptions or long description or nothing :-)",
            vuser_number = "13860771",
            vtimestamp_last_online = datetime.now(),
            )
        x.vuser_object.add(user1)

    def test_user_contact_list_exist(self):
        """test user contact list is created"""
        listy = VClientListUnit.objects.get(vname="Client1Contact1")
        print(listy.__dict__)
        self.assertEqual(listy.vuser_number, '13860771')


class UsersManagersTests(TestCase):

    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(email="normal@user.com", password="foo")
        self.assertEqual(user.email, "normal@user.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(user.username)
        except AttributeError:
            pass
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):
            User.objects.create_user(email="")
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="foo")

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(email="super@user.com", password="foo")
        self.assertEqual(admin_user.email, "super@user.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(admin_user.username)
        except AttributeError:
            pass
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="super@user.com", password="foo", is_superuser=False)



from rest_framework.test import APIClient

client = APIClient()
client.post('http://127.0.0.1:8000/sendem-rest-auth/login',
            {'username': 'impact', 'password': 'busy123'},
            format='json')

from requests.auth import HTTPBasicAuth

client.auth = HTTPBasicAuth('impact', 'busy123')
client.headers.update({'x-test': 'true'})