#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
use following resource for sorting usermodel cutom setup.
https://testdriven.io/blog/django-custom-user-model/
"""
from django.db import models
from django.apps import AppConfig
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid
import logging
from .managers import CustomUserManager

LOGGER = logging.getLogger('coasterx.request')


class SendemUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom django user model.
    """
    username = None
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(_("firstname"), max_length=128)
    last_name = models.CharField(_("lastname"), max_length=128, blank=True)
    is_active = models.BooleanField(_("active"), default=True)
    is_staff = models.BooleanField(_("staff"), default=False)
    is_admin = models.BooleanField(_("admin"), default=False)
    date_of_birth = models.DateField(_("date of birth"), blank=True, null=True)
    about = models.TextField(_("about"), blank=True)
    start_date = models.DateField(_("start date"), blank=True, null=True)
    date_joined = models.DateField(_("date joined"), blank=True, null=True)
    avatar = models.ImageField(_("picture"), blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']
    EMAIL_FIELD = 'email'
    objects = CustomUserManager()
    class Meta:
        verbose_name_plural = "Sendem Users custom"

    """SendemUser class method:"""
    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        LOGGER.debug(perm)
        LOGGER.debug(self.get_all_permissions(obj))
        if perm in self.get_all_permissions(): # list perms and check value
            return True
        else:
            return False

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def get_full_name(self):
        """return longer repr"""
        return "%s %s" % (self.first_name, self.last_name)

    def get_short_name(self):
        """return longer repr"""
        return "%s" % (self.first_name)

class VClientListUnit(models.Model):
    """
    Keep list of clients for a user as reference to their network.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vname = models.CharField(max_length=64)
    vdescription = models.TextField()
    vuser_number = models.CharField(max_length=32, default='')
    vtimestamp_last_online = models.DateTimeField(auto_now=True)
    sendemuserofclientlist = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='appcontact')

    class Meta:
        verbose_name_plural = "populate access list"

    def __repr__(self):
        return str(self.vname)
