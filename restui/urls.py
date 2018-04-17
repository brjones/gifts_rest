from django.conf.urls import url
from restui.views import loaders

urlpatterns = [
    url('ensembl/load', loaders.EnsemblFeature.as_view(), name='genome_detail'),
]
