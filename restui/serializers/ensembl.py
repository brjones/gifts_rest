from rest_framework import serializers
from django.core.serializers import serialize
from restui.models.ensembl import EnsemblGene, EnsemblTranscript
from psqlextra.query import ConflictAction
from itertools import chain # flatten list of lists, i.e. list of transcripts for each gene
import pprint

#
# NOTES
#
# Can we use ModelSerializer? Doesn't seem to work with bulk_insert
#

class EnsemblTranscriptSerializer(serializers.Serializer):
    transcript_id = serializers.IntegerField(required=False)
    enst_id = serializers.CharField(max_length=30)

    # class Meta:
    #     model = EnsemblTranscript
    #     fields = '__all__'

#
# Customizing ListSerializer behavior
#
# From http://www.django-rest-framework.org/api-guide/serializers/#listserializer

# There are a few use cases when you might want to customize the ListSerializer behavior. For example:
# You want to provide particular validation of the lists, such as checking that one element does not conflict with another element in a list.
# You want to customize the create or update behavior of multiple objects.
# For these cases you can modify the class that is used when many=True is passed, by using the list_serializer_class option on the serializer Meta class.

class EnsemblGeneListSerializer(serializers.ListSerializer):

    # The default implementation for multiple object creation is to simply call .create() for each item in the list
    # Override using the bulk_insert behaviour from postgres-extra to allow fast insertion and return obj IDs so that
    # we can recursively insert gene transcripts
    def create(self, validated_data):
        # incoming data has list of transcripts nested into each gene
        # map each ensg ID to the list of its transcripts, so that we can later
        # assign the gene to each transcript for the transcript bulk insert
        gdata = []
        tdata = {}
        for item in validated_data:
            # need to remove (i.e. pop) 'transcripts' from data as this is not part of the gene model
            tdata[item.get('ensg_id')] = item.pop('transcripts')
            gdata.append(dict(**item))

        #
        # bulk insert the genes
        #
        # WARNING
        #
        # From http://django-postgres-extra.readthedocs.io/manager/
        # In order to stick to the "everything in one query" principle, various, more advanced usages of bulk_insert are impossible.
        # It is not possible to have different rows specify different amounts of columns.
        #
        genes = EnsemblGene.objects.on_conflict(['ensg_id'], ConflictAction.UPDATE).bulk_insert(gdata, return_model=True)

        # map each transcript data to its corresponding gene object,
        # effectively establishing the gene-transcript one-to-many relationship
        map(lambda t, g: t.extend({"gene": gene}), ((transcript_data, gene) for gene in genes for transcript_data in tdata[gene.ensg_id]))
        
        # bulk insert the transcripts mapped to their genes
        transcripts = EnsemblTranscript.objects.on_conflict(['enst_id'],
                                                            ConflictAction.UPDATE).bulk_insert(list(chain.from_iterable(tdata.values())),
                                                                                               return_model=True)
        return genes

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
    # history = PrimaryKeyRelatedField(many=True, read_only=True)

    # this is necessary to allow incoming genes data to have a nested list of transcripts
    transcripts = EnsemblTranscriptSerializer(many=True, required=False)

    #
    # TODO
    # object-level validation
    # http://www.django-rest-framework.org/api-guide/serializers/#validation
    #
    def validate(self, data):
        """
        Check various Gene fields
        """
        return data

    class Meta:
        # model = EnsemblGene
        # fields = '__all__'
        list_serializer_class = EnsemblGeneListSerializer
