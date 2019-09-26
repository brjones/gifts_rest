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

from rest_framework import authentication
from aap_auth.models import AAPUser as User

from aap_client.tokens import verify_token
from jwt import DecodeError, InvalidTokenError as JWTInvalidTokenError, ExpiredSignatureError

from aap_auth.auth import AAPAcess

from future.utils import raise_with_traceback

from django.conf import settings


class AAPBackend(authentication.BaseAuthentication):
    """
    Authenticate against the Elixir AAP service.
    """

    def authenticate(self, request, token=None):
        """
        We're going to check the request object, if it's not None,
        for a bearer token and authenticate against that. Alternatively
        the jwt token could be passed in the token field. The token
        from the request object takes precedence.

        The function will return a tuple of a User object and None (needed
        by the Django REST framework). If authentication fails, return
        None in place of a user object.
        """
        #log Authenticating user request
        jwt = None
        # Use the token, if it's set. This could be overridden by
        # the token from the request below.
        if token:
            jwt = token

        # verify that the auth header exists
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        if auth_header:

            # verify that the header is in the correct format
            # Authorization: Bearer <JWT>
            splitted_header = auth_header.split()
            if len(splitted_header) != 2 or not auth_header.startswith(u'Bearer '):
                #log invalid token format
                return None

            jwt = splitted_header[1]

        # If we haven't found a token in either the function paramters
        # or the headers, we can't authenticate.
        if not jwt:
            return None, None

        try:
            decoded_token = verify_token(jwt, AAPAcess().cert)
        except ExpiredSignatureError as err:
            return None, None
        except DecodeError as err:
            raise_with_traceback(
                Exception(u'Unable to decode token: {}'.format(err)))
        except JWTInvalidTokenError as err:
            raise_with_traceback(
                Exception(u'{}'.format(err)))

        if settings.AAP_GIFTS_DOMAIN not in decoded_token['domains']:
            return None, None

        try:
            user = User.objects.get(elixir_id=decoded_token['sub'])

            if not user.is_active:
                ''' If the user isn't active, we can't send back a user'''
                return None, None

        except User.DoesNotExist:
            ''' Create a new user'''
            #log Creating user for elixir_id
            profile = AAPAcess().fetchProfile(decoded_token['sub'], jwt)
            user = User(elixir_id=decoded_token['sub'],
                        full_name=profile['attributes']['name'],
                        email=profile['attributes']['email'])
            user.is_admin = False
            user.validated = True
            user.save()

        return user, None


    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class YesBackend(authentication.BaseAuthentication):
    """
    Dummy authentication backend that always says yes.
    """

    def authenticate(self, request, token=None):
        """
        We're going to make a dummy user, no matter what.
        Used only for testing.
        """
        #log WARNING Using dummy authenticator, if you're not testing this is very bad

        user = User(elixir_id='usr-d03bb471-5718-4899-addd-393de8b6ad69',
                    full_name="Zapp Brannigan",
                    email="zapp@nimbus.doop")
        user.is_admin = False
        user.validated = True

        return user, None

    def get_user(self, user_id):
        #log WARNING Using dummy authenticator, if you're not testing this is very bad

        user = User(elixir_id='usr-d03bb471-5718-4899-addd-393de8b6ad69',
                    full_name="Zapp Brannigan",
                    email="zapp@nimbus.doop")
        user.is_admin = False
        user.validated = True

        return user, None
