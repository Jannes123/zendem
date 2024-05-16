#!/usr/bin/env python3
# -*- coding : utf-8 -*-
from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin
from .models import VClientListUnit, SendemUser
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import gettext_lazy as _

import logging
LOGGER = logging.getLogger('coasterx.request')


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = SendemUser
        fields = ["email",
                  "password",
                  "first_name",
                  "last_name",
                  "date_of_birth",
                  "is_active",
                  "is_admin",
                  "is_staff",
                  "date_joined",
                  "about",
                  "start_date",
                  "avatar",
                  "is_superuser"]


class UserCreationForm(forms.ModelForm):
    """copied dj docs."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = SendemUser
        fields = ["email", "first_name", "last_name", "password1", "password2"]

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class VSendemUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = SendemUser
    list_display = ("email", "first_name", "last_name", "is_staff", "get_contacts_names_only_preview")
    list_filter = ("is_superuser", "is_active", "groups")
    search_fields = ("first_name", "last_name", "email")
    ordering = ("email",)
    #exclude = ("last_name",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "password1", "password2"),
            },
        ),
    )

    def get_contacts(self, obj):
        """returns a queryset containing relatedfield on VClientListUnit"""
        LOGGER.debug(obj.__dict__)
        x = VClientListUnit.objects.filter(sendemuserofclientlist=obj)
        LOGGER.debug(HttpResponse(x.count()))
        LOGGER.debug(self.add_form)
        return str(x.count()) + str(' contacts. ') + str(x[:2])

    def get_contacts_names_only_preview(self, obj):
        """show condensed presentation of contacts list in admin view of this SendemUser"""
        LOGGER.debug(obj.__dict__)
        data_result = VClientListUnit.objects.filter(sendemuserofclientlist=obj)
        names_only_data = [q_item.vname for q_item in data_result]
        names_only = ', '.join(names_only_data[:2])
        return str(data_result.count()) + ' contacts. ' + str(names_only) + " ..."


class VClientListUnitAdmin(admin.ModelAdmin):
    model = VClientListUnit
    list_display = ['vname', 'vdescription', 'vuser_number', 'get_owner']

    def get_owner(self, obj):
        return str(obj.sendemuserofclientlist.all()[0].email) + ', id:' + str(obj.sendemuserofclientlist.all()[0].id)


admin.site.register(SendemUser, VSendemUserAdmin)
admin.site.register(VClientListUnit, VClientListUnitAdmin)

