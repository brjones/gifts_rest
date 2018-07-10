from rest_framework import authentication
from aap_auth.models import AAPUser as User

from aap_client.tokens import decode_token
from jwt import DecodeError, InvalidTokenError as JWTInvalidTokenError

from aap_auth.auth import AAPAcess

from future.utils import raise_with_traceback

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
            decoded_token = decode_token(jwt, AAPAcess().cert)
        except DecodeError as err:
            raise_with_traceback(
                Exception(u'Unable to decode token: {}'.format(err)))
        except JWTInvalidTokenError as err:
            raise_with_traceback(
                Exception(u'{}'.format(err)))
        
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
