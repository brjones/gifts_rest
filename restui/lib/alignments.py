from restui.models.mappings import Mapping
from restui.lib.external import ensembl_sequence
from sam_alignment_reconstructor.pairwise import pairwise_alignment

def fetch_pairwise(mapping_id):
    
    mapping = Mapping.objects.prefetch_related('alignments').select_related('transcript').select_related('uniprot').get(pk=mapping_id)
    
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
            
            seq = ensembl_sequence(enst, ens_release)
            
            uniprot_seq, match_str, ensembl_seq = pairwise_alignment(seq, cigarplus, mdz)
            
            pairwise_alignments.append({'uniprot_alignment': uniprot_seq,
                                        'ensembl_alignment': ensembl_seq,
                                        'match_str': match_str,
                                        'alignment_id': alignment.alignment_id,
                                        'ensembl_release': ens_release,
                                        'ensembl_id': enst,
                                        'uniprot_id': uniprot_id})

    return {'mapping_id': mapping_id,
            'alignments': pairwise_alignments}
