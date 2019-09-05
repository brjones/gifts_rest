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

from django.urls import path
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from restui.views import alignments
from restui.views import ensembl
from restui.views import mappings
from restui.views import uniprot
from restui.views import unmapped
from restui.views import service
from restui.views import version


@csrf_exempt
def method_router(request, *args, **kwargs):
    """
    Handler for method routing in the module

    Parameters
    ----------
    request : request object
    """
    if settings.FALLOVER and (request.method == 'POST' or request.method == 'PUT'):
        raise Http404
        # This doesn't work for some reason, maybe Alessandro can figure it out.
        # raise FalloverROException

    view = kwargs.pop('VIEW', None)
    if view is not None:
        return view(request, *args, **kwargs)

    raise Http404

urlpatterns = [
    # retrieve alignment run by ID
    path('alignments/alignment_run/<int:pk>/', alignments.AlignmentRunFetch.as_view()),

    # insert alignment run
    path('alignments/alignment_run/', alignments.AlignmentRunCreate.as_view()),

    # retrieve latest alignments by assembly accession
    #   param: alignment_type: perfect_match (default), identity
    path('alignments/alignment/latest/assembly/<assembly_accession>/',
         alignments.LatestAlignmentsFetch.as_view()),

    # fetch alignments by alignment run ID
    path('alignments/alignment/alignment_run/<int:pk>/',
         alignments.AlignmentByAlignmentRunFetch().as_view()),

    # retrieve alignment by ID
    path('alignments/alignment/<int:pk>/', alignments.AlignmentFetch.as_view()),

    # insert alignment
    path('alignments/alignment/', alignments.AlignmentCreate.as_view()),

    # bulk load of genes/transcripts
    path('ensembl/load/<species>/<assembly_accession>/<int:ensembl_tax_id>/<int:ensembl_release>/',
         ensembl.EnsemblFeature.as_view()),

    # fetch latest ensembl release (status load complete)
    path('ensembl/release/latest/assembly/<assembly_accession>/',
         ensembl.LatestEnsemblRelease.as_view()),

    # fetch species history by ID
    path('ensembl/species_history/<int:pk>/', ensembl.SpeciesHistory.as_view()),

    # fetch transcript by ID
    path('ensembl/transcript/<int:pk>/', ensembl.Transcript.as_view()),

    # fetch alignment by align run/uniprot/transcript
    path('ensembl/cigar/align_run/<int:run>/uniprot/<acc>/<int:seq_version>/transcript/<enst_id>/',
         ensembl.EnspUCigarFetch.as_view()),

    # update species history alignment status
    path('ensembl/species_history/<int:pk>/alignment_status/<status>/',
         ensembl.SpeciesHistoryAlignmentStatus.as_view()),

    # fetch/update cigar by alignment ID
    path('ensembl/cigar/alignment/<int:pk>/',
         ensembl.EnspUCigarFetchUpdateByAlignment.as_view()),

    # insert cigar/mdz
    path('ensembl/cigar/', ensembl.EnspUCigarCreate.as_view()),

    # fetch latest release_mapping_history for a given assembly
    path('mappings/release_history/latest/assembly/<assembly_accession>/',
         mappings.LatestReleaseMappingHistory.as_view()),

    # fetch mappings related to a given release mapping history
    path('mappings/release_history/<int:pk>/', mappings.MappingsByHistory.as_view()),

    # fetch ensembl/uniprot release per species
    path('mappings/release/<int:taxid>/', mappings.ReleasePerSpecies.as_view()),

    # species mapped/unmapped release stats
    path('mappings/stats/<int:taxid>/', mappings.ReleaseMappingStats.as_view()),

    # retrieve available mapping statuses
    path('mappings/statuses/', mappings.AvailableStatuses.as_view()),

    # add/delete a label to a mapping
    path('mapping/<int:pk>/labels/<label_id>/', method_router,
         {'VIEW': mappings.MappingLabelView.as_view()}),

    # retrieve all labels of a mapping
    path('mapping/<int:pk>/labels/', mappings.MappingLabelsView.as_view()),

    # edit/delete comment
    path('mapping/<int:pk>/comments/<comment_id>/', method_router,
         {'VIEW': mappings.EditDeleteCommentView.as_view()}),

    # add comment/retrieve all comments
    path('mapping/<int:pk>/comments/', method_router,
         {'VIEW': mappings.MappingCommentsView.as_view()}, name="add_retrieve_comments"),

    # update mapping status
    path('mapping/<int:pk>/status/', method_router,
         {'VIEW': mappings.MappingStatusView.as_view()}),

    # retrieve pairwise alignments for a mapping
    path('mapping/<int:pk>/pairwise/', mappings.MappingPairwiseAlignment.as_view()),

    # update mapping alignment_difference
    path('mapping/<int:pk>/alignment_difference/<int:difference>/', method_router,
         {'VIEW': mappings.MappingAlignmentDifference.as_view()}),

    # path('mapping/<int:pk>/alignment_run/<alignment_run>/difference/')

    # retrieve mapping and related entries
    path('mapping/<int:pk>/', mappings.MappingDetailed.as_view()),

    # search the mappings (limit/offset paginated results)
    path('mappings/', mappings.MappingViewsSearch.as_view()),

    # fetch uniprot entry by db ID
    path('uniprot/entry/<int:pk>/', uniprot.UniprotEntryFetch.as_view()),

    # add/delete a label to unmapped entry
    path('unmapped/<int:mapping_view_id>/labels/<label_id>/', method_router,
         {'VIEW': unmapped.AddDeleteLabel.as_view()}),

    # retrieve all labels of an unmapped entry
    path('unmapped/<int:mapping_view_id>/labels/', unmapped.GetLabels.as_view()),

    # edit/delete comment
    path('unmapped/<int:mapping_view_id>/comments/<comment_id>/', method_router,
         {'VIEW': unmapped.EditDeleteComment.as_view()}),

    # add comment/retrieve all comments for an unmapped entry
    path('unmapped/<int:mapping_view_id>/comments/', method_router,
         {'VIEW': unmapped.AddGetComments.as_view()}),

    # update status
    path('unmapped/<int:mapping_view_id>/status/', method_router,
         {'VIEW': unmapped.StatusChange.as_view()}),

    # retrieve unmapped and related entries
    path('unmapped/<int:mapping_view_id>/', unmapped.UnmappedDetailed.as_view()),

    # fetch unmapped entries (Swissprot, Ensembl)
    path('unmapped/<int:taxid>/<source>/', unmapped.UnmappedEntries.as_view()),

    # return service status
    path('service/ping/', service.PingService.as_view()),

    path('api/version/', version.APIVersion.as_view())
]

"""
DO NOT EDIT

This is used to note down the endpoints needed for the pipelines scripts used
by Ensembl

eu_alignment_perfect_match

X mappings/release_history/latest/assembly/<assembly_accession> # fetch latest
(by ensembl species history time loaded) release_mapping_history for a given
assembly:
  - optional param: ensembl release: fetch latest by release as well
  - return ensembl species history as nested element
  - mapping/history/<int:pk>/ # fetch the mappings for a given release mapping
    history (includes mapping type from corresponding mapping history)
X fetch transcripts by id
X fetch uniprot entries by id
X alignments/alignment_run/ # create alignment run
X alignments/alignment/ # create alignment


eu_alignment_blast_cigar

X fetch alignment run by ID
X fetch latest release mapping history ... (same as before) -> access ensembl
  species history
X fetch latest alignments by type and assembly accession
X create new alignment run
X fetch transcripts
X create alignment
X create cigar
"""
