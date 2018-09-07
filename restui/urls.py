from django.urls import path
from django.conf.urls import url
from restui.views import alignments, ensembl, mappings, uniprot

urlpatterns = [
    path('alignments/alignment_run/<int:pk>/', alignments.AlignmentRunFetch.as_view()), # retrieve alignment run by ID
    path('alignments/alignment_run/', alignments.AlignmentRunCreate.as_view()),         # insert alignment run
    path('alignments/alignment/latest/assembly/<assembly_accession>/',                  # retrieve latest alignments by assembly accession
         alignments.LatestAlignmentsFetch.as_view()),                                   #   param: alignment_type: perfect_match (default), identity
    path('alignments/alignment/<int:pk>/', alignments.AlignmentFetch.as_view()),        # retrieve alignment by ID
    path('alignments/alignment/', alignments.AlignmentCreate.as_view()),                # insert alignment
    
    path('ensembl/load/<species>/<assembly_accession>/<int:ensembl_tax_id>/<int:ensembl_release>/', # bulk load of genes/transcripts
         ensembl.EnsemblFeature.as_view()),
    path('ensembl/release/latest/assembly/<assembly_accession>/',                                   # fetch latest ensembl release (status load complete)
         ensembl.LatestEnsemblRelease.as_view()),
    path('ensembl/species_history/<int:pk>/', ensembl.SpeciesHistory.as_view()),                    # fetch species history by ID
    path('ensembl/transcript/<int:pk>/', ensembl.Transcript.as_view()),                             # fetch transcript by ID
    path('ensembl/cigar/align_run/<int:run>/uniprot/<acc>/<int:seq_version>/transcript/<enst_id>/', # fetch alignment by align run/uniprot/transcript
         ensembl.EnspUCigarFetch.as_view()),
    path('ensembl/cigar/', ensembl.EnspUCigarCreate.as_view()),                                     # insert cigar/mdz

    path('mappings/release_history/latest/assembly/<assembly_accession>/',              # fetch latest release_mapping_history for a given assembly
         mappings.LatestReleaseMappingHistory.as_view()),
    path('mappings/release_history/<int:pk>/', mappings.MappingsByHistory.as_view()),   # fetch mappings related to a given release mapping history (paginated results)
    path('mapping/<int:pk>/labels/<label_id>/', mappings.MappingLabelView.as_view()),   # add/delete a label to a mapping
    path('mapping/<int:pk>/labels/', mappings.MappingLabelsView.as_view()),             # retrieve all labels of a mapping
    path('mapping/<int:pk>/comments/', mappings.MappingCommentsView.as_view()),         # add comment/retrieve all comments of a mapping
    path('mapping/<int:pk>/status/', mappings.MappingStatusView.as_view()),             # update mapping status
    # path('mapping/<int:pk>/pairwise/', mappings.MappingPairwiseAlignment.as_view()),  # retrieve pairwise alignments for a mapping
    path('mapping/<int:pk>/', mappings.MappingView.as_view()),                          # retrieve single mapping
    path('mappings/stats/', mappings.MappingStatsView.as_view()),                       # retrieve mapping stats
    path('mappings/', mappings.MappingsView.as_view()),                                 # search the mappings (limit/offset paginated results)

    path('uniprot/entry/<int:pk>/', uniprot.UniprotEntryFetch.as_view()),                       # fetch uniprot entry by db ID
]

#
# DO NOT EDIT
#
# This is used to note down the endpoints needed for the pipelines scripts used by Ensembl
#
# eu_alignment_perfect_match
#
# X mappings/release_history/latest/assembly/<assembly_accession> # fetch latest (by ensembl species history time loaded) release_mapping_history for a given assembly
#   - optional param: ensembl release: fetch latest by release as well
#   - return ensembl species history as nested element
# - mapping/history/<int:pk>/ # fetch the mappings for a given release mapping history (includes mapping type from corresponding mapping history)
# X fetch transcripts by id
# X fetch uniprot entries by id
# X alignments/alignment_run/ # create alignment run
# X alignments/alignment/ # create alignment

#
# eu_alignment_blast_cigar
#
# X fetch alignment run by ID
# X fetch latest release mapping history ... (same as before) -> access ensembl species history
# X fetch latest alignments by type and assembly accession
# X create new alignment run
# X fetch transcripts
# X create alignment
# X create cigar
#
