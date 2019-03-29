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

from restui.lib.external import ensembl_sequence, ensembl_protein
from sam_alignment_reconstructor.pairwise import pairwise_alignment, cigar_split


def fetch_pairwise(mapping):

    pairwise_alignments = []

    enst = mapping.transcript.enst_id
    uniprot_id = mapping.uniprot.uniprot_acc

    for alignment in mapping.alignments.all():
        if alignment.alignment_run.score1_type == 'identity':
            cigarplus = alignment.pairwise.cigarplus
            mdz = alignment.pairwise.mdz

            if mdz.startswith('MD:Z:'):
                mdz = mdz[len('MD:Z:'):]

            ens_release = alignment.alignment_run.ensembl_release

            ensp = ensembl_protein(enst, ens_release)
            seq = ensembl_sequence(ensp, ens_release)

            uniprot_seq, match_str, ensembl_seq = pairwise_alignment(seq, cigarplus, mdz)

            pairwise_alignments.append({'uniprot_alignment': uniprot_seq,
                                        'ensembl_alignment': ensembl_seq,
                                        'match_str': match_str,
                                        'alignment_id': alignment.alignment_id,
                                        'ensembl_release': ens_release,
                                        'ensembl_id': ensp,
                                        'uniprot_id': uniprot_id,
                                        'alignment_type': 'identity'})

            # Break out of the loop, we're done
            break

        elif alignment.alignment_run.score1_type == 'perfect_match' and alignment.score1 == 1:
            ens_release = alignment.alignment_run.ensembl_release

            ensp = ensembl_protein(enst, ens_release)
            seq = ensembl_sequence(ensp, ens_release)

            pairwise_alignments.append({'uniprot_alignment': seq,
                                        'ensembl_alignment': seq,
                                        'match_str': '|' * len(seq),
                                        'alignment_id': alignment.alignment_id,
                                        'ensembl_release': ens_release,
                                        'ensembl_id': ensp,
                                        'uniprot_id': uniprot_id,
                                        'alignment_type': 'perfect_match'})


    return {'mapping_id': mapping.mapping_id,
            'alignments': pairwise_alignments}


def calculate_difference(cigar):
    diff_count = 0

    for c, op in cigar_split(cigar):
        if op == 'I' or op == 'D' or op == 'X':
            diff_count += c

    return diff_count
