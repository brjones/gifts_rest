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

from restui.models.mappings import Alignment
from restui.models.mappings import AlignmentRun
# from restui.models.mappings import Mapping
# from restui.models.mappings import MappingHistory
# from restui.models.mappings import ReleaseMappingHistory

from rest_framework import serializers


class AlignmentRunSerializer(serializers.ModelSerializer):
    """
    Serialize an AlignmentRun instance
    """

    class Meta:
        model = AlignmentRun
        fields = '__all__'


class AlignmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Alignment
        fields = '__all__'
