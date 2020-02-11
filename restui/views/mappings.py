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

import pprint
import re
import urllib.parse

from django.http import Http404
from django.utils import timezone
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.schemas import ManualSchema

import coreapi
import coreschema

from restui.models.ensembl import EnsemblSpeciesHistory
from restui.models.ensembl import TranscriptHistory
from restui.models.mappings import Mapping
from restui.models.mappings import MappingView
from restui.models.mappings import MappingHistory
from restui.models.mappings import ReleaseMappingHistory
from restui.models.mappings import ReleaseStats
from restui.models.uniprot import UniprotEntryHistory
from restui.models.annotations import CvUeStatus
from restui.models.annotations import CvUeLabel
from restui.models.annotations import UeMappingStatus
from restui.models.annotations import UeMappingComment
from restui.models.annotations import UeMappingLabel
from restui.serializers.mappings import MappingByHistorySerializer
from restui.serializers.mappings import ReleaseMappingHistorySerializer
from restui.serializers.mappings import EnsemblUniprotMappingSerializer
from restui.serializers.mappings import MappingSerializer
from restui.serializers.mappings import MappingCommentsSerializer
from restui.serializers.mappings import MappingsSerializer
from restui.serializers.mappings import MappingViewsSerializer
from restui.serializers.mappings import MappingAlignmentsSerializer
from restui.serializers.mappings import CommentLabelSerializer
from restui.serializers.mappings import ReleaseStatsSerializer
from restui.serializers.mappings import ReleasePerSpeciesSerializer
from restui.serializers.annotations import CvUeStatusSerializer
from restui.serializers.annotations import MappingStatusSerializer
from restui.serializers.annotations import MappingCommentSerializer
from restui.serializers.annotations import MappingLabelSerializer
from restui.serializers.annotations import LabelsSerializer
from restui.pagination import MappingViewFacetPagination
from restui.lib.alignments import fetch_pairwise
from restui.lib.mail import GiftsEmail
from django.conf import settings


def get_mapping(pk):
    try:
        return Mapping.objects.get(pk=pk)
    except Mapping.DoesNotExist:
        raise Http404


def build_taxonomy_data(mapping):
    """
    Find the ensembl tax id via one ensembl species history associated to
    transcript associated to the given mapping.

    Relationship between transcript and history is many to many but we just
    fetch one history as the tax id remains the same across all of them
    """
    try:
        ensembl_species_history = EnsemblSpeciesHistory.objects.filter(
            transcripthistory__transcript=mapping.transcript
        ).latest('time_loaded')
    except EnsemblSpeciesHistory.DoesNotExist:
        raise Http404(
            (
                "Couldn't find an ensembl species history associated to mapping {}"
            ).format(mapping.mapping_id)
        )

    try:
        return {
            'species': ensembl_species_history.species,
            'ensemblTaxId': ensembl_species_history.ensembl_tax_id,
            'uniprotTaxId': mapping.uniprot.uniprot_tax_id
        }
    except:
        raise Http404(
            (
                "Couldn't find uniprot tax id as I couldn't find a uniprot entry "
                "associated to the mapping"
            )
        )


def build_related_mappings_data(mapping):
    """
    Return the list of mappings sharing the same ENST or Uniprot accession of
    the given mapping.

    Parameters
    ----------
    mapping : Mapping object

    Returns
    -------
    list
        List of objects that are related to the same mapping group
    """

    # related mappings share the same group_id and tax id
    mapping_mh = mapping.mapping_history.latest(
        'release_mapping_history__time_mapped'
    )

    mapping_mh_rmh = mapping_mh.release_mapping_history
    mapping_grouping_id = mapping_mh.grouping_id

    related_mappings_mh = MappingHistory.objects.filter(
        release_mapping_history=mapping_mh_rmh,
        grouping_id=mapping_grouping_id
    )

    related_mappings = []
    for mh in related_mappings_mh:
        m = mh.mapping
        if m.mapping_id != mapping.mapping_id:
            related_mappings.append(
                MappingsSerializer.build_mapping(m, fetch_sequence=False)
            )

    return related_mappings


def build_related_unmapped_entries_data(mapping):
    """
    Return the list of unmapped entries releated to the mapping (via grouping_id)
    """

    # related unmapped entries share the same grouping_id and tax id
    mapping_mh = mapping.mapping_history.latest('release_mapping_history__time_mapped')
    mapping_mh_rmh = mapping_mh.release_mapping_history
    mapping_grouping_id = mapping_mh.grouping_id

    related_unmapped_ue_histories = UniprotEntryHistory.objects.filter(
        release_version=mapping_mh_rmh.uniprot_release,
        grouping_id=mapping_grouping_id
    )

    related_unmapped_ue_entries = []
    for ueh in related_unmapped_ue_histories:
        up_entry = ueh.uniprot
        related_unmapped_ue_entries.append({
            'uniprot_id': up_entry.uniprot_id,
            'uniprotAccession': up_entry.uniprot_acc,
            'entryType': Mapping.entry_type(up_entry.entry_type_id),
            'sequenceVersion': up_entry.sequence_version,
            'upi': up_entry.upi,
            'md5': up_entry.md5,
            'isCanonical': not up_entry.canonical_uniprot_id,
            'alias': up_entry.alias,
            'ensemblDerived': up_entry.ensembl_derived,
            'gene_symbol': up_entry.gene_symbol,
            'gene_accession': up_entry.chromosome_line,
            'length': up_entry.length,
            'protein_existence_id': up_entry.protein_existence_id
        })

    related_unmapped_transcript_histories = TranscriptHistory.objects.filter(
        ensembl_species_history=mapping_mh_rmh.ensembl_species_history,
        grouping_id=mapping_grouping_id
    )

    related_unmapped_transcripts = []
    for t_hist in related_unmapped_transcript_histories:
        transcript = t_hist.transcript
        related_unmapped_transcripts.append({
            'transcript_id': transcript.transcript_id,
            'enstId': transcript.enst_id,
            'enstVersion': transcript.enst_version,
            'upi': transcript.uniparc_accession,
            'biotype': transcript.biotype,
            'deleted': transcript.deleted,
            'chromosome': transcript.gene.chromosome,
            'regionAccession': transcript.gene.region_accession,
            'seqRegionStart': transcript.seq_region_start,
            'seqRegionEnd': transcript.seq_region_end,
            'seqRegionStrand': transcript.gene.seq_region_strand,
            'ensgId': transcript.gene.ensg_id,
            'ensgName': transcript.gene.gene_name,
            'ensgSymbol': transcript.gene.gene_symbol,
            'ensgAccession': transcript.gene.gene_accession,
            'ensgRegionAccession': transcript.gene.region_accession,
            'sequence': None,
            'enspId': transcript.ensp_id,
            'enspLen': transcript.ensp_len,
            'source': transcript.source,
            'select': transcript.select
        })

    return {
        'ensembl': related_unmapped_transcripts,
        'uniprot': related_unmapped_ue_entries
    }


#
# TODO: filter by ensembl release (optional argument)
#
class LatestReleaseMappingHistory(generics.RetrieveAPIView):
    """
    Fetch 'latest' release mapping history for the given assembly accesssion.
    """

    serializer_class = ReleaseMappingHistorySerializer
    schema = ManualSchema(
        description="Fetch 'latest' release mapping history for the given assembly accesssion",
        fields=[
            coreapi.Field(
                name="assembly_accession",
                required=True,
                location="path",
                schema=coreschema.String(),
                description="Assembly accession"
            ),
        ]
    )

    def get_object(self):
        assembly_accession = self.kwargs["assembly_accession"]

        # optional parameter is ensembl release
        # ensembl_release = self.request.query_params.get('ensembl_release')

        try:
            # latest means by ensembl species history time loaded
            obj = ReleaseMappingHistory.objects.select_related(
                'ensembl_species_history'
            ).filter(
                ensembl_species_history__assembly_accession__iexact=assembly_accession,
                ensembl_species_history__status="LOAD_COMPLETE"
            ).latest('time_mapped')

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
    schema = ManualSchema(
        description="Fetch mappings corresponding to a given release mapping history",
        fields=[
            coreapi.Field(
                name="id",
                required=True,
                location="path",
                schema=coreschema.Integer(),
                description="A unique integer value identifying this release mapping history."
            ),
        ]
    )

    def get_queryset(self):
        release_mapping_history_id = self.kwargs['pk']

        try:
            return Mapping.objects.filter(
                mapping_history__release_mapping_history=release_mapping_history_id
            ).order_by('mapping_id')
        except Mapping.DoesNotExist:
            raise Http404


class ReleasePerSpecies(APIView):
    """
    Retrieve Ensembl/Uniprot release per species
    """

    schema = ManualSchema(
        description="Retrieve Ensembl/Uniprot release per species",
        fields=[
            coreapi.Field(
                name="taxid",
                required=True,
                location="path",
                schema=coreschema.Integer(),
                description="Taxonomy id"
            ),
        ]
    )

    def get(self, request, taxid):
        # find the latest uniprot release corresponding to the species
        release_mapping_history = ReleaseMappingHistory.objects.select_related(
            'ensembl_species_history'
        ).filter(
            uniprot_taxid=taxid
        ).latest(
            'release_mapping_history_id'
        )

        serializer = ReleasePerSpeciesSerializer({
            'ensembl': release_mapping_history.ensembl_species_history.ensembl_release,
            'uniprot': release_mapping_history.uniprot_release
        })

        return Response(serializer.data)


class ReleaseMappingStats(APIView):
    """
    Species latest release mapped/unmapped stats (Swissprot/Ensembl)
    """

    schema = ManualSchema(
        description="Species latest release mapped/unmapped stats (Swissprot/Ensembl)",
        fields=[
            coreapi.Field(
                name="taxid",
                required=True,
                location="path",
                schema=coreschema.Integer(),
                description="Taxonomy id"
            ),
        ]
    )

    def get(self, request, taxid):
        # client is interested in latest release mapping history
        try:
            # find the release stats for the species latest release mapping
            rmh = ReleaseMappingHistory.objects.filter(
                uniprot_taxid=taxid
            ).latest(
                'release_mapping_history_id'
            )

            release_stats = ReleaseStats.objects.get(release_mapping_history=rmh)
        except:
            raise Http404(
                (
                    "Unable to find stats for latest species {} release mapping history"
                ).format(taxid)
            )

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
    schema = ManualSchema(
        description="Add or delete label a associated to the given mapping",
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
            ),
        ]
    )

    def post(self, request, pk, label_id):
        mapping = get_mapping(pk)

        mapping_labels = UeMappingLabel.objects.filter(
            mapping=mapping,
            label=label_id
        )

        if mapping_labels:
            # mapping already has a label, ignore
            return Response(status=status.HTTP_204_NO_CONTENT)

        try:
            serializer = MappingLabelSerializer(
                data={
                    'time_stamp': timezone.now(),
                    'user_stamp': request.user,
                    'label': label_id,
                    'mapping': pk
                }
            )
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
        mapping_labels = UeMappingLabel.objects.filter(
            mapping=mapping,
            label=label_id
        )

        if mapping_labels:
            mapping_labels.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        raise Http404


class MappingLabelsView(APIView):
    """
    Retrieve all labels for a given mapping
    """

    schema = ManualSchema(
        description="Retrieve all labels for a given mapping",
        fields=[
            coreapi.Field(
                name="id",
                required=True,
                location="path",
                schema=coreschema.Integer(),
                description="A unique integer value identifying the mapping"
            ),
        ]
    )

    def get(self, request, pk):
        mapping = get_mapping(pk)

        all_labels = CvUeLabel.objects.all()
        mapping_labels = mapping.labels.values_list('label', flat=True)

        label_map = []
        for label in all_labels:
            label_map.append({
                'label': label.description,
                'id': label.id,
                'status': label.id in mapping_labels
            })

        data = {'labels': label_map}
        serializer = LabelsSerializer(data)

        return Response(serializer.data)


class EditDeleteCommentView(APIView):
    """
    Edit (PUT) and delete (DELETE) a comment for a given mapping.
    """

    permission_class = (IsAuthenticated,)
    schema = ManualSchema(
        description="Edit or delete a comment for a given mapping.",
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
            ),
        ]
    )

    def put(self, request, pk, comment_id):
        mapping = get_mapping(pk)

        if 'text' not in request.data:
            return Response(
                {"error": "Text not specified"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            comment = mapping.comments.get(id=comment_id)
        except UeMappingComment.DoesNotExist:
            return Response(
                {"error": "Invalid comment ID: {}".format(comment_id)},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            if comment.deleted:
                return Response(
                    {"error": "Cannot edit deleted comment"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            comment.comment = request.data['text']
            comment.time_stamp = timezone.now()
            comment.save()

        editable = False
        if request.user and request.user == comment.user_stamp:
            editable = True

        serializer = CommentLabelSerializer({
            'commentId': comment.id,
            'text': comment.comment,
            'timeAdded': comment.time_stamp,
            'user': comment.user_stamp.full_name,
            'editable': editable
        })

        return Response(serializer.data)

    def delete(self, request, pk, comment_id):
        mapping = get_mapping(pk)

        try:
            comment = mapping.comments.get(id=comment_id)
        except:
            return Response(
                {"error": "Invalid comment ID: {}".format(comment_id)},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            comment.deleted = True
            comment.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class MappingCommentsView(APIView):
    """
    Add a comment/Retrieve all comments relative to a given mapping, includes
    mapping labels.
    """

    permission_classes = (IsAuthenticated,)
    schema = ManualSchema(
        description=(
            "Add a comment/Retrieve all comments relative to a given mapping, "
            "includes mapping labels."
        ),
        fields=[
            coreapi.Field(
                name="id",
                required=True,
                location="path",
                schema=coreschema.Integer(),
                description="A unique integer value identifying the mapping"
            ),
        ]
    )

    def get(self, request, pk):
        mapping = get_mapping(pk)

        # fetch mapping comment history, exclude deleted comments
        mapping_comments = mapping.comments.filter(
            deleted=False
        ).order_by(
            '-time_stamp'
        )

        # comments are editable if they belong to the requesting user
        comments = []
        for comment in mapping_comments:
            comments.append({
                'commentId': comment.id,
                'text': comment.comment,
                'timeAdded': comment.time_stamp,
                'user': comment.user_stamp.full_name,
                'editable': request.user and request.user == comment.user_stamp
            })

        data = {
            'mappingId': pk,
            'comments': comments
        }

        serializer = MappingCommentsSerializer(data)
        return Response(serializer.data)

    def post(self, request, pk):
        mapping = get_mapping(pk)

        try:
            serializer = MappingCommentSerializer(
                data={
                    'time_stamp': timezone.now(),
                    'user_stamp': request.user,
                    'comment': request.data['text'],
                    'mapping': mapping.mapping_id,
                    'deleted': False
                }
            )
        except KeyError:
            raise Http404("Must provide comment")

        if serializer.is_valid():
            serializer.save()

            email = GiftsEmail(request)
            build_comments_email = email.build_comments_email(mapping)
            if build_comments_email:
                email.send()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class MappingStatusView(APIView):
    """
    Change the status of a mapping
    """

    permission_classes = (IsAuthenticated,)
    schema = ManualSchema(
        description="Change the status of a mapping",
        fields=[
            coreapi.Field(
                name="id",
                required=True,
                location="path",
                schema=coreschema.Integer(),
                description="A unique integer value identifying the mapping"
            ),
        ]
    )

    def put(self, request, pk):
        mapping = get_mapping(pk)

        # retrieve the status object associated to the given description
        try:
            s = CvUeStatus.objects.get(description=request.data['status'])
        except KeyError:
            raise Http404("Payload should have 'status'")
        except CvUeStatus.DoesNotExist:
            raise Http404(
                "Couldn't get status object for {}".format(request.data['status'])
            )
        except MultipleObjectsReturned:
            raise Http404(
                "Couldn't get unique status for {}".format(request.data['status'])
            )

        """
        If the mapping has already been assigned that status, update the timestamp,
        otherwise create one from scratch
        """
        try:
            mapping_status = UeMappingStatus.objects.filter(
                mapping=mapping
            ).latest('time_stamp')
        except UeMappingStatus.DoesNotExist:
            # It's alright, for the first status change of a mapping a
            # historic record won't exist.
            pass

        else:
            if mapping_status.status.id == s.id:
                # The user is trying to change it to what the status
                # already is, nothing to do.
                return Response(status=status.HTTP_204_NO_CONTENT)

        # create new mapping status
        serializer = MappingStatusSerializer(
            data={
                'time_stamp': timezone.now(),
                'user_stamp': request.user,
                'status': s.id,
                'mapping': mapping.mapping_id
            }
        )

        if serializer.is_valid():
            serializer.save()
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update the status in the mapping record
        mapping.status = s
        mapping.save()

        # update status on mapping_view corresponding entry,
        # otherwise search won't reflect the status change
        try:
            mv = MappingView.objects.get(mapping_id=pk)
        except MappingView.DoesNotExist:
            return Response(
                {"error": "Could not find mapping {} in search table.".format(pk)},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            prev_status = CvUeStatus.objects.get(id=mv.status)
            mv.status = s.id
            mv.save()

            email = GiftsEmail(request)
            build_status_change_email = email.build_status_change_email(mapping, prev_status.description, s.description)
            if build_status_change_email:
                email.send()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MappingAlignmentDifference(APIView):
    """
    Update a mapping's alignment difference
    """

    permission_classes = (IsAuthenticated,)
    schema = ManualSchema(
        description="Update a mapping's alignment difference",
        fields=[
            coreapi.Field(
                name="id",
                required=True,
                location="path",
                schema=coreschema.Integer(),
                description="A unique integer value identifying the mapping"
            ),
            coreapi.Field(
                name="difference",
                required=True,
                location="path",
                schema=coreschema.Integer(),
                description="An integer representing the alignment difference"
            ),
        ])

    def post(self, request, pk, difference):
        mapping = get_mapping(pk)

        mapping.alignment_difference = difference
        mapping.save()

        serializer = EnsemblUniprotMappingSerializer(
            MappingsSerializer.build_mapping(mapping)
        )

        return Response(serializer.data)


class MappingPairwiseAlignment(APIView):
    """
    Retrieve a set of pairwise alignments for a single mapping
    """

    schema = ManualSchema(
        description="Retrieve a set of pairwise alignments for a single mapping",
        fields=[
            coreapi.Field(
                name="id",
                required=True,
                location="path",
                schema=coreschema.Integer(),
                description="A unique integer value identifying the mapping"
            ),
        ]
    )

    def get(self, request, pk):
        try:
            mapping = Mapping.objects.prefetch_related(
                'alignments'
            ).select_related(
                'transcript'
            ).select_related(
                'uniprot'
            ).get(pk=pk)
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

    schema = ManualSchema(
        description=(
            "Retrieve a single mapping, includes related mappings/unmapped "
            "entries and taxonomy information."
        ),
        fields=[
            coreapi.Field(
                name="id",
                required=True,
                location="path",
                schema=coreschema.Integer(),
                description="A unique integer value identifying the mapping"
            ),
        ]
    )

    def get(self, request, pk):
        mapping = get_mapping(pk)

        authenticated = False
        if request.user and request.user.is_authenticated:
            authenticated = True

        email_recipients_list = {
            recipient_id: recipient_details.get('name')
            for (recipient_id, recipient_details) in settings.EMAIL_RECIPIENT_LIST.items()
        }

        data = {
            'taxonomy': build_taxonomy_data(mapping),
            'mapping': MappingsSerializer.build_mapping(
                mapping,
                fetch_sequence=True,
                authenticated=authenticated
            ),
            'relatedEntries': {
                'mapped': build_related_mappings_data(mapping),
                'unmapped': build_related_unmapped_entries_data(mapping)
            },
            'emailRecipientsList': email_recipients_list
        }

        serializer = MappingSerializer(data)

        return Response(serializer.data)


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

        """
        filters for the given query, taking the form:
            facets=organism:9606,status:unreviewed
        """
        facets_params = self.request.query_params.get('facets', None)

        # search the mappings according to the search term 'type'
        queryset = None
        if search_term:
            if re.match(r"^ENS[A-Z]*?G[0-9]+?$", search_term, re.I):
                queryset = MappingView.objects.filter(ensg_id__iexact=search_term)

            elif re.match(r"^ENS[A-Z]*?T[0-9]+(.[0-9]+)?$", search_term, re.I):
                queryset = MappingView.objects.filter(enst_id__iexact=search_term)

            elif re.match(
                    r"^([O,P,Q][0-9][A-Z, 0-9]{3}[0-9]|[A-N,R-Z]([0-9][A-Z][A-Z, 0-9]{2}){1,2}[0-9])(-\d+)*$",  # pylint: disable=line-too-long
                    search_term, re.I
            ):  # looks like a Uniprot accession
                # filter in order to get the isoforms as well
                queryset = MappingView.objects.filter(
                    uniprot_acc__iregex=r"^"+search_term
                )

            else:
                # should be a search request with a gene symbol (both Uniprot
                # and Ensembl) and possibly name
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
            # NOTE: must unquote as apparently the browser does not decode
            facets_params = urllib.parse.unquote(facets_params)

            # create facets dict from e.g.
            # 'organism:9606,10090;status:unreviewed;chromosome:10,11,X'
            facets = {}
            for param in facets_params.split(';'):
                p = param.split(':')
                facets[p[0]] = p[1]

            queryset = queryset.all()

            # filter based on species
            if 'organism' in facets:
                # consider query may request for multiple organisms
                queryset = queryset.filter(
                    uniprot_tax_id__in=facets['organism'].split(',')
                )

            # filter on how large a difference between the pairwise
            # aligned protein sequences is, if there is an alignment
            if 'alignment' in facets:
                # consider query may request for multiple alignment differences
                alignment_diff_filter = Q()

                for diff in facets['alignment'].split(','):
                    if diff == 'identical':
                        alignment_diff_filter |= Q(alignment_difference=0)
                    elif diff == 'small':
                        alignment_diff_filter |= Q(
                            alignment_difference__gt=0,
                            alignment_difference__lte=5
                        )
                    elif diff == 'large':
                        alignment_diff_filter |= Q(alignment_difference__gt=5)

                queryset = queryset.filter(alignment_diff_filter)

            # filter based on status
            if 'status' in facets:
                # possible multiple statuses
                status_filter = Q()

                for status_description in facets['status'].split(','):
                    try:
                        status_id = CvUeStatus.objects.get(
                            description=status_description.upper()
                        ).id
                    except:
                        # TODO Should be a 400, how do we make this work with pagination?
                        # return Response(status=status.HTTP_400_BAD_REQUEST)
                        raise Http404("Invalid status type")
                    else:
                        status_filter |= Q(status=status_id)

                queryset = queryset.filter(status_filter)

            # filter based on chromosomes
            if 'chromosomes' in facets:
                # possible multiple chromosomes
                queryset = queryset.filter(
                    chromosome__in=facets['chromosomes'].split(',')
                )

            # filter based on entry type
            if 'type' in facets:
                # possible multiple types
                queryset = queryset.filter(
                    uniprot_mapping_status__in=facets['type'].split(',')
                )

            # filter out entries on patches
            if 'patches' in facets:
                # options, should be mutually exclusive
                # - 1: include patches
                # - 2: exclude patches
                # - 3: include only patches
                if facets["patches"] == 'exclude':
                    queryset = queryset.exclude(region_accession__iregex=r"^CHR")

                elif facets["patches"] == 'only':
                    queryset = queryset.filter(region_accession__iregex=r"^CHR")

        return queryset
