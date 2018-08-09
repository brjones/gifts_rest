from django.core.management.base import BaseCommand
from django.db.models import Max
import sys

from restui.models.mappings import Mapping

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        print("Ensure all mappings have a unique grouping_id")
        
        max_grouping_id = Mapping.objects.aggregate(largest=Max('unique_grouping_id'))
        if not max_grouping_id['largest']:
            max_grouping_id = 1

        mappings = Mapping.objects.filter(unique_grouping_id__isnull=True).order_by('grouping_id').all()
        
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
