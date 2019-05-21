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

from restui.models.ensembl import EnsemblTranscript
from restui.models.uniprot import UniprotEntry
from restui.models.mappings import MappingView
from restui.models.mappings import ReleaseMappingHistory
from restui.models.annotations import CvUeStatus, CvUeLabel
from restui.models.annotations import UeUnmappedEntryLabel
from restui.models.annotations import UeUnmappedEntryStatus

from restui.serializers.unmapped import UnmappedEntrySerializer
from restui.serializers.unmapped import UnmappedSwissprotEntrySerializer
from restui.serializers.unmapped import UnmappedEnsemblEntrySerializer
from restui.serializers.unmapped import CommentSerializer
from restui.serializers.unmapped import UnmappedEntryCommentsSerializer
from restui.serializers.annotations import LabelsSerializer
from restui.serializers.annotations import UnmappedEntryLabelSerializer
from restui.serializers.annotations import UnmappedEntryCommentSerializer
from restui.serializers.annotations import UnmappedEntryStatusSerializer
from restui.pagination import UnmappedEnsemblEntryPagination

from django.utils import timezone
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.schemas import ManualSchema

import coreapi
import coreschema


def get_uniprot_entry(mapping_view_id):
    try:
        mapping_view = MappingView.objects.get(pk=mapping_view_id)
        uniprot_entry = UniprotEntry.objects.get(pk=mapping_view.uniprot_id)
    except (MappingView.DoesNotExist, UniprotEntry.DoesNotExist):
        raise Http404

    return uniprot_entry


class UnmappedDetailed(APIView):
    """
    Retrieve a single "unmapped" entry, includes related entries.
    """

    schema = ManualSchema(
        description="Retrieve a single unmapped entry, includes related entries.",
        fields=[
            coreapi.Field(
                name="id",
                required=True,
                location="path",
                schema=coreschema.Integer(),
                description="A unique integer value identifying the mapping view id"
            ),
        ]
    )

    def get(self, request, mapping_view_id):
        try:
            mapping_view = MappingView.objects.get(pk=mapping_view_id)
        except MappingView.DoesNotExist:
            raise Http404

        # this is supposed to be called for an unmapped entry
        if (
                mapping_view.uniprot_mapping_status == 'mapped' and
                mapping_view.mapping_id is not None
        ):
            return Response(
                {"error":"Entry is mapped with id {}".format(mapping_view.mapping_id)},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = {
            'entry': mapping_view,
            'relatedEntries': list(
                MappingView.objects.filter(
                    grouping_id=mapping_view.grouping_id
                ).exclude(pk=mapping_view_id)
            )
        }

        serializer = UnmappedEntrySerializer(data)

        return Response(serializer.data)


class UnmappedEntries(APIView):
    """
    Present the details for Swissprot/Ensembl unmapped entities for the latest
    release for a given species
    """

    # pagination_class = PageNumberPagination # settings.DEFAULT_PAGINATION_CLASS
    schema = ManualSchema(
        description="Present the details for Swissprot/Ensembl unmapped entities for the latest release for a given species",
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
            ),
        ]
    )

    def get(self, request, taxid, source):
        if source == 'swissprot':
            # the Swissprot entries:
            # uniprot_entry_history for release X  minus mapping_history for release X
            # = all unmapped uniprot entries for release X
            # that all can be filtered by entry type

            # find the latest uniprot release corresponding to the species
            # release = UniprotEntryHistory.objects.aggregate(Max('release_version'))['release_version__max']
            release_mapping_history = ReleaseMappingHistory.objects.filter(
                uniprot_taxid=taxid
            ).latest(
                'release_mapping_history_id'
            )

            # get the Uniprot entries corresponding to that species and uniprot release
            release_uniprot_entries = UniprotEntry.objects.select_related(
                'entry_type'
            ).filter(
                uniprot_tax_id=taxid,
                uniprotentryhistory__release_version=release_mapping_history.uniprot_release,
                entry_type__description__icontains='swiss'
            )

            # find the mapped uniprot entries for the release and species
            release_mapped_uniprot_entries = UniprotEntry.objects.select_related(
                'entry_type'
            ).filter(
                mapping__mapping_history__release_mapping_history=release_mapping_history,
                ntry_type__description__icontains='swiss'
            ).distinct()

            # the unmapped swiss-prot entries
            # NOTE: using select_related('entry_type') to speed up query generates 'Index out of range' error, using it in the two sets above works
            release_unmapped_sp_entries = release_uniprot_entries.difference(
                release_mapped_uniprot_entries
            )
            # release_unmapped_sp_entries = release_uniprot_entries.exclude(uniprot_id__in=release_mapped_uniprot_entries.values_list('uniprot_id',flat=True))

            data = list(
                map(
                    lambda ue: {
                        'uniprotAccession': ue.uniprot_acc,
                        "entryType": ue.entry_type.description,
                        "isCanonical": False if ue.canonical_uniprot_id else True,
                        "alias": ue.alias if ue.alias else None,
                        "gene_symbol": ue.gene_symbol,
                        "gene_accession": ue.chromosome_line,
                        "length": ue.length,
                        "protein_existence_id": ue.protein_existence_id
                    },
                    release_unmapped_sp_entries.order_by('uniprot_acc')
                )
            )

            page = self.paginate_queryset(data)
            if page is not None:
                serializer = UnmappedSwissprotEntrySerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            # if pagination is not defined
            serializer = UnmappedSwissprotEntrySerializer(data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif source == 'ensembl':
            release_mapping_history = ReleaseMappingHistory.objects.filter(
                ensembl_species_history__ensembl_tax_id=taxid
            ).latest(
                'release_mapping_history_id'
            )

            release_transcripts = EnsemblTranscript.objects.select_related(
                'gene'
            ).filter(
                transcripthistory__ensembl_species_history=release_mapping_history.ensembl_species_history
            )

            release_mapped_transcripts = EnsemblTranscript.objects.select_related(
                'gene'
            ).filter(
                mapping__mapping_history__release_mapping_history=release_mapping_history
            ).distinct()

            """
            certain SQL operations, e.g.  values(), count(), order_by, don't work
            on union/intersection/difference

            see https://docs.djangoproject.com/en/1.11/ref/models/querysets/#django.db.models.query.QuerySet.union
            """
            release_unmapped_transcripts = EnsemblTranscript.objects.exclude(
                transcript_id__in=release_mapped_transcripts.values_list(
                    'transcript_id', flat=True
                )
            )

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

        return self.paginator.paginate_queryset(
            queryset,
            self.request,
            view=self
        )

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)


class AddDeleteLabel(APIView):
    """
    Add or delete label a associated to the given unmapped entry
    """

    permission_classes = (IsAuthenticated,)
    schema = ManualSchema(
        description="Add or delete label a associated to the given unmapped entry",
        fields=[
            coreapi.Field(
                name="id",
                required=True,
                location="path",
                schema=coreschema.Integer(),
                description="The mapping view id associated to the unmapped entry"
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

    def post(self, request, mapping_view_id, label_id):
        uniprot_entry = get_uniprot_entry(mapping_view_id)

        entry_labels = UeUnmappedEntryLabel.objects.filter(
            uniprot=uniprot_entry,
            label=label_id
        )

        if entry_labels:
            # label already attached, ignore
            return Response(status=status.HTTP_204_NO_CONTENT)

        try:
            label = CvUeLabel.objects.get(pk=label_id)
            serializer = UnmappedEntryLabelSerializer(
                data={
                    'time_stamp': timezone.now(),
                    'user_stamp': request.user,
                    'label': label_id,
                    'uniprot': uniprot_entry.uniprot_id
                }
            )
        except KeyError:
            raise Http404("Must provide valid label")

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, mapping_view_id, label_id):
        uniprot_entry = get_uniprot_entry(mapping_view_id)

        # delete all labels with the given description attached to the mapping
        # TODO: only those associated to the given user
        entry_labels = UeUnmappedEntryLabel.objects.filter(uniprot=uniprot_entry,label=label_id)
        if entry_labels:
            entry_labels.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        raise Http404

class GetLabels(APIView):
    """
    Retrieve all labels for a given unmapped entry
    """

    schema = ManualSchema(
        description="Retrieve all labels for a given unmapped entry",
        fields=[
            coreapi.Field(
                name="id",
                required=True,
                location="path",
                schema=coreschema.Integer(),
                description="The mapping view id associated to the given unmapped entry"
            ),
        ]
    )

    def get(self, request, mapping_view_id):
        uniprot_entry = get_uniprot_entry(mapping_view_id)

        all_labels = CvUeLabel.objects.all()
        entry_labels = uniprot_entry.labels.values_list('label', flat=True)

        label_map = []
        for label in all_labels:
            label_map.append({
                'label': label.description,
                'id': label.id,
                'status': True if label.id in entry_labels else False
            })

        data = {'labels': label_map}
        serializer = LabelsSerializer(data)

        return Response(serializer.data)


class AddGetComments(APIView):
    """
    Add a comment/Retrieve all comments relative to a given unmapped entry
    """

    permission_classes = (IsAuthenticated,)
    schema = ManualSchema(
        description="Add a comment/Retrieve all comments relative to a given unmapped entry.",
        fields=[
            coreapi.Field(
                name="id",
                required=True,
                location="path",
                schema=coreschema.Integer(),
                description="The mapping view id associated to the unmapped entry"
            ),
        ]
    )

    def get(self, request, mapping_view_id):
        uniprot_entry = get_uniprot_entry(mapping_view_id)

        # fetch mapping comment history, exclude deleted comments
        entry_comments = uniprot_entry.comments.filter(deleted=False).order_by('-time_stamp')

        # comments are editable if they belong to the requesting user
        comments = map(
            lambda c: {
                'commentId': c.id,
                'text': c.comment,
                'timeAdded': c.time_stamp,
                'user': c.user_stamp.full_name,
                'editable': True if request.user and request.user == c.user_stamp else False
            },
            entry_comments
        )

        data = {
            'mapping_view_id': mapping_view_id,
            'comments': list(comments)
        }
        serializer = UnmappedEntryCommentsSerializer(data)

        return Response(serializer.data)

    def post(self, request, mapping_view_id):
        uniprot_entry = get_uniprot_entry(mapping_view_id)

        try:
            serializer = UnmappedEntryCommentSerializer(
                data={
                    'time_stamp': timezone.now(),
                    'user_stamp': request.user,
                    'comment': request.data['text'],
                    'uniprot': uniprot_entry.uniprot_id,
                    'deleted': False
                }
            )
        except KeyError:
            raise Http404("Must provide comment")

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditDeleteComment(APIView):
    """
    Edit (PUT) and delete (DELETE) a comment for a given unmapped entry
    """

    permission_class = (IsAuthenticated,)
    schema = ManualSchema(
        description="Edit or delete a comment for a given unmapped entry.",
        fields=[
            coreapi.Field(
                name="id",
                required=True,
                location="path",
                schema=coreschema.Integer(),
                description="The mapping_view id associated to the unmapped entry"
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

    def put(self, request, mapping_view_id, comment_id):
        uniprot_entry = get_uniprot_entry(mapping_view_id)

        if 'text' not in request.data:
            return Response(
                {"error": "Text not specified"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            comment = uniprot_entry.comments.get(id=comment_id)
        except UeUnmappedEntryComment.DoesNotExist:
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

        serializer = CommentSerializer({
            'commentId': comment.id,
            'text': comment.comment,
            'timeAdded': comment.time_stamp,
            'user': comment.user_stamp.full_name,
            'editable': True if request.user and request.user == comment.user_stamp else False
        })

        return Response(serializer.data)

    def delete(self, request, mapping_view_id, comment_id):
        uniprot_entry = get_uniprot_entry(mapping_view_id)

        try:
            comment = uniprot_entry.comments.get(id=comment_id)
        except:
            return Response(
                "Invalid comment ID: {}".format(comment_id),
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            comment.deleted = True
            comment.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class StatusChange(APIView):
    """
    Change the status of an unmapped entry
    """

    permission_classes = (IsAuthenticated,)
    schema = ManualSchema(
        description="Change the status of an unmapped entry",
        fields=[
            coreapi.Field(
                name="id",
                required=True,
                location="path",
                schema=coreschema.Integer(),
                description="The mapping_view id associated to the unmapped entry"
            ),
        ]
    )

    def put(self, request, mapping_view_id):
        uniprot_entry = get_uniprot_entry(mapping_view_id)

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

        # If the entry has already been assigned that status, update the timestamp,
        # otherwise create one from scratch
        try:
            entry_status = UeUnmappedEntryStatus.objects.filter(
                uniprot=uniprot_entry
            ).latest(
                'time_stamp'
            )
        except UeUnmappedEntryStatus.DoesNotExist:
            # It's alright, for the first status change the historic record won't exist.
            pass
        else:
            if entry_status.status.id == s.id:
                # The user is trying to change it to what the status
                # already is, nothing to do.
                return Response(status=status.HTTP_204_NO_CONTENT)

        # create new status
        serializer = UnmappedEntryStatusSerializer(
            data={
                'time_stamp': timezone.now(),
                'user_stamp': request.user,
                'status': s.id,
                'uniprot': uniprot_entry.uniprot_id
            }
        )

        if serializer.is_valid():
            serializer.save()
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        """
        Update the status in the uniprot entry?
        We should first add it to the corresponding model
        uniprot_entry.status = s
        uniprot_entry.save()

        update status on mapping_view corresponding entry,
        otherwise search won't reflect the status change
        """
        try:
            mv = MappingView.objects.get(pk=mapping_view_id)
        except MappingView.DoesNotExist:
            return Response(
                {"error": "Could not find mapping_view {} in search table.".format(mapping_view_id)},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            mv.status = s.id
            mv.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
