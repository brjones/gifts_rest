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
from rest_framework.schemas import ManualSchema

import coreapi, coreschema

class EnsemblFeature(mixins.CreateModelMixin,
                     generics.GenericAPIView):

    serializer_class = EnsemblGeneSerializer
    schema = ManualSchema(description="Bulk load/update of genes and their transcript from an Ensembl release",
                          fields=[
                              coreapi.Field(
                                  name="species",
                                  required=True,
                                  location="path",
                                  schema=coreschema.String(),
                                  description="Species scientific name"
                              ),
                              coreapi.Field(
                                  name="assembly_accession",
                                  required=True,
                                  location="path",
                                  schema=coreschema.String(),
                                  description="Assembly accession"
                              ),
                              coreapi.Field(
                                  name="ensembl_tax_id",
                                  required=True,
                                  location="path",
                                  schema=coreschema.Integer(),
                                  description="Species taxonomy id"
                              ),
                              coreapi.Field(
                                  name="ensembl_release",
                                  required=True,
                                  location="path",
                                  schema=coreschema.Integer(),
                                  description="Ensembl release number"
                              ),
                          ])

    def get_serializer(self, *args, **kwargs):
        # method should have been passed request.data as 'data' keyword argument
        # assert "data" in kwargs, (
        #     "data not present"
        # )
        # # data should come as a list of feature-like items
        # assert isinstance(kwargs["data"], list), (
        #     "data is not a list"
        # )

        # when a serializer is instantiated and many=True is passed,
        # a ListSerializer instance will be created. The serializer
        # class then becomes a child of the parent ListSerializer
        kwargs["many"] = True

        return super(EnsemblFeature, self).get_serializer(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        # this calls self.perform_create(self.get_serializer)
        objs = self.create(request, *args, **kwargs)

        return Response({'success':1}, status=status.HTTP_201_CREATED)

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
    schema = ManualSchema(description="Retrieve a protein alignment for an alignment run by uniprot acc/seq version and transcript id",
                          fields=[
                              coreapi.Field(
                                  name="run",
                                  required=True,
                                  location="path",
                                  schema=coreschema.Integer(),
                                  description="Alignmet run id"
                              ),
                              coreapi.Field(
                                  name="acc",
                                  required=True,
                                  location="path",
                                  schema=coreschema.Integer(),
                                  description="Uniprot accession"
                              ),
                              coreapi.Field(
                                  name="seq_version",
                                  required=True,
                                  location="path",
                                  schema=coreschema.Integer(),
                                  description="Sequence version"
                              ),
                              coreapi.Field(
                                  name="enst_id",
                                  required=True,
                                  location="path",
                                  schema=coreschema.Integer(),
                                  description="Ensembl transcript ID"
                              ),
                          ])

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

class EnspUCigarFetchUpdateByAlignment(generics.RetrieveUpdateAPIView):
    """
    Fetch/Update cigar/mdz by alignment id
    """

    serializer_class = EnspUCigarSerializer
    schema = ManualSchema(description="Fetch/Update cigar/mdz by alignment id",
                          fields=[
                              coreapi.Field(
                                  name="id",
                                  required=True,
                                  location="path",
                                  schema=coreschema.Integer(),
                                  description="Alignmet id"
                              ),
                          ])

    def get_object(self):
        try:
            obj = EnspUCigar.objects.get(alignment=self.kwargs['pk'])
        except:
            raise Http404

        self.check_object_permissions(self.request, obj)

        return obj

class LatestEnsemblRelease(APIView):
    """
    Fetch the latest Ensembl release whose load is complete.
    """

    schema = ManualSchema(description="Fetch the latest Ensembl release whose load is complete",
                          fields=[
                              coreapi.Field(
                                  name="assembly_accession",
                                  required=True,
                                  location="path",
                                  schema=coreschema.String(),
                                  description="Assembly accession"
                              ),])


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

class SpeciesHistoryAlignmentStatus(APIView):
    """
    Update a species history's alignment status
    """

    schema = ManualSchema(description="Update a species history's alignment status",
                          fields=[
                              coreapi.Field(
                                  name="id",
                                  required=True,
                                  location="path",
                                  schema=coreschema.Integer(),
                                  description="A unique integer value identifying the species history"
                              ),
                              coreapi.Field(
                                  name="status",
                                  required=True,
                                  location="path",
                                  schema=coreschema.Integer(),
                                  description="String representing the updated alignment status"
                              ),
                          ])

    def post(self, request, pk, status):
        try:
            history = EnsemblSpeciesHistory.objects.get(pk=pk)
        except EnsemblSpeciesHistory.DoesNotExist:
            return Response({ "error": "Could not find species history {}".format(pk) }, status=status.HTTP_400_BAD_REQUEST)
        else:
            history.alignment_status = status
            history.save()

        serializer = SpeciesHistorySerializer(history)

        return Response(serializer.data)

class Transcript(generics.RetrieveAPIView):
    """
    Retrieve transcript instance by id.
    """

    queryset = EnsemblTranscript.objects.all()
    serializer_class = TranscriptSerializer
