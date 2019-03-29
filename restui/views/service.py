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

from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response

from restui.serializers.service import StatusSerializer


class PingService(APIView):
    """
    Return service status (0 if ok)
    """

    def get(self, request):
        serializer = StatusSerializer(
            {'ping': 0}
        )
        return Response(serializer.data)
