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
