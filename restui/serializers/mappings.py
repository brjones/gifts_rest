from rest_framework import serializers
from django.http import Http404

from restui.lib.external import ensembl_sequence
from restui.models.annotations import CvEntryType, CvUeStatus

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
    ensemblDerived = serializers.NullBooleanField()

class EnsemblTranscriptMappingSerializer(serializers.Serializer):
    enstId = serializers.CharField()
    enstVersion = serializers.IntegerField()
    upi = serializers.CharField()
    biotype = serializers.CharField()
    deleted = serializers.NullBooleanField()
    seqRegionStart = serializers.IntegerField()
    seqRegionEnd = serializers.IntegerField()
    ensgId = serializers.CharField()
    sequence = serializers.CharField(required=False)

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

class MappingSerializer(serializers.Serializer):
    """
    Serialize data in call to mapping/:id endpoint.

    JSON specs derived from:
    https://github.com/ebi-uniprot/gifts-mock/blob/master/data/mapping.json
    """
    
    taxonomy = TaxonomySerializer()
    mapping = EnsemblUniprotMappingSerializer()
    relatedMappings = EnsemblUniprotMappingSerializer(many=True)

class MappingsSerializer(serializers.Serializer):
    """
    Serialize data in call to mappings/ endpoint
    """

    taxonomy = TaxonomySerializer()
    entryMappings = EnsemblUniprotMappingSerializer(many=True)

    '''
    The goal of these two functions is to reduce the number of database calls. Rather
    than a lookup per mapping record, we'll cache these constants for the life of
    the request in the serializer class.
    '''
    _entry_type = None
    _status_type = None
    @classmethod
    def entry_type(cls, id):
        if not cls._entry_type:
            entries = {}
            for entry in CvEntryType.objects.all():
                entries[entry.id] = entry.description 
            cls._entry_type = entries
            
        return cls._entry_type[id]

    @classmethod
    def status_type(cls, id):
        if not cls._status_type:
            statuses = {}
            for status in CvUeStatus.objects.all():
                statuses[status.id] = status.description 
            cls._status_type = statuses
            
        return cls._status_type[id]

    @classmethod
    def build_mapping(cls, mapping, fetch_sequence=False):        
        mapping_history = mapping.mapping_history.select_related('release_mapping_history').select_related('release_mapping_history__ensembl_species_history').latest('mapping_history_id')
        release_mapping_history = mapping_history.release_mapping_history
        ensembl_history = mapping_history.release_mapping_history.ensembl_species_history
        
        status = mapping.status.latest('time_stamp').status_id#.description

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
                            'entryType':cls.entry_type(mapping_history.entry_type_id), 
                            'sequenceVersion':mapping.uniprot.sequence_version,
                            'upi':mapping.uniprot.upi,
                            'md5':mapping.uniprot.md5,
                            'ensemblDerived':mapping.uniprot.ensembl_derived,
                            },
                        'ensemblTranscript': {
                            'enstId':mapping.transcript.enst_id,
                            'enstVersion':mapping.transcript.enst_version,
                            'upi':mapping.transcript.uniparc_accession,
                            'biotype':mapping.transcript.biotype,
                            'deleted':mapping.transcript.deleted,
                            'seqRegionStart':mapping.transcript.seq_region_start,
                            'seqRegionEnd':mapping.transcript.seq_region_end,
                            'ensgId':mapping.transcript.gene.ensg_id,
                            'sequence':sequence
                            },
                       'alignment_difference': mapping.alignment_difference,
                       'status': cls.status_type(status)
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
    labels = CommentLabelSerializer(many=True)

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

class MappingStatsSerializer(serializers.Serializer):
    """
    Serializer for the /stats/ endpoint
    """
    totalMappingCount = serializers.IntegerField()
    statusMappingCount = StatusCountSerializer(many=True)
    labelMappingCount = LabelCountSerializer(many=True)
