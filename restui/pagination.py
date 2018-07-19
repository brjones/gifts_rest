import pprint
from collections import OrderedDict
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

#
# TODO
#
# sequence and mappings facets
#
class FacetPagination(LimitOffsetPagination):
    def get_facets(self, data):

        status = OrderedDict([('name','status'),('label','Status'),('items',[])])
        organism = OrderedDict([('name','organism'),('label','Organism'),('items',[])])
        #######
        # TODO
        sequence = OrderedDict([('name','sequence'),('label','Sequence'),('items',[])])
        mappings = OrderedDict([('name','mappings'),('label','Type'),('items',[])])
        #######
        
        status_values, organism_values = [], []
        for result in data:
            for mapping in result["entryMappings"]:
                try:
                    if mapping["status"] not in status_values:
                        status_values.append(mapping["status"])
                        status["items"].append({ "name":mapping["status"], "label":mapping["status"].replace("_"," ").capitalize() })
                except AttributeError:
                    # mapping might not have status defined
                    status_values.append(None)
                    status["items"].append({ "name":"None", "label":"Not defined" })
                    
            if result["taxonomy"]["ensemblTaxId"] not in organism_values:
                organism_values.append(result["taxonomy"]["ensemblTaxId"])
                organism["items"].append({ "name":result["taxonomy"]["ensemblTaxId"], "label":result["taxonomy"]["species"] })

        return [ status, organism, sequence, mappings ]
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
            ('facets', self.get_facets(data))
        ]))
