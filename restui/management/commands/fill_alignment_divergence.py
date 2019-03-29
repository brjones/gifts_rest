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

from django.core.management.base import BaseCommand

from restui.models.mappings import Mapping


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Back-filling protein alignment divergence")

        mappings = Mapping.objects.all()

        for mapping in mappings:
            print("Mapping id {}".format(mapping.mapping_id))
            difference = mapping.difference

            mapping.alignment_difference = difference

            mapping.save()
