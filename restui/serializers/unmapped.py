"""
.. See the NOTICE file distributed with this work for additional information
   regarding copyright ownership.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from rest_framework import serializers
from restui.serializers.mappings import MappingViewSerializer


class UnmappedEntrySerializer(serializers.Serializer):
    entry = MappingViewSerializer()
    relatedEntries = MappingViewSerializer(many=True)


class UnmappedSwissprotEntrySerializer(serializers.Serializer):
    """
    Serializer for unmapped Swissprot entries /unmapped/<taxid>/swissprot endpoint.
    """

    uniprotAccession = serializers.CharField()
    entryType = serializers.CharField()
    isCanonical = serializers.NullBooleanField()
    alias = serializers.CharField()
    gene_symbol = serializers.CharField()
    gene_accession = serializers.CharField()
    length = serializers.IntegerField()
    protein_existence_id = serializers.IntegerField()


class UnmappedEnsemblGeneSerializer(serializers.Serializer):
    ensgId = serializers.CharField()
    ensgName = serializers.CharField()
    chromosome = serializers.CharField()
    regionAccession = serializers.CharField()
    seqRegionStart = serializers.IntegerField()
    seqRegionEnd = serializers.IntegerField()
    seqRegionStrand = serializers.IntegerField()
    source = serializers.CharField()


class UnmappedEnsemblTranscriptSerializer(serializers.Serializer):
    enstId = serializers.CharField()
    biotype = serializers.CharField()
    source = serializers.CharField()


class UnmappedEnsemblEntrySerializer(serializers.Serializer):
    """
    Serializer for unmapped ensembl entries /unmapped/<taxid>/ensembl endpoint.
    """

    gene = UnmappedEnsemblGeneSerializer()

    # serializers.ListField(child=serializers.CharField())
    transcripts = UnmappedEnsemblTranscriptSerializer(many=True)

    @classmethod
    def build_group(cls, ensg_id, group):
        gene = group[0].gene

        transcripts = []
        for transcript in group:
            transcripts.append({
                'enstId': transcript.enst_id,
                'biotype': transcript.biotype,
                'source': transcript.source
            })

        output_group = {
            'gene': {
                'ensgId': gene.ensg_id,
                'ensgName': gene.gene_name,
                'chromosome': gene.chromosome,
                'regionAccession': gene.region_accession,
                'seqRegionStart': gene.seq_region_start,
                'seqRegionEnd': gene.seq_region_end,
                'seqRegionStrand': gene.seq_region_strand,
                'source': gene.source
            },
            'transcripts': transcripts
        }

        return output_group


class CommentSerializer(serializers.Serializer):
    """
    For nested serialization of user comment for an unmapped entry in call to
    unmapped/<id>/comments/ endpoint.
    """

    commentId = serializers.IntegerField()
    text = serializers.CharField()
    timeAdded = serializers.DateTimeField()
    user = serializers.CharField()
    editable = serializers.BooleanField()


class UnmappedEntryCommentsSerializer(serializers.Serializer):
    """
    Serialize data in call to unmapped/<id>/comments/ endpoint.
    """

    mapping_view_id = serializers.IntegerField()
    comments = CommentSerializer(many=True)
