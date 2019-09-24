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
from django.apps import AppConfig
from django.conf import settings

from aap_auth.auth import AAPAcess


class AppAuthConfig(AppConfig):
    name = 'aap_auth'

    def ready(self):
        """
        Initialize the AAP authentication app

        Load the AAP service key in to the authentication
        singleton, for use as calls come in.
        """
        #log Initializing AAP app

        AAPAcess()
