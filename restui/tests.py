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

import mock

from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from django.http import Http404
from django.db import connection

from restui.models.ensembl import EnsemblGene
from restui.models.ensembl import EnsemblTranscript
from restui.models.ensembl import EnsemblSpeciesHistory
from restui.models.ensembl import TranscriptHistory
from restui.models.ensembl import EnspUCigar
from restui.models.mappings import Mapping
from restui.models.mappings import MappingView
from restui.models.mappings import MappingHistory

from restui.lib import alignments
from restui.lib import external
from restui.views import mappings
from restui.views import unmapped


class EnsemblTest(APITestCase):
    fixtures = [
        'ensembl_gene', 'ensembl_transcript', 'uniprot_entry',
        'cv_ue_status', 'mapping', 'ensembl_species_history',
        'release_mapping_history', 'alignment_run', 'alignment',
        'ensp_u_cigar', 'transcript_history', 'cv_entry_type',
        'mapping_view', 'mapping_history', 'release_stats', 'cv_ue_label',
        'aap_auth_aapuser', 'ue_mapping_label', 'ue_unmapped_entry_label'
    ]

    # Test that data is present in the test db

    def test_ensemblgene_request(self):
        gene = EnsemblGene.objects.filter(pk=2).values()
        self.assertEqual(gene[0]['gene_name'], 'RAD1')

    def test_ensembltranscript_request(self):
        transcript = EnsemblTranscript.objects.filter(pk=2).values()
        self.assertEqual(transcript[0]['gene_id'], 1)

    def test_ensembl_species_history_request(self):
        mapping = mappings.get_mapping(1)
        ensembl_species_history = EnsemblSpeciesHistory.objects.filter(
            transcripthistory__transcript=mapping.transcript
        ).latest('time_loaded')
        self.assertEqual(ensembl_species_history.assembly_accession, 'GRCh37')

        mapping = mappings.get_mapping(2)
        ensembl_species_history = EnsemblSpeciesHistory.objects.filter(
            transcripthistory__transcript=mapping.transcript
        ).latest('time_loaded')
        self.assertEqual(ensembl_species_history.assembly_accession, 'GRCh38')

        mapping = mappings.get_mapping(3)
        ensembl_species_history = EnsemblSpeciesHistory.objects.filter(
            transcripthistory__transcript=mapping.transcript
        ).latest('time_loaded')
        self.assertEqual(ensembl_species_history.assembly_accession, 'GRCh38')

        mapping = mappings.get_mapping(4)
        ensembl_species_history = EnsemblSpeciesHistory.objects.filter(
            transcripthistory__transcript=mapping.transcript
        ).latest('time_loaded')
        self.assertEqual(ensembl_species_history.assembly_accession, 'GRCh38')

        mock_mapping = mock.Mock(spec=Mapping)
        mock_mapping.transcript = 2

        ensembl_species_history = EnsemblSpeciesHistory.objects.filter(
            transcripthistory__transcript=mock_mapping.transcript
        ).latest('time_loaded')
        self.assertEqual(ensembl_species_history.assembly_accession, 'GRCh38')



    ###############
    # /alignments #
    ###############

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
        self.assertEqual(response.data['results'][0]['alignment_id'], 2)

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
        self.assertEqual(response.data['alignment_run_id'], 3)

        client = APIClient()
        response = client.post(
            '/alignments/alignment/',
            data={
                'uniprot_id': 2,
                'score1': 1,
                'report': 'Alignment',
                'is_current': True,
                'score2': 1,
                'alignment_run': 3,
                'transcript': 2,
                'mapping': 2
            }
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['alignment_id'], 4)

    ############
    # /ensembl #
    ############

    def test_cigar_post(self):
        client = APIClient()
        response_1 = client.post(
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

        response_2 = client.post(
            '/alignments/alignment/',
            data={
                'uniprot_id': 2,
                'score1': 1,
                'report': 'Alignment',
                'is_current': True,
                'score2': 1,
                'alignment_run': response_1.data['alignment_run_id'],
                'transcript': 2,
                'mapping': 2
            }
        )

        response_3 = client.post(
            '/ensembl/cigar/',
            data={
                'alignment': response_2.data['alignment_id'],
                'cigarplus': 'M',
                'mdz': 'abcd'
            }
        )
        self.assertEqual(response_3.status_code, 201)
        self.assertEqual(
            response_3.data['alignment'],
            response_2.data['alignment_id']
        )

    def test_cigar_align_run_request(self):
        client = APIClient()
        response = client.get(
            '/ensembl/cigar/align_run/2/uniprot/P51587/1/transcript/ENST00000380152.7/'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['alignment'], 3)

    def test_cigar_alignment_get_request(self):
        client = APIClient()
        response = client.get('/ensembl/cigar/alignment/1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['alignment'], 1)

    # def test_cigar_alignment_put_request(self):
    #     client = APIClient()
    #     response = client.get('/ensembl/cigar/alignment/1/')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['alignment'], 1)

    # def test_cigar_alignment_patch_request(self):
    #     client = APIClient()
    #     response = client.get('/ensembl/cigar/alignment/1/')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['alignment'], 1)

    def test_latest_assembly_request(self):
        client = APIClient()
        response = client.get('/ensembl/release/latest/assembly/GRCh38/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['release'], 95)

    def test_spp_history_post(self):
        client = APIClient()
        response = client.post(
            '/ensembl/species_history/1/alignment_status/ALIGNMENT_TEST/'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['alignment_status'], 'ALIGNMENT_TEST')

    def test_spp_history_request(self):
        client = APIClient()
        response = client.get('/ensembl/species_history/2/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['assembly_accession'], 'GRCh38')
        self.assertEqual(response.data['alignment_status'], 'ALIGNMENT_COMPLETE')

    def test_transcript_request(self):
        client = APIClient()
        response = client.get('/ensembl/transcript/2/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['enst_id'], 'ENST00000380152.7')

    ############
    # /mapping #
    ############

    def test_mapping_functions(self):
        with self.assertRaises(Http404):
            mapping = mappings.get_mapping(99)

        mapping = mappings.get_mapping(3)
        self.assertEqual(mapping.transcript.gene.gene_name, 'BRCA2')
        self.assertEqual(mapping.uniprot.uniprot_acc, 'P51587')

        with self.assertRaises(Http404):
            mock_mapping = mock.Mock(spec=Mapping)
            mock_mapping.transcript = 99
            tax = mappings.build_taxonomy_data(
                mock_mapping
            )

        tax = mappings.build_taxonomy_data(mapping)
        self.assertEqual(tax['ensemblTaxId'], 9606)

        related_mappings = mappings.build_related_mappings_data(mapping),
        self.assertEqual(related_mappings[0][0]['mappingId'], 4)
        self.assertEqual(
            related_mappings[0][0]['ensemblTranscript']['ensgId'],
            'ENSG00000139618'
        )
        self.assertEqual(
            related_mappings[0][0]['ensemblTranscript']['ensgName'],
            'BRCA2'
        )
        self.assertEqual(
            related_mappings[0][0]['ensemblTranscript']['enstId'],
            'ENST00000380152.7'
        )
        self.assertEqual(
            related_mappings[0][0]['uniprotEntry']['uniprotAccession'],
            'O60671'
        )

        unrelated_mappings = mappings.build_related_unmapped_entries_data(mapping)
        print("\nUNRELATED MAPPINGS:", unrelated_mappings)
        self.assertEqual(unrelated_mappings['ensembl'], [])

    def test_mapping_request(self):
        client = APIClient()
        response = client.get('/mapping/1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['mapping']['mappingId'], 1)

    def test_mapping_labels_request(self):
        mapping = mappings.get_mapping(1)
        mapped_label = mapping.labels.values_list('label', flat=True)[0]

        client = APIClient()
        response = client.get('/mapping/1/labels/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['labels'][mapped_label-1]['status'], True)

    def test_mapping_pairwise_request(self):
        client = APIClient()
        response = client.get('/mapping/1/pairwise/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['mapping_id'], 1)

    ## This is a function that is not publically available
    # def test_mapping_status_request(self):
    #     client = APIClient()
    #     response = client.put(
    #         '/mapping/1/status/',
    #         data={}
    #     )
    #     print(response)
    #     print(response.data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['labels'], [])

    #############
    # /mappings #
    #############

    def test_mappings_request(self):
        client = APIClient()
        response = client.get('/mappings/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 3)

    def test_mappings_release_request(self):
        client = APIClient()
        response = client.get('/mappings/release/9606/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['ensembl'], 95)
        self.assertEqual(response.data['uniprot'], '2019_05')

    def test_mappings_release_history_latest_request(self):
        client = APIClient()
        response = client.get('/mappings/release_history/latest/assembly/GRCh38/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'MAPPING_COMPLETED')

    def test_mappings_release_history_request(self):
        """
        This raises an UnorderedObjectListWarning
        """
        client = APIClient()
        response = client.get('/mappings/release_history/1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_mappings_stats_request(self):
        client = APIClient()
        response = client.get('/mappings/stats/9606/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(isinstance(response.data, dict), True)

    def test_mappings_status_request(self):
        client = APIClient()
        response = client.get('/mappings/statuses/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['id'], 1)
        self.assertEqual(response.data[0]['description'], 'testing')

    ############
    # /service #
    ############

    def test_service_ping(self):
        client = APIClient()
        response = client.get('/service/ping/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['ping'], 0)

    ############
    # /uniprot #
    ############

    def test_uniprot_request(self):
        client = APIClient()
        response = client.get('/uniprot/entry/2/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['uniprot_acc'], 'O60671')

    #############
    # /unmapped #
    #############

    def test_get_uniprot_entry(self):
        uniprot_entry = unmapped.get_uniprot_entry(1)
        self.assertEqual(uniprot_entry.uniprot_acc, "P51587")

    def test_unmapped_request(self):
        client = APIClient()
        response = client.get('/unmapped/2/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['entry']['uniprot_acc'], "P54792")

    def test_unmapped_labels_request(self):
        uniprot_entry = unmapped.get_uniprot_entry(4)
        mapped_label = uniprot_entry.labels.values_list('label', flat=True)[0]

        client = APIClient()
        response = client.get('/unmapped/4/labels/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['labels'][mapped_label-1]['status'],
            True
        )

    def test_unmapped_tax_source_request(self):
        client = APIClient()
        response = client.get('/unmapped/9606/ensembl/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['results'][0]['transcripts'][0]['enstId'],
            'ENST00000544455.5'
        )


class LibAlignment(APITestCase):

    fixtures = [
        'ensembl_gene', 'ensembl_transcript', 'uniprot_entry',
        'cv_ue_status', 'mapping', 'ensembl_species_history',
        'release_mapping_history', 'alignment_run', 'alignment',
        'ensp_u_cigar', 'transcript_history', 'cv_entry_type',
        'mapping_history'
    ]

    def test_fetch_pairwise(self):
        mapping = Mapping.objects.prefetch_related(
            'alignments'
        ).select_related(
            'transcript'
        ).select_related(
            'uniprot'
        ).get(pk=3)

        pwaln = alignments.fetch_pairwise(mapping)

        self.assertEqual(
            pwaln['alignments'][0]['uniprot_alignment'][0:7],
            'MPIGSKE'
        )
        self.assertEqual(
            pwaln['alignments'][0]['ensembl_alignment'][0:7],
            'MPIGSKE'
        )

    def test_fetch_alignment(self):
        mapping = Mapping.objects.prefetch_related(
            'alignments'
        ).select_related(
            'transcript'
        ).select_related(
            'uniprot'
        ).get(pk=3)

        enst = mapping.transcript.enst_id
        uniprot_id = mapping.uniprot.uniprot_acc
        mapped_aln = mapping.alignments.all()

        aln = alignments._fetch_alignment(mapped_aln[0], enst, uniprot_id)
        self.assertEqual(aln['uniprot_alignment'][0:7], 'MPIGSKE')

    def test_calculate_difference(self):
        diff = alignments.calculate_difference('3M1I3M1D5M')
        self.assertEqual(diff, 2)


class LibExternal(APITestCase):

    def test_tark_transcript(self):
        tark_entry = external.tark_transcript('ENST00000382038', 95)
        self.assertEqual(tark_entry['stable_id'], 'ENST00000382038')

    def test_ensembl_current_release(self):
        e_release = external.ensembl_current_release()
        self.assertEqual(isinstance(e_release,int), True)

    def test_ensembl_sequence(self):
        seq = external.ensembl_sequence('ENST00000382038', 95)
        self.assertEqual(seq[0:7], 'GCTTGCC')

    def test_ensembl_protein(self):
        prot = external.ensembl_protein('ENST00000382038', 95)
        self.assertEqual(prot, 'ENSP00000371469')
