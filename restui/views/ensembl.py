from restui.models.ensembl import EnsemblGene, EnsemblTranscript, EnspUCigar, EnsemblSpeciesHistory
from restui.serializers.ensembl import EnsemblGeneSerializer, EnspUCigarSerializer, EnsemblReleaseSerializer, SpeciesHistorySerializer, TranscriptSerializer
from restui.lib.external import ensembl_sequence

from django.http import Http404
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

import pprint

class EnsemblFeature(mixins.CreateModelMixin,
                     generics.GenericAPIView):

    serializer_class = EnsemblGeneSerializer

    def get_serializer(self, *args, **kwargs):
        # method should have been passed request.data as 'data' keyword argument
        assert "data" in kwargs, (
            "data not present"
        )
        # data should come as a list of feature-like items
        assert isinstance(kwargs["data"], list), (
            "data is not a list"
        )

        # when a serializer is instantiated and many=True is passed,
        # a ListSerializer instance will be created. The serializer
        # class then becomes a child of the parent ListSerializer
        kwargs["many"] = True

        return super(EnsemblFeature, self).get_serializer(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        # this calls self.perform_create(self.get_serializer)
        objs = self.create(request, *args, **kwargs)
        return objs

class EnspUCigarAlignmnent(APIView):
    """
    Retrieve a protein alignment and return the pairwise alignment strings.
    """

    def get(self, request, pk):
        protein_alignment = get_object_or_404(EnspUCigar, pk=pk)

class EnspUCigarCreate(generics.CreateAPIView):
    """
    Insert an alignment
    """

    serializer_class = EnspUCigarSerializer

class EnspUCigarFetch(generics.RetrieveAPIView):
    """
    Retrieve a protein alignment for an alignment run by uniprot acc/seq version and transcript id.
    """

    serializer_class = EnspUCigarSerializer

    def get_object(self):
        try:
            obj = EnspUCigar.objects.get(alignment__alignment_run=self.kwargs['run'],
                                         alignment__mapping__uniprot__uniprot_acc=self.kwargs['acc'],
                                         alignment__mapping__uniprot__sequence_version=self.kwargs['seq_version'],
                                         alignment__transcript__enst_id=self.kwargs['enst_id'])
        except:
            raise Http404

        # may raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

class LatestEnsemblRelease(APIView):
    """
    Fetch the latest Ensembl release whose load is complete.
    """

    def get(self, request, assembly_accession):
        try:
            species_history = EnsemblSpeciesHistory.objects.filter(assembly_accession__iexact=assembly_accession,
                                                                   status='LOAD_COMPLETE').latest('ensembl_release')
        except (EnsemblSpeciesHistory.DoesNotExist, IndexError):
            raise Http404

        serializer = EnsemblReleaseSerializer({ 'release': species_history.ensembl_release })
        return Response(serializer.data)

class SpeciesHistory(generics.RetrieveAPIView):
    """
    Retrieve an Ensembl Species History by id.
    """

    queryset = EnsemblSpeciesHistory.objects.all()
    serializer_class = SpeciesHistorySerializer

class Transcript(generics.RetrieveAPIView):
    """
    Retrieve transcript instance by id.
    """

    queryset = EnsemblTranscript.objects.all()
    serializer_class = TranscriptSerializer
