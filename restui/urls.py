from django.urls import path
from django.conf.urls import url
from restui.views import loaders, mappings

urlpatterns = [
    path('ensembl/load/<species>/<assembly_accession>/<int:ensembl_tax_id>/<int:ensembl_release>/', loaders.EnsemblFeature.as_view(), name='genome_detail'),
    path('mapping/<int:pk>/', mappings.Mapping.as_view()),
    path('comments/<int:pk>/', mappings.MappingComments.as_view()),
    path('mappings/', mappings.Mappings.as_view())
]
