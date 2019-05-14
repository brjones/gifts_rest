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

from django.conf import settings

from cryptography.x509 import load_pem_x509_certificate as load_pem
from cryptography.hazmat.backends import default_backend

import os
import requests


class AAPAcess(object):
    """
    Singleton object to access the AAP service

    Singleton to fetch/load the public key from the AAP service,
    authenticate jwt and fetch user profiles.
    """
    __instance = None
    _cert = None

    def __new__(cls):
        """
        Initialize the singleton if an instance doesn't already
        exist. Ensure the public PEM from the AAP service is
        loaded for use.
        """
        if AAPAcess.__instance is None:
            # log Initializing authentication singleton
            AAPAcess.__instance = object.__new__(cls)

        AAPAcess.__instance._loadPEM()
        return AAPAcess.__instance

    def _loadPEM(self):
        """
        Load the public PEM for validating jwts from our
        local cache file. Go fetch it if we don't already have it.
        """

        if self._cert is not None:
            return

        pem_filename = settings.AAP_PEM_FILE

        # log Loading public PEM certificate

        if not os.path.isfile(pem_filename):
            # The pem file hasn't been downloaded yet, grab it
            try:
                self.fetchPEM()
            except Exception:
                # log Error fetching PEM from AAP when trying to lead PEM
                raise

        try:
            with open(pem_filename, 'r') as cert_file:
                cert = load_pem(cert_file.read().encode(),
                                default_backend())
                self.cert = cert.public_key()
        except Exception:
            # log Error loading PEM from local file
            # re-raise the exception received
            raise

    def fetchPEM(self):
        """
        Fetch the PEM from the AAP service

        Fetch the PEM certificate from the AAP server and
        save it to our local cache file.
        """
        pem_filename = settings.AAP_PEM_FILE

        # log Fetching PEM certificate from AAP service
        r = requests.get(settings.AAP_PEM_URL)

        if r.status_code != requests.codes.ok:
            raise Exception("Unable to fetch AAP PEM certificate")

        if r.text is not None:
            with open(pem_filename, 'w') as cert_file:
                cert_file.write(r.text)

    @property
    def cert(self):
        """
        Accessor to fetch the certificate
        """
        return self._cert

    @cert.setter
    def cert(self, cert):
        self._cert = cert

    def fetchProfile(self, elixir_id, token):
        """
        Fetch a user profile from the AAP service

        Fetch a profile for a user using their exlixir_id
        and authenticating via the jwt token we've been
        presented.
        """

        #log Fetching profile from AAP service for elixir_id

        headers = {"Authorization": "Bearer {}".format(token),
                   "Content-Type": "application/json;charset=UTF-8"}

        r = requests.get(settings.AAP_PROFILE_URL.format(elixir_id), headers=headers)

        if r.status_code != requests.codes.ok:
            raise Exception("Error fetching profile, status: {}".format(r.status_code))

        return r.json()
