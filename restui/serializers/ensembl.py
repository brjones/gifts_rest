import pprint
from itertools import chain # flatten list of lists, i.e. list of transcripts for each gene

from django.utils import timezone
from django.core.serializers import serialize
from rest_framework import serializers
from psqlextra.query import ConflictAction

from restui.models.ensembl import EnsemblGene, EnsemblTranscript, EnsemblSpeciesHistory, GeneHistory, TranscriptHistory, EnspUCigar


#
# NOTE: cannot use ModelSerializer, doesn't work with bulk_insert
#
class EnsemblTranscriptSerializer(serializers.Serializer):
    transcript_id = serializers.IntegerField(required=False)
    gene = serializers.PrimaryKeyRelatedField(read_only=True)
    enst_id = serializers.CharField(max_length=30)
    enst_version = serializers.IntegerField(required=False)
    ccds_id = serializers.CharField(max_length=30, required=False)
    uniparc_accession = serializers.CharField(max_length=30, required=False)
    biotype = serializers.CharField(max_length=40, required=False)
    deleted = serializers.NullBooleanField(required=False)
    seq_region_start = serializers.IntegerField(required=False)
    seq_region_end = serializers.IntegerField(required=False)
    supporting_evidence = serializers.CharField(max_length=45, required=False)
    userstamp = serializers.CharField(max_length=30, required=False)
    time_loaded = serializers.DateTimeField(required=False)
    select = serializers.NullBooleanField(required=False)
    ensp_id = serializers.CharField(max_length=30, required=False)
    ensp_len = serializers.IntegerField(required=False)
    source = serializers.CharField(max_length=30, required=False)

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

            # need to remove (i.e. pop) 'transcripts' from data as this is not part of the gene model
            tdata[item.get('ensg_id')] = item.pop('transcripts')

            for t in tdata[item.get('ensg_id')]: # add timestamp to gene's transcripts
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
        for t, g in ((transcript_data, gene) for gene in genes for transcript_data in tdata[gene.ensg_id]):
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
    gene_symbol = serializers.CharField(max_length=30, required=False)
    gene_accession = serializers.CharField(max_length=30, required=False)
    source = serializers.CharField(max_length=30, required=False)

    # this is necessary to allow incoming genes data to have a nested list of transcripts
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
