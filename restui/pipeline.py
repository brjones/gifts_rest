from itertools import chain # flatten list of lists, i.e. list of transcripts for each gene

from django.utils import timezone
from psqlextra.query import ConflictAction

from restui.models.ensembl import EnsemblGene, EnsemblTranscript,\
    EnsemblSpeciesHistory, GeneHistory, TranscriptHistory

def batched(data, size=100):
    gdata = []
    tdata = {}

    timestamp = timezone.now()
    length = len(data) # assume the iterable implements Sequence semantics

    # transform incoming data for genes/transcripts in a way suitable for bulk insertion
    #
    # assume incoming data has list of transcripts nested into each gene
    # map each ensg ID to the list of its transcripts, so that we can later
    # assign the gene to each transcript for the transcripts bulk insert
    for i, item in enumerate(data):
        item['time_loaded'] = timestamp # add timestamp to gene
        ensg_id = item.get('ensg_id')

        # need to remove 'transcripts' from data as this is not part of the gene model
        # NOTE: assume payload always contains non-empty transcripts data for each gene
        tdata[ensg_id] = item.pop('transcripts')

        for t in tdata[ensg_id]: # add timestamp to gene's transcripts too
            t['time_loaded'] = timestamp
            
        gdata.append(dict(**item))

        if len(gdata) == size or i == length-1:
            yield gdata, tdata
            gdata = []
            tdata = {}

def bulk_upload(history, data):
    # create new species history associated to this bulk upload
    species_history = EnsemblSpeciesHistory.objects.create(**history)
    species_history.status = 'LOAD_STARTED' # set temporary status
    species_history.save()

    # bulk insert the genes and transcripts in batches
    for gdata, tdata in batched(data, size=500):
        #
        # WARNING
        #
        # From http://django-postgres-extra.readthedocs.io/manager/
        # In order to stick to the "everything in one query" principle, various, more advanced usages of bulk_insert are impossible.
        # It is not possible to have different rows specify different amounts of columns.
        #
        genes = EnsemblGene.objects.on_conflict(['ensg_id'], ConflictAction.UPDATE).bulk_insert(gdata, return_model=True)

        # map each transcript data to its corresponding gene object,
        # effectively establishing the gene-transcript one-to-many relationship
        # use generator expression to reduce memory footprint
        for t, g in ( (transcript_data, gene) for gene in genes for transcript_data in tdata[gene.ensg_id] ):
            # bulk insert the transcripts mapped to their genes
            t["gene"] = g
            transcripts = EnsemblTranscript.objects.on_conflict(['enst_id'],
                                                                ConflictAction.UPDATE).bulk_insert(list(chain.from_iterable(tdata.values())),
                                                                                                   return_model=True)

            # insert genes and trascripts histories
            # TODO: optimise, bulk_insert again?!
            # UPDATE: tried bulk_insert, but receive a strange error:
            #         'column "ensembl_species_history" does not exist'
            #         HINT:  Perhaps you meant to reference the column "gene_history.ensembl_species_history_id"
            #                or the column "excluded.ensembl_species_history_id".
            #
            # GeneHistory.objects.on_conflict(['ensembl_species_history', 'gene'],
            #                                ConflictAction.UPDATE).bulk_insert([ dict(ensembl_species_history=history, gene=g) for g in genes ])
            for gene in genes:
                GeneHistory.objects.create(ensembl_species_history=species_history, gene=gene)
            for transcript in transcripts:
                TranscriptHistory.objects.create(ensembl_species_history=species_history, transcript=transcript)

    species_history.time_loaded = timezone.now() # WARNING: this generates datetime with microseconds and no UTC
    species_history.status = 'LOAD_COMPLETE'
    species_history.save()
