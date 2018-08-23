from collections import OrderedDict
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from restui.serializers.mappings import MappingsSerializer
from rest_framework import status
#
# TODO
#
# sequence and mappings facets
#
class FacetPagination(LimitOffsetPagination):
    def create_facets(self, queryset):
        statuses = OrderedDict([('name','status'),('label','Status'),('items',[])])
        organism = OrderedDict([('name','organism'),('label','Organism'),('items',[])])
        sequence = OrderedDict([('name','sequence'),('label','Sequence'),('items',[])])
        #######
        # TODO
        mappings = OrderedDict([('name','mappings'),('label','Type'),('items',[])])
        #######

        for species in queryset.species():
            organism["items"].append({ "name":species[0], "label":species[1] })
    
        for status in queryset.statuses():
            statuses["items"].append({ "name":MappingsSerializer.status_type(status), "label":MappingsSerializer.status_type(status).replace("_"," ").capitalize() })

        differences = queryset.divergences()
        if differences[0]:
            sequence["items"].append({ "label": "identical", "name": "identical", "count": differences[0] })
        if differences[1]:
            sequence["items"].append({ "label": "small", "name": "small", "count": differences[1] })
        if differences[2]:
            sequence["items"].append({ "label": "large", "name": "large", "count": differences[2] })
            
#        return [ statuses, organism, sequence, mappings ]
        return [ statuses, organism, sequence ]

    def paginate_queryset(self, queryset, request, view=None):
        self.count = queryset.grouped_count
        self.limit = self.get_limit(request)

        if self.limit is None:
            return None

        self.offset = self.get_offset(request)

        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return []
        
        mapping_groups = []
        self.facets = self.create_facets(queryset)
        for _, group in queryset.grouped_slice(self.offset, self.limit).items():
            mapping_groups.append(MappingsSerializer.build_mapping_group(group))
        
        return mapping_groups
    
    def get_paginated_response(self, data):
        
        if not data:
            return Response(status=status.HTTP_204_NO_CONTENT)
                
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
            ('facets', self.facets)
        ]))
