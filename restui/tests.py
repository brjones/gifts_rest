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

import json
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from restui.models.ensembl import EnsemblGene
from restui.models.ensembl import EnsemblTranscript


class ServiceTest(APITestCase):
    def test_ping(self):
        client = APIClient()
        response = client.get('/service/ping/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['ping'], 0)


class EnsemblTest(APITestCase):
    fixtures = ['ensembl_gene', 'ensembl_transcript']

    def test_ensemblgene_request(self):
        gene = EnsemblGene.objects.filter(pk=2).values()
        self.assertEqual(gene[0]['gene_name'], 'RAD1')

    def test_ensembltranscript_request(self):
        transcript = EnsemblTranscript.objects.filter(pk=1).values()
        self.assertEqual(transcript[0]['gene_id'], 1)

    def test_(self):
