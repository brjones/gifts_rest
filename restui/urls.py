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
    # path('alignments/perfect_matches/'),                                              # GIFTS:fetch_latest_uniprot_enst_perfect_matches, doesn't seem to be used, skip at the moment
    
    path('ensembl/load/<species>/<assembly_accession>/<int:ensembl_tax_id>/<int:ensembl_release>/', # genes/transcripts bulk load
         ensembl.EnsemblFeature.as_view()),
    path('ensembl/release/latest/assembly/<assembly_accession>/',                                   # fetch latest ensembl release (status load complete)
         ensembl.LatestEnsemblRelease.as_view()),
    path('ensembl/species_history/<int:pk>/', ensembl.SpeciesHistory.as_view()),                    # fetch species history by ID
    path('ensembl/transcript/<int:pk>/', ensembl.Transcript.as_view()),                             # fetch transcript by ID
    path('ensembl/cigar/align_run/<int:run>/uniprot/<acc>/<int:seq_version>/transcript/<enst_id>/', # fetch alignment by align run/uniprot/transcript
         ensembl.EnspUCigarFetch.as_view()),
    path('ensembl/cigar/', ensembl.EnspUCigarCreate.as_view()),                                     # insert cigar/mdz

    # path('mappings/release_mapping_history/latest/assembly/<accession>'),           # retrieve the mappings for the latest (by ensembl species history time loaded) release_mapping_history by assembly accession
    # path('mappings/release_mapping_history/<int:pk>/'),                             # GIFTS:get_info_from_perfect_match_alignment_run, doesn't seem to be used, skip at the moment
    # path('mapping/<int:pk>/perfect/'),                                              # GIFTS:is_perfect_eu_match_mapping_id, , doesn't seem to be used, skip at the moment
    path('mapping/<int:pk>/labels/<label_id>/', mappings.MappingLabelView.as_view()), # add/delete a label to a mapping
    path('mapping/<int:pk>/labels/', mappings.MappingLabelsView.as_view()),           # retrieve all labels of a mapping
    path('mapping/<int:pk>/comments/', mappings.MappingCommentsView.as_view()),       # add comment/retrieve all comments of a mapping
    path('mapping/<int:pk>/status/', mappings.MappingStatusView.as_view()),           # update mapping status
    # path('mapping/<int:pk>/pairwise/', mappings.MappingPairwiseAlignment.as_view()),  # retrieve pairwise alignments for a mapping
    path('mapping/<int:pk>/', mappings.MappingView.as_view()),                        # retrieve single mapping
    path('mappings/stats/', mappings.MappingStatsView.as_view()),                     # retrieve mapping stats
    path('mappings/', mappings.MappingsView.as_view()),                               # search the mappings

    path('uniprot/entry/<int:pk>/', uniprot.UniprotEntryFetch.as_view()),             # fetch uniprot entry by db ID
]
