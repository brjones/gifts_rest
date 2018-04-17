from rest_framework import serializers
from django.core.serializers import serialize
from restui.models.ensembl import EnsemblGene
from psqlextra.query import ConflictAction
import pprint

class EnsemblGeneListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        genes = [dict(**item) for item in validated_data]
        pprint.pprint(genes)
#        genes = [EnsemblGene(**item) for item in validated_data]
#        objs = EnsemblGene.objects.on_conflict(['ensg_id'], ConflictAction.UPDATE).bulk_create(genes)
        objs = EnsemblGene.objects.on_conflict(['ensg_id'], ConflictAction.UPDATE).bulk_insert(genes, return_model=True)
        pprint.pprint(objs)
        return objs

class EnsemblGeneSerializer(serializers.Serializer):
    gene_id = serializers.IntegerField(required=False)
    ensg_id = serializers.CharField(max_length=30)
    gene_name = serializers.CharField(max_length=30)
    chromosome = serializers.CharField(max_length=50, required=False)
    region_accession = serializers.CharField(max_length=50, required=False)
    mod_id = serializers.CharField(max_length=30, required=False)
    deleted = serializers.NullBooleanField(required=False)
    seq_region_start = serializers.IntegerField(required=False)
    seq_region_end = serializers.IntegerField(required=False)
    seq_region_strand = serializers.IntegerField(required=False)
    biotype = serializers.CharField(max_length=40, required=False)
    time_loaded = serializers.DateTimeField(required=False)

    class Meta:
        list_serializer_class = EnsemblGeneListSerializer
