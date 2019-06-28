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

from sam_alignment_reconstructor.pairwise import pairwise_alignment
from sam_alignment_reconstructor.pairwise import cigar_split
from restui.lib.external import ensembl_sequence
from restui.lib.external import ensembl_protein


def fetch_pairwise(mapping):
    """
    Function to fetch the pairwise sequence alignment for a given mapping
    between a mapped sequence in ensembl and UniProt.

    Parameters
    ----------
    mappings

    Returns
    -------
    dict
        mapping_id : int
        alignments : list
            List of the alignments and the matching strings
    """

    pairwise_alignments = []

    enst = mapping.transcript.enst_id
    uniprot_id = mapping.uniprot.uniprot_acc

    for alignment in mapping.alignments.all():
        if alignment.alignment_run.score1_type == 'identity':
            pairwise_alignments.append(
                _fetch_alignment(alignment, enst, uniprot_id)
            )

            # Break out of the loop, we're done
            break

        elif (
                alignment.alignment_run.score1_type == 'perfect_match' and
                alignment.score1 == 1
        ):
            pairwise_alignments.append(
                _fetch_alignment(alignment, enst, uniprot_id)
            )

    return {
        'mapping_id': mapping.mapping_id,
        'alignments': pairwise_alignments
    }


def _fetch_alignment(alignment, enst, uniprot_id):
    """
    Parameters
    ----------
    alignment
    enst       : str
    uniprot_id : str

    Returns
    -------
    pw_alignment : dict
        Alignment object
    """
    ens_release = alignment.alignment_run.ensembl_release

    ensp = ensembl_protein(enst, ens_release)
    seq = ensembl_sequence(ensp, ens_release)

    ensembl_seq = seq
    uniprot_seq = seq

    match_str = '|' * len(seq)
    alignment_type = 'perfect_match'

    if alignment.alignment_run.score1_type == 'identity':
        cigarplus = alignment.pairwise.cigarplus
        mdz = alignment.pairwise.mdz

        if mdz.startswith('MD:Z:'):
            mdz = mdz[len('MD:Z:'):]

        uniprot_seq, match_str, ensembl_seq = pairwise_alignment(seq, cigarplus, mdz)

        alignment_type = 'identity'

    pw_alignment = {
        'uniprot_alignment': ensembl_seq,
        'ensembl_alignment': uniprot_seq,
        'match_str': match_str,
        'alignment_id': alignment.alignment_id,
        'ensembl_release': ens_release,
        'ensembl_id': ensp,
        'uniprot_id': uniprot_id,
        'alignment_type': alignment_type
    }

    return pw_alignment


def calculate_difference(cigar):
    """
    Calculate the difference between 2 sequences based on the cigar string

    Parameters
    ----------
    cigar : str

    Returns
    -------
    diff_count : int
    """
    diff_count = 0

    for c, op in cigar_split(cigar):
        if op in ('I', 'D', 'X'):
            diff_count += c

    return diff_count
