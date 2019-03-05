import pprint
from itertools import chain # flatten list of lists, i.e. list of transcripts for each gene

from django.utils import timezone
from django.core.serializers import serialize
from rest_framework import serializers
from psqlextra.query import ConflictAction

from restui.models.ensembl import EnsemblGene, EnsemblTranscript, EnsemblSpeciesHistory, GeneHistory, TranscriptHistory, EnspUCigar


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
        #
        # create new species history, use required parameters passed to view from endpoint URL
        #
        # NOTE: filter is likely to be not necessary
        #
        history_attrs = { k:v for (k,v) in self.context['view'].kwargs.items()
                          if k in ('species', 'assembly_accession', 'ensembl_tax_id', 'ensembl_release') }
        history_attrs['status'] = 'LOAD_STARTED' # temporary status
        history = EnsemblSpeciesHistory.objects.create(**history_attrs)

        #
        # transform incoming data for genes/transcripts in a way suitable for bulk insertion
        #
        # assume incoming data has list of transcripts nested into each gene
        # map each ensg ID to the list of its transcripts, so that we can later
        # assign the gene to each transcript for the transcripts bulk insert
        gdata = []
        tdata = {}
        timestamp = timezone.now()

        for item in validated_data:
            item['time_loaded'] = timestamp # add timestamp to gene

            ensg_id = item.get('ensg_id')

            # need to remove 'transcripts' from data as this is not part of the gene model
            #
            # NOTE: assume payload always contains non-empty transcripts data for each gene
            #
            tdata[ensg_id] = item.pop('transcripts')

            # add timestamp to gene's transcripts too
            for t in tdata[ensg_id]:
                t['time_loaded'] = timestamp

            gdata.append(dict(**item))

        #
        # bulk insert the genes and transcripts
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
        # use generator expression to reduce memory footprint
        for t, g in ( (transcript_data, gene) for gene in genes for transcript_data in tdata[gene.ensg_id] ):
            t["gene"] = g
        
        # bulk insert the transcripts mapped to their genes
        transcripts = EnsemblTranscript.objects.on_conflict(['enst_id'],
                                                            ConflictAction.UPDATE).bulk_insert(list(chain.from_iterable(tdata.values())),
                                                                                               return_model=True)
        #
        # insert genes and trascripts histories
        #
        # TODO: optimise, bulk_insert again?!
        #
        # UPDATE: tried bulk_insert, but receive a strange error:
        #         'column "ensembl_species_history" does not exist'
        #         HINT:  Perhaps you meant to reference the column "gene_history.ensembl_species_history_id"
        #                or the column "excluded.ensembl_species_history_id".
        #
        # GeneHistory.objects.on_conflict(['ensembl_species_history', 'gene'],
        #                                ConflictAction.UPDATE).bulk_insert([ dict(ensembl_species_history=history, gene=g) for g in genes ])
        #
        for gene in genes:
            GeneHistory.objects.create(ensembl_species_history=history, gene=gene)
        for transcript in transcripts:
            TranscriptHistory.objects.create(ensembl_species_history=history, transcript=transcript)

        history.time_loaded = timezone.now() # WARNING: this generates datetime with microseconds and no UTC
        history.status = 'LOAD_COMPLETE'
        history.save()
        
        return genes

class EnsemblGeneSerializer(serializers.Serializer):
    gene_id = serializers.IntegerField(required=False)
    ensg_id = serializers.CharField(max_length=30)
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
