from django.urls import path
from django.conf.urls import url
from restui.views import ensembl, mappings

urlpatterns = [
    path('ensembl/load/<species>/<assembly_accession>/<int:ensembl_tax_id>/<int:ensembl_release>/', ensembl.EnsemblFeature.as_view(), name='genome_detail'),
    path('mapping/<int:pk>/status/', mappings.MappingStatusView.as_view()),
    path('mapping/<int:pk>/comments/', mappings.MappingCommentView.as_view()),
    path('mapping/<int:pk>/labels/<label>/', mappings.DeleteMappingLabelView.as_view()),
    path('mapping/<int:pk>/labels/', mappings.CreateMappingLabelView.as_view()),
    path('mapping/<int:pk>/', mappings.MappingView.as_view()),
    path('comments/<int:pk>/', mappings.MappingCommentsView.as_view()),
    path('mappings/', mappings.MappingsView.as_view()),
]
