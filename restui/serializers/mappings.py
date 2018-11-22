from rest_framework import serializers
from django.http import Http404

from restui.lib.external import ensembl_sequence
from restui.models.annotations import CvEntryType, CvUeStatus
from restui.models.mappings import Mapping, ReleaseMappingHistory, MappingHistory, ReleaseStats
from restui.serializers.ensembl import SpeciesHistorySerializer
from restui.serializers.annotations import StatusSerializer, StatusHistorySerializer

class TaxonomySerializer(serializers.Serializer):
    """
    For nested serialization of taxonomy in call to mapping/<id> endpoint.
    """

    species = serializers.CharField()
    ensemblTaxId = serializers.IntegerField()
    uniprotTaxId = serializers.IntegerField()

class UniprotEntryMappingSerializer(serializers.Serializer):
    uniprotAccession = serializers.CharField()
    entryType = serializers.CharField()
    sequenceVersion = serializers.IntegerField()
    upi = serializers.CharField()
    md5 = serializers.CharField()
    isCanonical = serializers.NullBooleanField()
    alias = serializers.CharField()
    ensemblDerived = serializers.NullBooleanField()
    gene_symbol = serializers.CharField()
    gene_accession = serializers.CharField()
    length = serializers.IntegerField()

class EnsemblTranscriptMappingSerializer(serializers.Serializer):
    enstId = serializers.CharField()
    enstVersion = serializers.IntegerField()
    upi = serializers.CharField()
    biotype = serializers.CharField()
    deleted = serializers.NullBooleanField()
    chromosome = serializers.CharField()
    regionAccession = serializers.CharField()
    seqRegionStart = serializers.IntegerField()
    seqRegionEnd = serializers.IntegerField()
    seqRegionStrand = serializers.IntegerField()
    ensgId = serializers.CharField()
    ensgName = serializers.CharField()
    sequence = serializers.CharField(required=False)
    ensgSymbol = serializers.CharField()
    ensgAccession = serializers.CharField()
    ensgRegionAccession = serializers.CharField()
    enspId = serializers.CharField()
    enspLen = serializers.IntegerField()
    select = serializers.NullBooleanField()
    
class EnsemblUniprotMappingSerializer(serializers.Serializer):
    """
    For nested serialization of Ensembl-Uniprot mapping in call to mapping/<id> endpoint.
    """

    mappingId = serializers.IntegerField()
    timeMapped = serializers.DateTimeField()
    uniprotRelease = serializers.CharField()
    ensemblRelease = serializers.CharField()
    uniprotEntry = UniprotEntryMappingSerializer()
    ensemblTranscript = EnsemblTranscriptMappingSerializer()
    alignment_difference = serializers.IntegerField()
    status = serializers.CharField()
    status_history = StatusHistorySerializer(many=True)


class RelatedEntriesSerializer(serializers.Serializer):
    """
    For nested serialization of mapped/unmapped mapping releated entries
    """

    mapped = EnsemblUniprotMappingSerializer(many=True)
    unmapped = UniprotEntryMappingSerializer(many=True)

class MappingSerializer(serializers.Serializer):
    """
    Serialize data in call to mapping/:id endpoint.

    JSON specs derived from:
    https://github.com/ebi-uniprot/gifts-mock/blob/master/data/mapping.json
    """
    
    taxonomy = TaxonomySerializer()
    mapping = EnsemblUniprotMappingSerializer()
    relatedEntries = RelatedEntriesSerializer()

class MappingHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for MappingHistory instances
    """

    class Meta:
        model = MappingHistory
        fields = '__all__'

class ReleaseMappingHistorySerializer(serializers.ModelSerializer):
    """
    Serializers for ReleaseMappingHistory instances, includes nested ensembl species history
    """
    # mapping_history = MappingHistorySerializer(many=True)
    ensembl_species_history = SpeciesHistorySerializer()

    class Meta:
        model = ReleaseMappingHistory
        fields = '__all__'

class MappingByHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for mappings returned by the mappings/release_history/<id> endpoint.
    """

    mapping_history = MappingHistorySerializer(many=True)

    class Meta:
        model = Mapping
        fields = '__all__'

class MappingsSerializer(serializers.Serializer):
    """
    Serialize data in call to mappings/ endpoint
    """

    taxonomy = TaxonomySerializer()
    entryMappings = EnsemblUniprotMappingSerializer(many=True)

    @classmethod
    def build_mapping(cls, mapping, fetch_sequence=False, authenticated=False): 
        mapping_history = mapping.mapping_history.select_related('release_mapping_history').select_related('release_mapping_history__ensembl_species_history').latest('mapping_history_id')
        release_mapping_history = mapping_history.release_mapping_history
        ensembl_history = mapping_history.release_mapping_history.ensembl_species_history
        
        status = mapping.status.id

        sequence = None
        if fetch_sequence:
            try:
                sequence = ensembl_sequence(mapping.transcript.enst_id, ensembl_history.ensembl_release)
            except Exception as e:
                print(e) # TODO: log
                sequence = None
        
        mapping_obj = { 'mappingId':mapping.mapping_id,
                        'timeMapped':release_mapping_history.time_mapped,
                        'ensemblRelease':ensembl_history.ensembl_release,
                        'uniprotRelease':release_mapping_history.uniprot_release,
                        'uniprotEntry': {
                            'uniprotAccession':mapping.uniprot.uniprot_acc,
                            'entryType':Mapping.entry_type(mapping_history.entry_type_id), 
                            'sequenceVersion':mapping.uniprot.sequence_version,
                            'upi':mapping.uniprot.upi,
                            'md5':mapping.uniprot.md5,
                            'isCanonical': False if mapping.uniprot.canonical_uniprot_id else True,
                            'alias': mapping.uniprot.alias,
                            'ensemblDerived':mapping.uniprot.ensembl_derived,
                            'gene_symbol':mapping.uniprot.gene_symbol,
                            'gene_accession':mapping.uniprot.chromosome_line,
                            'length':mapping.uniprot.length
                            },
                        'ensemblTranscript': {
                            'enstId':mapping.transcript.enst_id,
                            'enstVersion':mapping.transcript.enst_version,
                            'upi':mapping.transcript.uniparc_accession,
                            'biotype':mapping.transcript.biotype,
                            'deleted':mapping.transcript.deleted,
                            'chromosome':mapping.transcript.gene.chromosome,
                            'regionAccession':mapping.transcript.gene.region_accession,
                            'seqRegionStart':mapping.transcript.seq_region_start,
                            'seqRegionEnd':mapping.transcript.seq_region_end,
                            'seqRegionStrand': mapping.transcript.gene.seq_region_strand,
                            'ensgId':mapping.transcript.gene.ensg_id,
                            'ensgName':mapping.transcript.gene.gene_name,
                            'ensgSymbol':mapping.transcript.gene.gene_symbol,
                            'ensgAccession':mapping.transcript.gene.gene_accession,
                            'ensgRegionAccession':mapping.transcript.gene.region_accession,
                            'sequence':sequence,
                            'enspId':mapping.transcript.ensp_id,
                            'enspLen':mapping.transcript.ensp_len,
                            'select':mapping.transcript.select
                            },
                       'alignment_difference': mapping.alignment_difference,
                       'status': Mapping.status_type(status),
                       'status_history': mapping.statuses(usernames=authenticated)
                       }

        return mapping_obj

    @classmethod
    def build_mapping_group(cls, mappings_group, fetch_sequence=False):
        mapping_set = dict() 
        try:
            mapping_set['taxonomy'] = cls.build_taxonomy_data(mappings_group[0])
        except Exception as e:
            ###log
            print(e)
            raise Http404("Couldn't create taxonomy element for mapping object {}".format(mappings_group[0].mapping_id))
    
        mapping_set['entryMappings'] = []
        
        for mapping in mappings_group:
            mapping_set['entryMappings'].append(cls.build_mapping(mapping, fetch_sequence=fetch_sequence))

        return mapping_set
    
    @classmethod
    def build_taxonomy_data(cls, mapping):
        # Find the ensembl tax id via one ensembl species history associated to transcript
        # associated to the given mapping.
        # Relationship between transcript and history is many to many but we just fetch one history
        # as the tax id remains the same across all of them
        try:
            ensembl_history = mapping.mapping_history.select_related('release_mapping_history').select_related('release_mapping_history__ensembl_species_history').latest('mapping_history_id').release_mapping_history.ensembl_species_history
#            ensembl_history = mapping.transcript.history.latest('ensembl_release')
            uniprot_tax_id = mapping.uniprot.uniprot_tax_id
        except Exception as e:
            ###log
            print(e)
            raise Http404("Couldn't find an ensembl species history associated to mapping {}".format(mapping.mapping_id))
        
        try:
            return { 'species':ensembl_history.species,
                     'ensemblTaxId':ensembl_history.ensembl_tax_id,
                     'uniprotTaxId':uniprot_tax_id }
        except:
            raise Http404("Couldn't find uniprot tax id as I couldn't find a uniprot entry associated to the mapping")

class LabelSerializer(serializers.Serializer):
    """
    Serializer for an individual label
    """
    label = serializers.CharField()
    id = serializers.IntegerField()
    status = serializers.BooleanField()

class MappingLabelsSerializer(serializers.Serializer):
    """
    For nested serialization of user label for a mapping in call to labels/<mapping_id> endpoint.
    """
    labels = LabelSerializer(many=True)
    
class CommentLabelSerializer(serializers.Serializer):
    """
    For nested serialization of user comment for a mapping in call to comments/<mapping_id> endpoint.
    """

    text = serializers.CharField()
    timeAdded = serializers.DateTimeField()
    user = serializers.CharField()
    
class MappingCommentsSerializer(serializers.Serializer):
    """
    Serialize data in call to comments/<mapping_id> endpoint.

    JSON specs derived from https://github.com/ebi-uniprot/gifts-mock/blob/master/data/comments.json
    """

    mappingId = serializers.IntegerField()
    comments = CommentLabelSerializer(many=True)

class MappingPairwiseAlignmentSerializer(serializers.Serializer):
    """
    For a nested pairwise alignment object
    """
    uniprot_alignment = serializers.CharField()
    ensembl_alignment = serializers.CharField()
    match_str = serializers.CharField()
    alignment_id = serializers.IntegerField()
    alignment_type = serializers.CharField()
    ensembl_release = serializers.IntegerField()
    ensembl_id = serializers.CharField()
    uniprot_id = serializers.CharField()
    
class MappingAlignmentsSerializer(serializers.Serializer):
    """
    Serializer for pairwise alignment sets
    """
    mapping_id = serializers.IntegerField()
    alignments = MappingPairwiseAlignmentSerializer(many=True)

class UniprotMappedCountSerializer(serializers.Serializer):
    """
    Serializer for counts related to mapped/unmapped Uniprot entries
    """

    mapped = serializers.IntegerField()
    not_mapped_sp = serializers.IntegerField()

class EnsemblMappedCountSerializer(serializers.Serializer):
    """
    Serializer for counts related to mapped/unmapped gene/transcript entries
    """

    gene_mapped = serializers.IntegerField()
    gene_not_mapped_sp = serializers.IntegerField()
    transcript_mapped = serializers.IntegerField()

class MappingCountSerializer(serializers.Serializer):
    """
    Serializer for general and specific mapping counts
    """

    total = serializers.IntegerField()
    uniprot = UniprotMappedCountSerializer()
    ensembl = EnsemblMappedCountSerializer()

class StatusCountSerializer(serializers.Serializer):
    """
    Serializer for an individual status' count
    """
    status = serializers.CharField()
    count = serializers.IntegerField()

class LabelCountSerializer(serializers.Serializer):
    """
    Serializer for an individual label's count
    """
    label = serializers.CharField()
    count = serializers.IntegerField()

class ReleaseStatsSerializer(serializers.ModelSerializer):
    """
    Serializer for ReleaseStats instances
    """

    class Meta:
        model = ReleaseStats
        fields = '__all__'

class UnmappedSwissprotEntrySerializer(serializers.Serializer):
    """
    Serializer for unmapped Swissprot entries /mappings/unmapped/<taxid>/swissprot endpoint.
    """

    uniprotAccession = serializers.CharField()
    entryType = serializers.CharField()
    isCanonical = serializers.NullBooleanField()
    alias = serializers.CharField()

class UnmappedEnsemblGeneSerializer(serializers.Serializer):
    ensgId = serializers.CharField()
    ensgName = serializers.CharField()
    chromosome = serializers.CharField()
    regionAccession = serializers.CharField()
    seqRegionStart = serializers.IntegerField()
    seqRegionEnd = serializers.IntegerField()
    seqRegionStrand = serializers.IntegerField()
    
class UnmappedEnsemblEntrySerializer(serializers.Serializer):
    """
    Serializer for unmapped ensembl entries /mappings/unmapped/<taxid>/ensembl endpoint.
    """

    gene = UnmappedEnsemblGeneSerializer()
    transcripts = serializers.ListField(child=serializers.CharField())

    @classmethod
    def build_group(cls, ensg_id, group):
        gene = group[0].gene

        return { 'gene':{ 'ensgId':gene.ensg_id,
	                  'ensgName':gene.gene_name,
	                  'chromosome':gene.chromosome,
                          'regionAccession':gene.region_accession,
	                  'seqRegionStart':gene.seq_region_start,
	                  'seqRegionEnd':gene.seq_region_end,
	                  'seqRegionStrand':gene.seq_region_strand },
                 'transcripts':[ t.enst_id for t in group ] }

class ReleasePerSpeciesSerializer(serializers.Serializer):
    """
    Serializer for ensembl/uniprot release numbers /mappings/release/<taxid>/ endpoint
    """

    ensembl = serializers.IntegerField()
    uniprot = serializers.CharField()
