from rest_framework import serializers

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

class CommentLabelSerializer(serializers.Serializer):
    """
    For nested serialization of user comment or label for a mapping in call to comments/<mapping_id> endpoint.
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
    status = serializers.CharField()
    comments = CommentLabelSerializer(many=True)
    labels = CommentLabelSerializer(many=True)
