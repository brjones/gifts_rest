import pprint
import re
import requests
from collections import defaultdict, OrderedDict

from restui.models.ensembl import EnsemblGene, EnsemblTranscript, EnsemblSpeciesHistory, TranscriptHistory
from restui.models.mappings import Mapping, MappingView, MappingHistory, ReleaseMappingHistory, ReleaseStats
from restui.models.uniprot import UniprotEntry, UniprotEntryHistory
from restui.models.annotations import CvEntryType, CvUeStatus, CvUeLabel, UeMappingStatus, UeMappingComment, UeMappingLabel
from restui.serializers.mappings import MappingByHistorySerializer, ReleaseMappingHistorySerializer, MappingHistorySerializer,\
    MappingSerializer, MappingCommentsSerializer, MappingsSerializer, MappingViewsSerializer,\
    MappingAlignmentsSerializer, CommentLabelSerializer, MappingLabelsSerializer,\
    ReleaseStatsSerializer, UnmappedSwissprotEntrySerializer, UnmappedEnsemblEntrySerializer, ReleasePerSpeciesSerializer
from restui.serializers.annotations import StatusSerializer, CvUeStatusSerializer, CommentSerializer, LabelSerializer
from restui.pagination import FacetPagination, MappingViewFacetPagination, UnmappedEnsemblEntryPagination
from restui.lib.external import ensembl_sequence
from restui.lib.alignments import fetch_pairwise

from django.http import Http404
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Max, F, Q, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.schemas import ManualSchema

import coreapi, coreschema

def get_mapping(pk):
    try:
        return Mapping.objects.get(pk=pk)
    except Mapping.DoesNotExist:
        raise Http404

def get_mapping_history(mapping):
    # A mapping can have multiple entries in mapping history and it is not clear which one to go for.
    # The assumption would be that when mapping is curated it is always related to latest status
    #
    # just pick latest mapping_history entry (the one with the highest id)
    #
    try:
        return MappingHistory.objects.filter(mapping=mapping).order_by('-mapping_history_id')[0]
    except MappingHistory.DoesNotExist:
        raise Http404

def get_status(mapping):
    try:
        mapping_status = Mapping.status_type(mapping.status)
    except (IndexError, CvUeStatus.DoesNotExist):
        # TODO: should log this anomaly or do something else
        mapping_status = None

    return mapping_status

def get_label(label):
    """
    Retrieve the label object associated to the given description
    """

    try:
        return CvUeLabel.objects.get(description=label)
    except CvUeLabel.DoesNotExist:
        raise Http404("Couldn't get label object for {}".format(label))
    except MultipleObjectsReturned:
        raise Http404("Couldn't get unique label object for {}".format(label))
    
def build_taxonomy_data(mapping):
    # Find the ensembl tax id via one ensembl species history associated to transcript
    # associated to the given mapping.
    # Relationship between transcript and history is many to many but we just fetch one history
    # as the tax id remains the same across all of them
    try:
        ensembl_species_history = EnsemblSpeciesHistory.objects.get(transcripthistory__transcript=mapping.transcript)
    except EnsemblSpeciesHistory.DoesNotExist:
        raise Http404("Couldn't find an ensembl species history associated to mapping {}".format(mapping.mapping_id))
    
    try:
        return { 'species':ensembl_species_history.species,
                 'ensemblTaxId':ensembl_species_history.ensembl_tax_id,
                 'uniprotTaxId':mapping.uniprot.uniprot_tax_id }
    except:
        raise Http404("Couldn't find uniprot tax id as I couldn't find a uniprot entry associated to the mapping")


def build_related_mappings_data(mapping):
    """
    Return the list of mappings sharing the same ENST or Uniprot accession of the given mapping.
    """

    # related mappings share the same group_id and tax id
    mapping_mh = mapping.mapping_history.latest('release_mapping_history__time_mapped')
    mapping_mh_rmh = mapping_mh.release_mapping_history
    mapping_grouping_id = mapping_mh.grouping_id

    related_mappings_mh = MappingHistory.objects.filter(release_mapping_history=mapping_mh_rmh, grouping_id=mapping_grouping_id)
    related_mappings = filter(lambda m: m.mapping_id != mapping.mapping_id, ( mh.mapping for mh in related_mappings_mh ) )

    # mappings = Mapping.objects.filter(mapping_history__grouping_id=mapping.mapping_history.latest('release_mapping_history__time_mapped').grouping_id, uniprot__uniprot_tax_id=mapping.uniprot.uniprot_tax_id).exclude(pk=mapping.mapping_id)

    return list(map(lambda m: MappingsSerializer.build_mapping(m, fetch_sequence=False), related_mappings))

def build_related_unmapped_entries_data(mapping):
    """
    Return the list of unmapped entries releated to the mapping (via grouping_id)
    """

    # related unmapped entries share the same grouping_id and tax id
    mapping_mh = mapping.mapping_history.latest('release_mapping_history__time_mapped')
    mapping_mh_rmh = mapping_mh.release_mapping_history
    mapping_grouping_id = mapping_mh.grouping_id

    related_unmapped_ue_histories = UniprotEntryHistory.objects.filter(release_version=mapping_mh_rmh.uniprot_release,
                                                                       grouping_id=mapping_grouping_id)
    related_unmapped_ue_entries = map( lambda ue: { 'uniprotAccession': ue.uniprot_acc,
                                                    'entryType': Mapping.entry_type(ue.entry_type_id),
                                                    'sequenceVersion': ue.sequence_version,
                                                    'upi': ue.upi,
                                                    'md5': ue.md5,
                                                    'isCanonical': False if ue.canonical_uniprot_id else True,
                                                    'alias': ue.alias,
                                                    'ensemblDerived': ue.ensembl_derived,
                                                    'gene_symbol': ue.gene_symbol,
                                                    'gene_accession': ue.chromosome_line,
                                                    'length': ue.length,
                                                    'protein_existence_id': ue.protein_existence_id }, ( ueh.uniprot for ueh in related_unmapped_ue_histories ) )

    related_unmapped_transcript_histories = TranscriptHistory.objects.filter(ensembl_species_history=mapping_mh_rmh.ensembl_species_history,
                                                                             grouping_id=mapping_grouping_id)
    related_unmapped_transcripts = map(lambda transcript: { 'enstId':transcript.enst_id,
                                                            'enstVersion':transcript.enst_version,
                                                            'upi':transcript.uniparc_accession,
                                                            'biotype':transcript.biotype,
                                                            'deleted':transcript.deleted,
                                                            'chromosome':transcript.gene.chromosome,
                                                            'regionAccession':transcript.gene.region_accession,
                                                            'seqRegionStart':transcript.seq_region_start,
                                                            'seqRegionEnd':transcript.seq_region_end,
                                                            'seqRegionStrand':transcript.gene.seq_region_strand,
                                                            'ensgId':transcript.gene.ensg_id,
                                                            'ensgName':transcript.gene.gene_name,
                                                            'ensgSymbol':transcript.gene.gene_symbol,
                                                            'ensgAccession':transcript.gene.gene_accession,
                                                            'ensgRegionAccession':transcript.gene.region_accession,
                                                            'sequence':None,
                                                            'enspId':transcript.ensp_id,
                                                            'enspLen':transcript.ensp_len,
                                                            'source':transcript.source,
                                                            'select':transcript.select }, ( th.transcript for th in related_unmapped_transcript_histories ) )


    return { 'ensembl':list(related_unmapped_transcripts),
             'uniprot':list(related_unmapped_ue_entries) }

#
# TODO: filter by ensembl release (optional argument)
#
class LatestReleaseMappingHistory(generics.RetrieveAPIView):
    """
    Fetch 'latest' release mapping history for the given assembly accesssion.
    """

    serializer_class = ReleaseMappingHistorySerializer
    schema = ManualSchema(description="Fetch 'latest' release mapping history for the given assembly accesssion",
                          fields=[
                              coreapi.Field(
                                  name="assembly_accession",
                                  required=True,
                                  location="path",
                                  schema=coreschema.String(),
                                  description="Assembly accession"
                              ),])

    def get_object(self):
        assembly_accession = self.kwargs["assembly_accession"]

        # optional parameter is ensembl release
        # ensembl_release = self.request.query_params.get('ensembl_release')

        try:
            # latest means by ensembl species history time loaded
            obj = ReleaseMappingHistory.objects.select_related('ensembl_species_history').filter(ensembl_species_history__assembly_accession__iexact=assembly_accession).latest('ensembl_species_history__time_loaded')

        except ReleaseMappingHistory.DoesNotExist:
            raise Http404

        # may raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

class MappingsByHistory(generics.ListAPIView):
    """
    Fetch mappings corresponding to a given release mapping history
    """

    serializer_class = MappingByHistorySerializer
    pagination_class = PageNumberPagination
    schema = ManualSchema(description="Fetch mappings corresponding to a given release mapping history",
                          fields=[
                              coreapi.Field(
                                  name="id",
                                  required=True,
                                  location="path",
                                  schema=coreschema.Integer(),
                                  description="A unique integer value identifying this release mapping history."
                              ),])

    def get_queryset(self):
        release_mapping_history_id = self.kwargs['pk']

        try:
            return Mapping.objects.filter(mapping_history__release_mapping_history=release_mapping_history_id)
        except Mapping.DoesNotExist:
            raise Http404

class UnmappedEntries(APIView):
    """
    Present the details for Swissprot/Ensembl unmapped entities for the latest release for a given species
    """

    # pagination_class = PageNumberPagination # settings.DEFAULT_PAGINATION_CLASS
    schema = ManualSchema(description="Present the details for Swissprot/Ensembl unmapped entities for the latest release for a given species",
                          fields=[
                              coreapi.Field(
                                  name="taxid",
                                  required=True,
                                  location="path",
                                  schema=coreschema.Integer(),
                                  description="Taxonomy id"
                              ),
                              coreapi.Field(
                                  name="source",
                                  required=True,
                                  location="path",
                                  schema=coreschema.String(),
                                  description="Source, either 'swissprot' or 'ensembl'"
                              ),])

    def get(self, request, taxid, source):
        if source == 'swissprot':
            # the Swissprot entries:
            # uniprot_entry_history for release X  minus mapping_history for release X
            # = all unmapped uniprot entries for release X
            # that all can be filtered by entry type

            # find the latest uniprot release corresponding to the species
            # release = UniprotEntryHistory.objects.aggregate(Max('release_version'))['release_version__max']
            release_mapping_history = ReleaseMappingHistory.objects.filter(uniprot_taxid=taxid).latest('release_mapping_history_id')
            # get the Uniprot entries corresponding to that species and uniprot release
            release_uniprot_entries = UniprotEntry.objects.select_related('entry_type').filter(uniprot_tax_id=taxid,uniprotentryhistory__release_version=release_mapping_history.uniprot_release,entry_type__description__icontains='swiss')
            # find the mapped uniprot entries for the release and species
            release_mapped_uniprot_entries = UniprotEntry.objects.select_related('entry_type').filter(mapping__mapping_history__release_mapping_history=release_mapping_history,entry_type__description__icontains='swiss').distinct()
            
            # the unmapped swiss-prot entries
            # NOTE: using select_related('entry_type') to speed up query generates 'Index out of range' error, using it in the two sets above works
            release_unmapped_sp_entries = release_uniprot_entries.difference(release_mapped_uniprot_entries)
            # release_unmapped_sp_entries = release_uniprot_entries.exclude(uniprot_id__in=release_mapped_uniprot_entries.values_list('uniprot_id',flat=True))

            data=list(map(lambda ue: { 'uniprotAccession':ue.uniprot_acc,
                                       "entryType":ue.entry_type.description,
                                       "isCanonical": False if ue.canonical_uniprot_id else True,
                                       "alias":ue.alias if ue.alias else None,
                                       "gene_symbol":ue.gene_symbol,
                                       "gene_accession":ue.chromosome_line,
                                       "length":ue.length,
                                       "protein_existence_id":ue.protein_existence_id }, release_unmapped_sp_entries.order_by('uniprot_acc')))
            
            page = self.paginate_queryset(data)
            if page is not None:
                serializer = UnmappedSwissprotEntrySerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            # if pagination is not defined
            serializer = UnmappedSwissprotEntrySerializer(data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif source == 'ensembl':
            release_mapping_history = ReleaseMappingHistory.objects.filter(ensembl_species_history__ensembl_tax_id=taxid).latest('release_mapping_history_id')
            release_transcripts = EnsemblTranscript.objects.select_related('gene').filter(transcripthistory__ensembl_species_history=release_mapping_history.ensembl_species_history)
            release_mapped_transcripts = EnsemblTranscript.objects.select_related('gene').filter(mapping__mapping_history__release_mapping_history=release_mapping_history).distinct()
            # certain SQL operations, e.g.  values(), count(), order_by, don't work on union/intersection/difference
            # see https://docs.djangoproject.com/en/1.11/ref/models/querysets/#django.db.models.query.QuerySet.union
            # release_unmapped_transcripts = release_transcripts.difference(release_mapped_transcripts)
            release_unmapped_transcripts = release_transcripts.exclude(transcript_id__in=release_mapped_transcripts.values_list('transcript_id', flat=True))

            page = self.paginate_queryset(release_unmapped_transcripts)
            if page is not None:
                serializer = UnmappedEnsemblEntrySerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            # if pagination is not defined
            serializer = UnmappedEnsemblEntrySerializer(data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            raise Http404('Unknown source')
        
    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            # if self.pagination_class is None:
            #     self._paginator = None
            # else:
            #     self._paginator = self.pagination_class()
            source = self.kwargs['source']
            if source == 'ensembl':
                self._paginator = UnmappedEnsemblEntryPagination()
            elif source == 'swissprot':
                self._paginator = LimitOffsetPagination()
            else:
                raise Exception('Unknown source')

        return self._paginator

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None

        return self.paginator.paginate_queryset(queryset, self.request, view=self)
        # limit = self.request.query_params.get('limit', 100)
        # offset = self.request.query_params.get('offset', 0)
        
        
    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

class ReleasePerSpecies(APIView):
    """
    Retrieve Ensembl/Uniprot release per species
    """

    schema = ManualSchema(description="Retrieve Ensembl/Uniprot release per species",
                          fields=[
                              coreapi.Field(
                                  name="taxid",
                                  required=True,
                                  location="path",
                                  schema=coreschema.Integer(),
                                  description="Taxonomy id"
                              ),])

    def get(self, request, taxid):
        # find the latest uniprot release corresponding to the species
        release_mapping_history = ReleaseMappingHistory.objects.select_related('ensembl_species_history').filter(uniprot_taxid=taxid).latest('release_mapping_history_id')

        serializer = ReleasePerSpeciesSerializer({ 'ensembl': release_mapping_history.ensembl_species_history.ensembl_release,
                                                   'uniprot': release_mapping_history.uniprot_release })

        return Response(serializer.data)

class ReleaseMappingStats(APIView):
    """
    Species latest release mapped/unmapped stats (Swissprot/Ensembl)
    """

    schema = ManualSchema(description="Species latest release mapped/unmapped stats (Swissprot/Ensembl)",
                          fields=[
                              coreapi.Field(
                                  name="taxid",
                                  required=True,
                                  location="path",
                                  schema=coreschema.Integer(),
                                  description="Taxonomy id"
                              ),])

    def get(self, request, taxid):
        # client is interested in latest release mapping history
        try:
            # find the release stats for the species latest release mapping
            rmh = ReleaseMappingHistory.objects.filter(uniprot_taxid=taxid).latest('release_mapping_history_id')
            release_stats = ReleaseStats.objects.get(release_mapping_history=rmh)
        except:
            raise Http404("Unable to find stats for latest species {} release mapping history".format(taxid))

        serializer = ReleaseStatsSerializer(release_stats)
        return Response(serializer.data)

class AvailableStatuses(generics.ListAPIView):
    """
    Retrieve available statuses
    """

    serializer_class = CvUeStatusSerializer
    queryset = CvUeStatus.objects.all()

class MappingLabelView(APIView):
    """
    Add or delete label a associated to the given mapping
    """

    permission_classes = (IsAuthenticated,)
    schema = ManualSchema(description="Add or delete label a associated to the given mapping",
                          fields=[
                              coreapi.Field(
                                  name="id",
                                  required=True,
                                  location="path",
                                  schema=coreschema.Integer(),
                                  description="A unique integer value identifying the mapping"
                              ),
                              coreapi.Field(
                                  name="label_id",
                                  required=True,
                                  location="path",
                                  schema=coreschema.Integer(),
                                  description="A unique integer value identifying the label"
                              ),])

    def post(self, request, pk, label_id):
        mapping = get_mapping(pk)
        
        mapping_labels = UeMappingLabel.objects.filter(mapping=mapping,label=label_id)
        if mapping_labels:
            # Mapping already exists, ignore

            return Response(status=status.HTTP_204_NO_CONTENT)

        try:
            label = CvUeLabel.objects.get(pk=label_id)
            serializer = LabelSerializer(data={ 'time_stamp': timezone.now(),
                                                'user_stamp': request.user,
                                                'label': label_id,
                                                'mapping': pk })
        except KeyError:
            raise Http404("Must provide valid label")
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, label_id):
        mapping = get_mapping(pk)

        # delete all labels with the given description attached to the mapping
        # TODO: only those associated to the given user
        mapping_labels = UeMappingLabel.objects.filter(mapping=mapping,label=label_id)
        if mapping_labels:
            mapping_labels.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        raise Http404


class MappingLabelsView(APIView):
    """
    Retrieve all labels for a given mapping
    """

    schema = ManualSchema(description="Retrieve all labels for a given mapping",
                          fields=[
                              coreapi.Field(
                                  name="id",
                                  required=True,
                                  location="path",
                                  schema=coreschema.Integer(),
                                  description="A unique integer value identifying the mapping"
                              ),])

    def get(self, request, pk):
        mapping = get_mapping(pk)
        
        all_labels = CvUeLabel.objects.all()
        
        mapping_labels = mapping.labels.values_list('label', flat=True)
        
        label_map = []
        
        for label in all_labels:
            if label.id in mapping_labels:
                label_map.append({'label': label.description, 'id': label.id, 'status': True})
            else:
                label_map.append({'label': label.description, 'id': label.id, 'status': False})

        data = { 'labels': label_map }

        serializer = MappingLabelsSerializer(data)
        return Response(serializer.data)

class EditDeleteCommentView(APIView):
    """
    Edit (PUT) and delete (DELETE) a comment for a given mapping.
    """

    permission_class = (IsAuthenticated,)
    schema = ManualSchema(description="Edit or delete a comment for a given mapping.",
                          fields=[
                              coreapi.Field(
                                  name="id",
                                  required=True,
                                  location="path",
                                  schema=coreschema.Integer(),
                                  description="A unique integer value identifying the mapping"
                              ),
                              coreapi.Field(
                                  name="comment_id",
                                  required=True,
                                  location="path",
                                  schema=coreschema.Integer(),
                                  description="A unique integer value identifying the comment"
                              ),])

    def put(self, request, pk, comment_id):
        mapping = get_mapping(pk)

        try:
            comment = mapping.comments.get(id=comment_id)
        except KeyError:
            return Response({ "error": "Text not specified" }, status=status.HTTP_400_BAD_REQUEST)
        except UeMappingComment.DoesNotExist:
            return Response({ "error": "Invalid comment ID: {}".format(comment_id) }, status=status.HTTP_400_BAD_REQUEST)
        else:
            if comment.deleted:
                return Response({ "error":"Cannot edit deleted comment" }, status=status.HTTP_400_BAD_REQUEST)

            comment.comment = request.data['text']
            comment.time_stamp = timezone.now()
            comment.save()

        serializer = CommentLabelSerializer({ 'commentId': comment.id,
                                              'text': comment.comment,
                                              'timeAdded': comment.time_stamp,
                                              'user': comment.user_stamp.full_name,
                                              'deleted': comment.deleted })
        return Response(serializer.data)

    def delete(self, request, pk, comment_id):
        mapping = get_mapping(pk)

        try:
            comment = mapping.comments.get(id=comment_id)
        except:
            return Response("Invalid comment ID: {}".format(comment_id), status=status.HTTP_400_BAD_REQUEST)
        else:
            comment.deleted = True
            comment.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
    
class MappingCommentsView(APIView):
    """
    Add a comment/Retrieve all comments relative to a given mapping, includes mapping labels.
    """

    permission_classes = (IsAuthenticated,)
    schema = ManualSchema(description="Add a comment/Retrieve all comments relative to a given mapping, includes mapping labels.",
                          fields=[
                              coreapi.Field(
                                  name="id",
                                  required=True,
                                  location="path",
                                  schema=coreschema.Integer(),
                                  description="A unique integer value identifying the mapping"
                              ),])

    def get(self, request, pk):
        mapping = get_mapping(pk)

        # fetch mapping comment history
        mapping_comments = mapping.comments.order_by('-time_stamp')
        comments = map(lambda c: { 'commentId':c.id, 'text':c.comment, 'timeAdded':c.time_stamp, 'user':c.user_stamp.full_name, 'deleted':c.deleted }, mapping_comments)

        data = {  'mappingId': pk,
                  'comments':list(comments)
        }

        serializer = MappingCommentsSerializer(data)
        return Response(serializer.data)
    
    def post(self, request, pk):
        mapping = get_mapping(pk)

        try:
            serializer = CommentSerializer(data={ 'time_stamp':timezone.now(),
                                                  'user_stamp':request.user,
                                                  'comment':request.data['text'],
                                                  'mapping':mapping.mapping_id })
        except KeyError:
            raise Http404("Must provide comment")

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MappingStatusView(APIView):
    """
    Change the status of a mapping
    """

    permission_classes = (IsAuthenticated,)
    schema = ManualSchema(description="Change the status of a mapping",
                          fields=[
                              coreapi.Field(
                                  name="id",
                                  required=True,
                                  location="path",
                                  schema=coreschema.Integer(),
                                  description="A unique integer value identifying the mapping"
                              ),])

    def put(self, request, pk):
        mapping = get_mapping(pk)

        # retrieve the status object associated to the given description
        try:
            s = CvUeStatus.objects.get(description=request.data['status'])
        except KeyError:
            raise Http404("Payload should have 'status'")
        except CvUeStatus.DoesNotExist:
            raise Http404("Couldn't get status object for {}".format(request.data['status']))
        except MultipleObjectsReturned:
            raise Http404("Couldn't get unique status for {}".format(request.data['status']))

        # If the mapping has already been assigned that status, update the timestamp,
        # otherwise create one from scratch
        try:
            mapping_status = UeMappingStatus.objects.filter(mapping=mapping).latest('time_stamp')
        except UeMappingStatus.DoesNotExist:
            # It's alright, for the first status change of a mapping a
            # historic record won't exist.
            pass

        else:
            if mapping_status.status == s.id:
                # The user is trying to change it to what the status
                # already is, nothing to do.
                return Response(status=status.HTTP_204_NO_CONTENT)

        # create new mapping status
        serializer = StatusSerializer(data={ 'time_stamp':timezone.now(),
                                             'user_stamp':request.user,
                                             'status':s.id,
                                             'mapping':mapping.mapping_id })

        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Update the status in the mapping record
        mapping.status = s
        mapping.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MappingPairwiseAlignment(APIView):
    """
    Retrieve a set of pairwise alignments for a single mapping
    """

    schema = ManualSchema(description="Retrieve a set of pairwise alignments for a single mapping",
                          fields=[
                              coreapi.Field(
                                  name="id",
                                  required=True,
                                  location="path",
                                  schema=coreschema.Integer(),
                                  description="A unique integer value identifying the mapping"
                              ),])


    def get(self, request, pk):
        try:
            mapping = Mapping.objects.prefetch_related('alignments').select_related('transcript').select_related('uniprot').get(pk=pk)
            alignments = fetch_pairwise(mapping)
        except Exception as e:
            pprint.pprint(e)
            raise Http404
         
        serializer = MappingAlignmentsSerializer(alignments)
         
        return Response(serializer.data)


class MappingDetailed(APIView):
    """
    Retrieve a single mapping, includes related mappings/unmapped entries and taxonomy information.
    """

    schema = ManualSchema(description="Retrieve a single mapping, includes related mappings/unmapped entries and taxonomy information.",
                          fields=[
                              coreapi.Field(
                                  name="id",
                                  required=True,
                                  location="path",
                                  schema=coreschema.Integer(),
                                  description="A unique integer value identifying the mapping"
                              ),])

    def get(self, request, pk):
        mapping = get_mapping(pk)

        data = { 'taxonomy': build_taxonomy_data(mapping),
                 'mapping': MappingsSerializer.build_mapping(mapping, fetch_sequence=True, authenticated=True if request.user and request.user.is_authenticated else False),
                 'relatedEntries': { 'mapped': build_related_mappings_data(mapping),
                                     'unmapped': build_related_unmapped_entries_data(mapping) } }

        serializer = MappingSerializer(data)

        return Response(serializer.data)

#
# NOTES
#
# - What does it mean to search with a given mapping ID, return just that mapping
#   or all 'related' mappings?
#   We're returning only that mapping at the moment, to discuss with Uniprot
#
class MappingsSearch(generics.ListAPIView):
    """
    Search/retrieve all mappings. Mappings are grouped if they share ENST or UniProt accessions.
    'Facets' are used for filtering and returned by the service based on the result set.
    """

    serializer_class = MappingsSerializer
    pagination_class = FacetPagination
    schema = ManualSchema(description="Retrieve a single mapping, includes related mappings/unmapped entries and taxonomy information.",
                          fields=[
                              coreapi.Field(
                                  name="searchTerm",
                                  location="query",
                                  schema=coreschema.Integer(),
                                  description="Search term (no wildcards)"
                              ),
                              coreapi.Field(
                                  name="limit",
                                  location="query",
                                  schema=coreschema.Integer(),
                                  description="Number of results to return per page"
                              ),
                              coreapi.Field(
                                  name="offset",
                                  location="query",
                                  schema=coreschema.Integer(),
                                  description="The initial index from which to return the results"
                              ),
                              coreapi.Field(
                                  name="facets",
                                  location="query",
                                  schema=coreschema.Integer(),
                                  description="Filters for the given query, taking the form 'facets=key1:value1,key2:value2...'\nPossible keys (values) are: organism (taxid) , sequence (identical, small, large), status and chromosomes"
                              ),
                          ])
    
    def get_queryset(self):
        results = dict()
        
        # the ENSG, ENST, UniProt accession or mapping id. If none are provided all mappings are returned
        search_term = self.request.query_params.get('searchTerm', None)
        
        # filters for the given query, taking the form facets=organism:9606,status:unreviewed
        facets_params = self.request.query_params.get('facets', None)

        # search the mappings according to the search term 'type'
        queryset = None
        if search_term:
            if search_term.isdigit(): # this is a mapping ID
                # TODO
                #  what does it mean to search with a given mapping ID, return just that mapping
                #  or all 'related' mappings? We're returning only that mapping at the moment
                queryset = [ get_mapping(search_term) ]
            else: # this is either an ENSG/ENST or UniProt accession or gene name
                if re.match(r"^ENS[A-Z]*?G[0-9]+?$", search_term, re.I):
                    queryset = Mapping.objects.filter(transcript__gene__ensg_id__iexact=search_term)
                elif re.match(r"^ENS[A-Z]*?T[0-9]+?$", search_term, re.I):
                    queryset = Mapping.objects.filter(transcript__enst_id__iexact=search_term)
                elif re.match(r"^([O,P,Q][0-9][A-Z, 0-9]{3}[0-9]|[A-N,R-Z]([0-9][A-Z][A-Z, 0-9]{2}){1,2}[0-9])(-\d+)*$",
                              search_term, re.I): # looks like a Uniprot accession
                    # filter in order to get the isoforms as well
                    queryset = Mapping.objects.filter(uniprot__uniprot_acc__iregex=r"^"+search_term)
                else:
                    # should be a search request with a gene symbol and possibly name
                    query_filter = Q(transcript__gene__gene_symbol__iregex=r"^"+search_term)
                    query_filter |= Q(transcript__gene__gene_name__iregex=r"^"+search_term)
                    queryset = Mapping.objects.filter(query_filter)

        else:
            # no search term: return all mappings
            #
            # WARNING!! This is massively hitting the database
            #
            # See Matt's June 19 Matt's comments on slack for a possible direction
            # e.g. https://github.com/encode/django-rest-framework/issues/1721
            #
            # Can return an iterator, but this is not compatible with pagination, see comments below
            # queryset = Mapping.objects.all().iterator()
            queryset = Mapping.objects.all()

        #
        # Apply filters based on facets parameters
        #
        if facets_params:
            queryset = queryset.all()
            # create facets dict from e.g. 'organism:9606,status:unreviewed'
            facets = dict( tuple(param.split(':')) for param in facets_params.split(',') )

            # follow the relationships up to ensembl_species_history to filter based on taxid
            if 'organism' in facets:
                queryset = queryset.filter(transcript__transcripthistory__ensembl_species_history__ensembl_tax_id=facets['organism'])

            # Filter on how large a difference between the pairwise aligned protein sequences, if there is an alignment
            if 'sequence' in facets:
                if facets['sequence'] == 'identical':
                    queryset = queryset.filter(alignment_difference=0)
                elif facets['sequence'] == 'small':
                    queryset = queryset.filter(alignment_difference__gt=0, alignment_difference__lte=5)
                elif facets['sequence'] == 'large':
                    queryset = queryset.filter(alignment_difference__gt=5)

            # filter queryset based on status
            # NOTE: cannot directly filter by following relationships,
            #       have to fetch latest status associated to each mapping
            if 'status' in facets:
                # create closure to be used in filter function to filter queryset based on status
                # binds to given status so filter can pass each mapping which is compared against binding param
                try:
                    status_id = CvUeStatus.objects.get(description=facets['status'].upper()).id
                except:
                    raise Http404("Invalid status type")
                    # TODO Should be a 400, how do we make this work with pagination?
                    #return Response(status=status.HTTP_400_BAD_REQUEST)

                queryset = queryset.filter(status=status_id)

            if 'chromosomes' in facets:
                queryset = queryset.filter(transcript__gene__chromosome=facets['chromosomes'])

        return queryset

class MappingViewsSearch(generics.ListAPIView):
    """
    Search/retrieve all mappings views.
    'Facets' are used for filtering and returned by the service based on the result set.
    """

    serializer_class = MappingViewsSerializer
    pagination_class = MappingViewFacetPagination

    def get_queryset(self):
        # either the ENSG, ENST, UniProt accession, gene symbol or gene name
        # if none are provided all mappings are returned
        search_term = self.request.query_params.get('searchTerm', None)

        # filters for the given query, taking the form facets=organism:9606,status:unreviewed
        facets_params = self.request.query_params.get('facets', None)

        # search the mappings according to the search term 'type'
        queryset = None
        if search_term:
            if re.match(r"^ENS[A-Z]*?G[0-9]+?$", search_term, re.I):
                queryset = MappingView.objects.filter(ensg_id__iexact=search_term)
            elif re.match(r"^ENS[A-Z]*?T[0-9]+?$", search_term, re.I):
                queryset = MappingView.objects.filter(enst_id__iexact=search_term)
            elif re.match(r"^([O,P,Q][0-9][A-Z, 0-9]{3}[0-9]|[A-N,R-Z]([0-9][A-Z][A-Z, 0-9]{2}){1,2}[0-9])(-\d+)*$",
                          search_term, re.I): # looks like a Uniprot accession
                # filter in order to get the isoforms as well
                queryset = MappingView.objects.filter(uniprot_acc__iregex=r"^"+search_term)
            else:
                # should be a search request with a gene symbol (both Uniprot and Ensembl) and possibly name
                query_filter = Q(gene_symbol_up__iregex=r"^"+search_term)
                query_filter |= Q(gene_symbol_eg__iregex=r"^"+search_term)
                query_filter |= Q(gene_name__iregex=r"^"+search_term)
                queryset = MappingView.objects.filter(query_filter)
        else:
            # no search term: return all mappings
            queryset = MappingView.objects.all()

        #
        # Apply filters based on facets parameters
        #
        if facets_params:
            # create facets dict from e.g. 'organism:9606,status:unreviewed'
            facets = dict( tuple(param.split(':')) for param in facets_params.split(',') )

            queryset = queryset.all()

            # filter based on species
            # TODO: allow multiple organisms
            if 'organism' in facets:
                queryset = queryset.filter(uniprot_tax_id=facets['organism'])

            # filter on how large a difference between the pairwise
            # aligned protein sequences is, if there is an alignment
            if 'alignment' in facets:
                if facets['alignment'] == 'identical':
                    queryset = queryset.filter(alignment_difference=0)
                elif facets['alignment'] == 'small':
                    queryset = queryset.filter(alignment_difference__gt=0, alignment_difference__lte=5)
                elif facets['alignment'] == 'large':
                    queryset = queryset.filter(alignment_difference__gt=5)

            # filter based on status
            if 'status' in facets:
                try:
                    status_id = CvUeStatus.objects.get(description=facets['status'].upper()).id
                except:
                    raise Http404("Invalid status type")
                    # TODO Should be a 400, how do we make this work with pagination?
                    #return Response(status=status.HTTP_400_BAD_REQUEST)

                queryset = queryset.filter(status=status_id)

            # filter based on chromosomes
            if 'chromosomes' in facets:
                queryset = queryset.filter(chromosome=facets['chromosomes'])

            # filter based on entry type
            if 'type' in facets:
                queryset = queryset.filter(uniprot_mapping_status=facets['type'])

            # filter out entries on patches
            if 'patches' in facets:
                # options:
                # - 1: include patches
                # - 2: exclude patches
                # - 3: include only patches
                if facets["patches"] == 'exclude':
                    queryset = queryset.exclude(region_accession__iregex=r"^CHR")
                elif facets["patches"] == 'only':
                    queryset = queryset.filter(region_accession__iregex=r"^CHR")

        return queryset
