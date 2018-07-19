from restui.models.ensembl import EnsemblGene
from restui.serializers.ensembl import EnsemblGeneSerializer

from django.shortcuts import render
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from rest_framework.response import Response

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
