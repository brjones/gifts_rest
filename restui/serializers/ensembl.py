from celery.result import ResultBase

from django.utils import timezone
from django.core.serializers import serialize
from rest_framework import serializers


from restui.tasks import bulk_upload_task
from restui.models.ensembl import EnsemblTranscript, EnsemblSpeciesHistory, EnspUCigar

class EnsemblTranscriptSerializer(serializers.Serializer):
    """
    Deserialise transcripts specified in genes
    ensembl/load/<species>/<assembly_accession>/<ensembl_tax_id>/<ensembl_release> endpoint
    """

    #
    # NOTE
    #
    # - cannot use ModelSerializer, doesn't work with bulk_insert
    #   must explicity specify serialization fields
    # - use null default values so if the client doesn't provide some values
    #   the defaults override the existing field (otherwise the existing
    #   value won't be replaced)
    #
    transcript_id = serializers.IntegerField(required=False)
    gene = serializers.PrimaryKeyRelatedField(read_only=True)
    enst_id = serializers.CharField(max_length=30)
    enst_version = serializers.IntegerField(required=False, default=None)
    ccds_id = serializers.CharField(max_length=30, required=False, default=None)
    uniparc_accession = serializers.CharField(max_length=30, required=False, default=None)
    biotype = serializers.CharField(max_length=40, required=False, default=None)
    deleted = serializers.NullBooleanField(required=False, default=None)
    seq_region_start = serializers.IntegerField(required=False, default=None)
    seq_region_end = serializers.IntegerField(required=False, default=None)
    supporting_evidence = serializers.CharField(max_length=45, required=False, default=None)
    userstamp = serializers.CharField(max_length=30, required=False, default=None)
    time_loaded = serializers.DateTimeField(required=False)
    select = serializers.NullBooleanField(required=False, default=None)
    ensp_id = serializers.CharField(max_length=30, required=False, default=None)
    ensp_len = serializers.IntegerField(required=False, default=None)
    source = serializers.CharField(max_length=30, required=False, default=None)

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
        # data necessary to create new load record, i.e. species history
        history_attrs = { k:v for (k,v) in self.context['view'].kwargs.items()
                          if k in ('species', 'assembly_accession', 'ensembl_tax_id', 'ensembl_release') }
        
        result = bulk_upload_task.delay(history = history_attrs, data = validated_data)

        return ( result.get(),result.status )


class EnsemblGeneSerializer(serializers.Serializer):
    gene_id = serializers.IntegerField(required=False)
    ensg_id = serializers.CharField(max_length=30, required=False)
    gene_name = serializers.CharField(max_length=255, required=False, default=None)
    chromosome = serializers.CharField(max_length=50, required=False, default=None)
    region_accession = serializers.CharField(max_length=50, required=False, default=None)
    mod_id = serializers.CharField(max_length=30, required=False, default=None)
    deleted = serializers.NullBooleanField(required=False, default=None)
    seq_region_start = serializers.IntegerField(required=False, default=None)
    seq_region_end = serializers.IntegerField(required=False, default=None)
    seq_region_strand = serializers.IntegerField(required=False, default=None)
    biotype = serializers.CharField(max_length=40, required=False, default=None)
    time_loaded = serializers.DateTimeField(required=False, default=None)
    gene_symbol = serializers.CharField(max_length=30, required=False, default=None)
    gene_accession = serializers.CharField(max_length=30, required=False, default=None)
    source = serializers.CharField(max_length=30, required=False, default=None)

    # this is necessary to allow incoming genes data to have a nested list of transcripts
    # assume payload always contains non-empty transcripts data for each gene (no default value)
    transcripts = EnsemblTranscriptSerializer(many=True, required=False)

    #
    # TODO? object-level validation
    # http://www.django-rest-framework.org/api-guide/serializers/#validation
    #
    def validate(self, data):
        """
        Check various Gene fields
        """
        return data

    class Meta:
        list_serializer_class = EnsemblGeneListSerializer

class EnspUCigarSerializer(serializers.ModelSerializer):
    """
    Serializer for protein alignment instances
    """

    class Meta:
        model = EnspUCigar
        fields = '__all__'

class EnsemblReleaseSerializer(serializers.Serializer):
    """
    To serialize the latest Ensembl release whose load is complete
    """

    release = serializers.IntegerField(min_value=1, required=True)

class SpeciesHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = EnsemblSpeciesHistory
        fields = '__all__'

class TranscriptSerializer(serializers.ModelSerializer):

    class Meta:
        model = EnsemblTranscript
        fields = '__all__'
