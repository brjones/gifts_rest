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
    fixtures = [
        'ensembl_gene', 'ensembl_transcript', 'uniprot_entry',
        'cv_ue_status', 'mapping', 'ensembl_species_history',
        'release_mapping_history', 'alignment_run', 'alignment'
    ]

    def test_ensemblgene_request(self):
        gene = EnsemblGene.objects.filter(pk=2).values()
        self.assertEqual(gene[0]['gene_name'], 'RAD1')

    def test_ensembltranscript_request(self):
        transcript = EnsemblTranscript.objects.filter(pk=1).values()
        self.assertEqual(transcript[0]['gene_id'], 1)

    def test_alignment_alignments_run_request(self):
        client = APIClient()
        response = client.get('/alignments/alignment/alignment_run/1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['alignment_run'], 1)

    def test_alignment_request(self):
        client = APIClient()
        response = client.get('/alignments/alignment/1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['alignment_id'], 1)

    def test_alignments_assembly_request(self):
        client = APIClient()
        response = client.get('/alignments/alignment/latest/assembly/GRCh38/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['alignment_id'], 1)

    def test_alignment_run_request(self):
        client = APIClient()
        response = client.get('/alignments/alignment_run/1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['alignment_run_id'], 1)

    def test_alignment_run_post(self):
        client = APIClient()
        response = client.post(
            '/alignments/alignment_run/',
            data={
                'userstamp': 'test_userstamp',
                'time_run': '2019-05-01 00:00:00',
                'score1_type': 'perfect_match',
                'report_type': 'sp mapping value',
                'pipeline_name': 'test_loading',
                'pipeline_comment': 'test',
                'ensembl_release': 0,
                'uniprot_file_swissprot': '/test/location/sp.txt',
                'uniprot_file_isoform': '/test/location/iso.txt',
                'uniprot_dir_trembl': '/test/location/trembl',
                'logfile_dir': '/test/location/log.txt',
                'pipeline_script': 'testing_testing.sh',
                'score2_type': 'coverage',
                'release_mapping_history': 1
            }
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['alignment_run_id'], 2)

        client = APIClient()
        response = client.post(
            '/alignments/alignment/',
            data={
                'uniprot_id': 2,
                'score1': 1,
                'report': 'Alignment',
                'is_current': True,
                'score2': 1,
                'alignment_run': 2,
                'transcript': 2,
                'mapping': 2
            }
        )
        self.assertEqual(response.data['alignment_id'], 2)

    def test_cigar(self):
        print("Test")
