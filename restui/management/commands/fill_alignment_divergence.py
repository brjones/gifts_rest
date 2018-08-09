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
