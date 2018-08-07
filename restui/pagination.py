from collections import OrderedDict
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from restui.serializers.mappings import MappingsSerializer
#
# TODO
#
# sequence and mappings facets
#
class FacetPagination(LimitOffsetPagination):
    def create_facets(self, queryset):
        statuses = OrderedDict([('name','status'),('label','Status'),('items',[])])
        organism = OrderedDict([('name','organism'),('label','Organism'),('items',[])])
        #######
        # TODO
        sequence = OrderedDict([('name','sequence'),('label','Sequence'),('items',[])])
        mappings = OrderedDict([('name','mappings'),('label','Type'),('items',[])])
        #######

        for species in queryset.species():
            organism["items"].append({ "name":species[0], "label":species[1] })
    
        for status in queryset.statuses():
            statuses["items"].append({ "name":status, "label":status.replace("_"," ").capitalize() })
            
        return [ statuses, organism, sequence, mappings ]

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
        
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
            ('facets', self.facets)
        ]))
