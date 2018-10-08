import pprint

from restui.models.mappings import Alignment, AlignmentRun
from restui.serializers.alignments import AlignmentSerializer, AlignmentRunSerializer

from django.http import Http404

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination

class AlignmentRunCreate(generics.CreateAPIView):
    """
    Store an AlignmentRun 
    """

    serializer_class = AlignmentRunSerializer

class AlignmentRunFetch(generics.RetrieveAPIView):
    """
    Retrieve an AlignmentRun
    """

    queryset = AlignmentRun.objects.all()
    serializer_class = AlignmentRunSerializer
    
class AlignmentCreate(generics.CreateAPIView):
    """
    Insert an Alignment
    """

    serializer_class = AlignmentSerializer

class AlignmentFetch(generics.RetrieveAPIView):
    """
    Retrieve an Alignment
    """

    queryset = Alignment.objects.all()
    serializer_class = AlignmentSerializer

class AlignmentByAlignmentRunFetch(generics.ListAPIView):
    """
    Retrieve all alignments for a given alignment run
    """

    serializer_class = AlignmentSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        try:
            alignment_run = AlignmentRun.objects.get(pk=self.kwargs["pk"])
        except (AlignmentRun.DoesNotExist, IndexError):
            raise Http404

        return Alignment.objects.filter(alignment_run=alignment_run)

#
# TODO
#
# We should probably filter to those whose mapping has been completed
# (i.e. MAPPING_COMPLETE in release_mapping_history)
#
class LatestAlignmentsFetch(generics.ListAPIView):
    """
    Retrieve either perfect or blast latest alignments for a given assembly
    """

    serializer_class = AlignmentSerializer
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        assembly_accession = self.kwargs["assembly_accession"]

        # alignment type must be either 'identity' or 'perfect_match', default to latter
        alignment_type = self.request.query_params.get('type', 'perfect_match')
        if not alignment_type in ('identity', 'perfect_match'):
            raise Http404('Invalid alignment type')

        try:
            alignment_run = AlignmentRun.objects.filter(release_mapping_history__ensembl_species_history__assembly_accession__iexact=assembly_accession,
                                                        score1_type=alignment_type).order_by('-time_run')[0]
        except (AlignmentRun.DoesNotExist, IndexError):
            raise Http404
        
        return Alignment.objects.filter(alignment_run=alignment_run)
    
