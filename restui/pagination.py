import pprint
from collections import OrderedDict
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from restui.serializers.mappings import MappingsSerializer, MappingViewsSerializer, UnmappedEnsemblEntrySerializer
from restui.models.mappings import Mapping, MappingView
from rest_framework import status
#
# TODO
#
# chromosome and mappings facets
#
class FacetPagination(LimitOffsetPagination):
    def create_facets(self, queryset):
        statuses = OrderedDict([('name','status'),('label','Status'),('items',[])])
        organism = OrderedDict([('name','organism'),('label','Organism'),('items',[])])
        sequence = OrderedDict([('name','divergence'),('label','Divergence'),('items',[])])

        species_set = queryset.species()
        for species in species_set:
            organism["items"].append({ "name":species[0], "label":species[1] })

        for status in queryset.statuses():
            statuses["items"].append({ "name":Mapping.status_type(status), "label":Mapping.status_type(status).replace("_"," ").capitalize() })

        differences = queryset.divergences()
        if differences[0]:
            sequence["items"].append({ "label": "identical", "name": "identical", "count": differences[0] })
        if differences[1]:
            sequence["items"].append({ "label": "small", "name": "small", "count": differences[1] })
        if differences[2]:
            sequence["items"].append({ "label": "large", "name": "large", "count": differences[2] })

        if len(species_set) == 1:
            chromosomes = OrderedDict([('name','chromosomes'),('label','Chromosomes'),('items',[])])
            
            for chromosome in queryset.chromosomes():
                chromosomes["items"].append({ 'name':chromosome.lower(), 'label':chromosome.upper() })

            return [ statuses, organism, sequence, chromosomes ]

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

class MappingViewFacetPagination(LimitOffsetPagination):
    def create_facets(self, queryset):
        statuses = OrderedDict([('name','status'),('label','Status'),('items',[])])
        organism = OrderedDict([('name','organism'),('label','Organism'),('items',[])])
        sequence = OrderedDict([('name','alignment'),('label','Alignment'),('items',[])])
        types = OrderedDict([('name','type'),('label','Type'),('items',[])])

        species_set = queryset.species()
        for species in species_set:
            organism["items"].append({ "name":species[0], "label":species[1] })

        for status in queryset.statuses():
            try:
                description = MappingView.status_description(status)
                statuses["items"].append({ "name":description, "label":description.replace("_"," ").capitalize() })
            except:
                pass

        differences = queryset.divergences()
        if differences[0]:
            sequence["items"].append({ "label": "Identical", "name": "identical", "count": differences[0] })
        if differences[1]:
            sequence["items"].append({ "label": "Small diff", "name": "small", "count": differences[1] })
        if differences[2]:
            sequence["items"].append({ "label": "Large diff", "name": "large", "count": differences[2] })

        for mapping_type in queryset.types():
            types["items"].append({ 'name':mapping_type, 'label':mapping_type.replace("_"," ").capitalize() })

        if len(species_set) == 1:
            chromosomes = OrderedDict([('name','chromosomes'),('label','Chromosomes'),('items',[])])

            for chromosome in queryset.chromosomes():
                chromosomes["items"].append({ 'name':chromosome.lower(), 'label':chromosome.upper() })

            return [ statuses, organism, sequence, chromosomes, types ]

        return [ statuses, organism, sequence, types ]


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
            mapping_groups.append(MappingViewsSerializer.build_mapping_group(group))

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

class UnmappedEnsemblEntryPagination(LimitOffsetPagination):
    """
    Paginate unmapped ensembl transcripts
    """

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

        unmapped_groups = []
        for ensg_id, group in queryset.grouped_slice(self.offset, self.limit).items():
            unmapped_groups.append( UnmappedEnsemblEntrySerializer.build_group(ensg_id, group) )

        unmapped_groups.sort(key=lambda e: e['gene']['ensgName'])

        return unmapped_groups

    def get_paginated_response(self, data):
        if not data:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
