from django.http import Http404
from rest_framework import serializers
from restui.models.ensembl import EnsemblSpeciesHistory
from restui.models.mappings import ReleaseMappingHistory
import re


class EnsemblFlagSerializer(serializers.Serializer):
    load_status = serializers.BooleanField()
    aligment_status = serializers.BooleanField()

    def to_representation(self, instance):
        load_status = EnsemblSpeciesHistory.objects.filter(ensembl_release=str(instance))
        if not load_status:
            raise Http404()
        flag_load = all([re.match('.*_COMPLETE', e.status) if e.status is not None else False for e in load_status])
        flag_alignment = all(
            [re.match('.*_COMPLETE', e.alignment_status) if e.alignment_status is not None else False for e in
             load_status])
        repr = {
            'load_status': flag_load,
            'aligment_status': flag_alignment,
        }
        return super().to_representation(repr)


class UniprotFlagSerializer(serializers.Serializer):

    mapping_status = serializers.BooleanField()

    def to_representation(self, instance):
        print(instance)
        load_status = ReleaseMappingHistory.objects.filter(uniprot_release=str(instance))
        if not load_status:
            raise Http404()
        flag_mapping = all([re.match('.*_COMPLETE', e.status) if e.status is not None else False for e in load_status])
        repr = {
            'mapping_status': flag_mapping
        }
        return super().to_representation(repr)
