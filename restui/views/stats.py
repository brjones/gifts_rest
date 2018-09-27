import pprint
import re
import requests
from collections import OrderedDict

from restui.models.ensembl import EnsemblGene
from restui.models.mappings import Mapping, ReleaseStats
from restui.models.uniprot import UniprotEntry
from restui.models.annotations import CvEntryType, CvUeStatus, CvUeLabel, UeMappingStatus, UeMappingComment, UeMappingLabel
from restui.serializers.stats import ReleaseStatsSerializer
from restui.pagination import FacetPagination

from django.http import Http404
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Max, F, Q, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

class MappedStats(APIView):
    """
    Return stats on all the mappings
    """
    def get(self, request):

        #
        # Mapping stats: general and Uniprot/Ensembl specific
        #
        mappings_count = Mapping.objects.count() # tot mappings

        uniprot_mapped_count = Mapping.objects.values('uniprot').distinct().count() # tot mapped uniprot entries
        uniprot_not_mapped_sp_count = None # tot non mapped Swiss-Prot entries, NOTE: NO WAY TO GET IT AT THE MOMENT

        all_entry_types = dict( (entry.id, entry.description) for entry in CvEntryType.objects.all() )
        sp_entry_type_ids = [ k for (k, v) in all_entry_types.items() if v.lower().startswith('swiss') ]
        nonsp_entry_type_ids = list(set(all_entry_types.keys()).difference(sp_entry_type_ids))

        #
        # NOTE:
        #  This is not requested but it's computation is reported (commented) here for completeness
        uniprot_mapped_sp_count = 0 # tot mapped Swiss-Prot entries, NOTE: NOT REQUESTED BUT HERE FOR COMPLETENESS
        # if sp_entry_type_ids:
        #     query_filter = Q(mapping_history__entry_type=sp_entry_type_ids[0])
        #
        #     for i in range(1, len(sp_entry_type_ids)):
        #         query_filter = query_filter | Q(mapping_history__entry_type=sp_entry_type_ids[i])
        #
        #     uniprot_mapped_sp_count = Mapping.objects.filter(query_filter).values('uniprot').distinct().count()
        #
        # tot non mapped genes which none of its transcripts match to any SwissProt entry
        gene_not_mapped_sp_count = 0
        #
        # NOTE:
        #   Here we're counting genes not mapped to Swiss-Prot entries among the mapped genes.
        #   As discussed with UniProt, they'd prefer counting among the non mapped genes, which
        #   in this case coincide with counting the non-mapped genes in general, as done below.
        #
        # if nonsp_entry_type_ids:
        #     query_filter = Q(mapping_history__entry_type=nonsp_entry_type_ids[0])
        #
        #     for i in range(1, len(sp_entry_type_ids)):
        #         query_filter = query_filter | Q(mapping_history__entry_type=nonsp_entry_type_ids[i])
        #
        #     gene_not_mapped_sp_count = Mapping.objects.filter(query_filter).values('transcript__gene').distinct().count()

        gene_ids = set( gene.gene_id for gene in EnsemblGene.objects.all() )
        gene_mapped_ids = set( item['transcript__gene'] for item in Mapping.objects.values('transcript__gene').distinct() )
        gene_mapped_count = len(gene_mapped_ids) # tot mapped Ensembl genes
        gene_not_mapped_sp_count = len(gene_ids.difference(gene_mapped_ids))

        transcript_mapped_count = Mapping.objects.values('transcript').distinct().count() # tot mapped Ensembl transcripts

        #
        # Stats relative to mapping labels
        #
        all_labels = CvUeLabel.objects.all()
        
        label_counts = []
        
        for label in all_labels:
            count = UeMappingLabel.objects.filter(label=label).count()
            label_counts.append({'label': label.description, 'count': count})

        #
        # Stats for mapping status
        #
        status_counts = []
        status_totals = Mapping.objects.values('status').annotate(total=Count('status'))
        for status_count in status_totals:
            status_counts.append({'status': Mapping.status_type(status_count['status']), 'count': status_count['total']})
    
        serializer = MappingStatsSerializer({'mapping': { 'total': mappings_count,
                                                          'uniprot': { 'mapped': uniprot_mapped_count,
                                                                       'not_mapped_sp': uniprot_not_mapped_sp_count },
                                                          'ensembl': { 'gene_mapped': gene_mapped_count,
                                                                       'gene_not_mapped_sp': gene_not_mapped_sp_count,
                                                                       'transcript_mapped': transcript_mapped_count } },
                                             'status': status_counts,
                                             'label': label_counts })

        return Response(serializer.data)

class UnmappedStats(APIView):
    """
    Total counts for Swissprot/Ensembl not mapped entries
    """

    def get(self, request):
        # client is interested in latest release mapping history
        try:
            release_stats = ReleaseStats.objects.latest('release_mapping_history')
        except:
            raise Http404

        serializer = ReleaseStatsSerializer(release_stats)
        return Response(serializer.data)
