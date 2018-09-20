from rest_framework.exceptions import APIException

class FalloverROException(APIException):
    """
    Exception to handle when we're in fallover mode and endpoints are read only.
    """
    status_code = 503
    default_detail = 'We\'re in fallover mode. Updates disabled, try again later.'
    default_code = 'service_unavailable'
