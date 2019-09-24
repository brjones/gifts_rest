"""
.. See the NOTICE file distributed with this work for additional information
   regarding copyright ownership.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from django.db import models

from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


class AAPUserManager(BaseUserManager):
    def create_user(self, elixir_id, full_name=None, email=None):
        """
        Creates and saves a User with the given elixir_id, full_name,
        and email address.
        """
        if not elixir_id:
            raise ValueError('Users must have an elixir_id')

        user = self.model(
            elixir_id=elixir_id,
            full_name=full_name,
            email=self.normalize_email(email),
        )

        user.save(using=self._db)
        return user

    def create_superuser(self, elixir_id, full_name=None, email=None):
        """
        Creates and saves a superuser with the given elixir_id, full_name,
        and email address.
        """
        user = self.create_user(
            elixir_id,
            full_name,
            email
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class AAPUser(AbstractBaseUser):
    elixir_id = models.CharField(max_length=50, blank=False, null=False, primary_key=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        blank=True,
    )
    is_admin = models.BooleanField(default=False)
    validated = models.BooleanField(default=False)

    objects = AAPUserManager()

    USERNAME_FIELD = 'elixir_id'

    def __str__(self):
        return self.elixir_id

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    @property
    def is_active(self):
        "Is the user validated"
        return self.validated
