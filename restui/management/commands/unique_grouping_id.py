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

from __future__ import print_function

import sys
from django.core.management.base import BaseCommand
from django.db.models import Max
from restui.models.mappings import Mapping


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Ensure all mappings have a unique grouping_id")

        max_grouping_id = Mapping.objects.aggregate(
            largest=Max('unique_grouping_id')
        )

        if not max_grouping_id['largest']:
            max_grouping_id = 1

        mappings = Mapping.objects.filter(
            unique_grouping_id__isnull=True
        ).order_by('grouping_id').all()

        if mappings.first():
            current_group = mappings.first().grouping_id
        else:
            print("No non-unique grouping id mappings, quitting")
            sys.exit()

        grouped_mappings = {}

        for mapping in mappings:
            if mapping.grouping_id != current_group:
                print("\tUpdating group {} with unique ids".format(current_group))
                # We're on to the next group, update the records we've found so far
                for tax, m_group in grouped_mappings.items():
                    print("\tTax id {}".format(tax))
                    for m in m_group:
                        m.unique_grouping_id = max_grouping_id
                        m.save()

                    max_grouping_id = max_grouping_id + 1

                # Then clear the grouped_mappings hash and start again
                grouped_mappings = {}
                current_group = mapping.grouping_id

            # Stuff the mapping in the tax group for this grouping_id
            print("Storing mapping id {}".format(mapping.mapping_id))
            taxid = mapping.uniprot.uniprot_tax_id
            if taxid not in grouped_mappings:
                grouped_mappings[taxid] = []

            grouped_mappings[taxid].append(mapping)
