from django.urls import path
from django.conf.urls import url
from restui.views import ensembl, mappings
#from restui.views import alignments, ensembl, mappings

urlpatterns = [
#     path('alignments/alignment_run/<int:pk>/', alignments.AlignmentRunFetch.as_view()),    # retrieve alignment run by ID (GET)
#     path('alignments/alignment_run/', alignments.AlignmentRunCreate.as_view()),            # insert alignment run (POST),
#     path('alignments/alignment/latest/assembly/<assembly_accession>/', alignments.LatestAlignmentsFetch.as_view()), # retrieve latest alignments by assembly accession (GET)
#     path('alignments/alignment/<int:pk>/', alignments.AlignmentFetch.as_view()),           # retrieve alignment by ID (GET)
#     path('alignments/alignment/', alignments.AlignmentCreate.as_view()),                   # insert alignment (POST)
    # path('alignments/perfect_matches/'), # fetch_latest_uniprot_enst_perfect_matches
    
    path('ensembl/load/<species>/<assembly_accession>/<int:ensembl_tax_id>/<int:ensembl_release>/', ensembl.EnsemblFeature.as_view()),
#    path('ensembl/assembly/<assembly_accession>/release/latest/', ensembl.LatestEnsemblRelease.as_view()), # fetch latest ensembl release (status load complete) (GET)
#    path('ensembl/species_history/<int:pk>/', ensembl.SpeciesHistoryFetch.as_view()), # fetch species history by ID (GET)
#    path('ensembl/transcript/<int:pk>/', ensembl.TranscriptFetch.as_view()),          # fetch transcript by ID (GET)
    ########
    # NOTE
    # this is yet to be discussed, don't know whether multiple values are allowed, and EnspUCigar schema might change
    #
#    path('ensembl/cigar/uniprot_acc/<uniprot_acc>/uniprot_seq_version/<int:uniprot_seq_version>/ensp_id/<ensp_id>/', ensembl.EnspUCigarFetch.as_view()), # fetch_cigarmdz
    ########
#    path('ensembl/cigar/', ensembl.EnspUCigarCreate.as_view()), # insert cigarmdz (POST)
    
    # path('mapping/<int:pk>/perfect/'), # is_perfect_eu_match_mapping_id
    path('mapping/<int:pk>/status/', mappings.MappingStatusView.as_view()),
    path('mapping/<int:pk>/comments/', mappings.MappingCommentView.as_view()),
    path('mapping/<int:pk>/labels/<label>/', mappings.DeleteMappingLabelView.as_view()),
    path('mapping/<int:pk>/labels/', mappings.CreateMappingLabelView.as_view()),
    path('mapping/<int:pk>/', mappings.MappingView.as_view()),
    path('comments/<int:pk>/', mappings.MappingCommentsView.as_view()),
#    path('labels/', mappings.LabelsView.as_view()),                                      # retrieve list of possible labels (GET)
    path('mappings/', mappings.MappingsView.as_view()),                                  # search the mappings (GET)

    # path('mappings/release_mapping_history/latest/assembly/<accession>'), # retrieve the mappings for the latest (by ensembl species history time loaded) release_mapping_history by assembly accession (GET)
    # path('mappings/release_mapping_history/<int:pk>/'), # get_info_from_perfect_match_alignment_run
]
