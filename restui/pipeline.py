from django.utils import timezone
from psqlextra.query import ConflictAction

# flatten list of lists, i.e. list of transcripts for each gene
from itertools import chain

from restui.models.ensembl import EnsemblGene
from restui.models.ensembl import EnsemblTranscript
from restui.models.ensembl import EnsemblSpeciesHistory
from restui.models.ensembl import GeneHistory
from restui.models.ensembl import TranscriptHistory


def batched(data, size=100):
    gdata = []
    tdata = {}

    timestamp = timezone.now()

    # assume the iterable implements Sequence semantics
    length = len(data)

    """
    Transform incoming data for genes/transcripts in a way suitable for bulk insertion
    assume incoming data has list of transcripts nested into each gene
    map each ensg ID to the list of its transcripts, so that we can later
    assign the gene to each transcript for the transcripts bulk insert
    """
    for i, item in enumerate(data):

        # add timestamp to gene
        item['time_loaded'] = timestamp
        ensg_id = item.get('ensg_id')

        """
        Need to remove 'transcripts' from data as this is not part of the gene model
        NOTE: assume payload always contains non-empty transcripts data for each gene
        """

        tdata[ensg_id] = item.pop('transcripts')

        # add timestamp to gene's transcripts too
        for t in tdata[ensg_id]:
            t['time_loaded'] = timestamp
            
        gdata.append(dict(**item))

        if len(gdata) == size or i == length-1:
            yield gdata, tdata, i
            gdata = []
            tdata = {}


def bulk_upload(task, history, data):

    total_genes = len(data)

    task.update_state(state="LOADING SPECIES HISTORY TO DATABASE")
    # create new species history associated to this bulk upload
    species_history = EnsemblSpeciesHistory.objects.create(**history)
    # set temporary status
    species_history.status = 'LOAD_STARTED'
    species_history.save()

    # bulk insert the genes and transcripts in batches
    for gdata, tdata, current_number in batched(data, size=500):

        """
        Bulk insert the genes and transcripts
        WARNING
        From http://django-postgres-extra.readthedocs.io/manager/
        In order to stick to the "everything in one query" principle, various,
        more advanced usages of bulk_insert are impossible.
        It is not possible to have different rows specify different amounts of
        columns.
        """

        task.update_state(
            state="LOADING ENTRIES TO DATABASE",
            meta={
                'current': current_number,
                'total': total_genes,
            }
        )

        genes = EnsemblGene.objects.on_conflict(
            ['ensg_id'], ConflictAction.UPDATE
        ).bulk_insert(
            gdata,
            return_model=True
        )

        """
        Map each transcript data to its corresponding gene object,
        effectively establishing the gene-transcript one-to-many relationship
        use generator expression to reduce memory footprint
        """

        for gene in genes:
            for transcript_data in tdata[gene.ensg_id]:
                transcript_data["gene"] = gene

        # bulk insert the transcripts mapped to their genes
        transcripts = EnsemblTranscript.objects.on_conflict(
            ['enst_id'],
            ConflictAction.UPDATE
        ).bulk_insert(
            list(
                chain.from_iterable(tdata.values())
            ),
            return_model=True
        )

        """
        Insert genes and transcripts histories
        TODO: optimise, bulk_insert again?!
        UPDATE: tried bulk_insert, but receive a strange error:
                'column "ensembl_species_history" does not exist'
                HINT:  Perhaps you meant to reference the column:
                           "gene_history.ensembl_species_history_id"
                       or the column:
                           "excluded.ensembl_species_history_id".
        GeneHistory.objects.on_conflict(
            ['ensembl_species_history', 'gene'],
            ConflictAction.UPDATE
        ).bulk_insert(
            [dict(ensembl_species_history=history, gene=g) for g in genes ]
                )
        """

        for gene in genes:
            GeneHistory.objects.create(
                ensembl_species_history=species_history,
                gene=gene
            )

        for transcript in transcripts:
            TranscriptHistory.objects.create(
                ensembl_species_history=species_history,
                transcript=transcript
            )

    # WARNING: this generates datetime with microseconds and no UTC
    species_history.time_loaded = timezone.now()
    species_history.status = 'LOAD_COMPLETE'
    species_history.save()
