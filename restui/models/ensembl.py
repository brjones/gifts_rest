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

from collections import defaultdict

from django.db import models
from django.db.models import Count
from psqlextra.models import PostgresModel
from psqlextra.manager import PostgresManager, PostgresQuerySet
from django.db.models.deletion import CASCADE


class EnsemblSpeciesHistory(PostgresModel):
    objects = PostgresManager()

    ensembl_species_history_id = models.BigAutoField(primary_key=True)
    species = models.CharField(max_length=30, blank=True, null=True)
    assembly_accession = models.CharField(max_length=30, blank=True, null=True)
    ensembl_tax_id = models.BigIntegerField(blank=True, null=True)
    ensembl_release = models.BigIntegerField(blank=True, null=True)
    status = models.CharField(max_length=30, blank=True, null=True)
    time_loaded = models.DateTimeField(blank=True, null=True)
    alignment_status = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return "{0} - {1} {2} {3}".format(self.ensembl_species_history_id, self.species, self.assembly_accession, self.ensembl_tax_id, self.ensembl_release)

    class Meta:
        managed = False
        db_table = 'ensembl_species_history'


class EnsemblGene(PostgresModel):
    # override default Django manager
    objects = PostgresManager()

    gene_id = models.BigAutoField(primary_key=True)
    ensg_id = models.CharField(unique=True, max_length=30, blank=True, null=True)
    gene_name = models.CharField(max_length=255, blank=True, null=True)
    chromosome = models.CharField(max_length=50, blank=True, null=True)
    region_accession = models.CharField(max_length=50, blank=True, null=True)
    mod_id = models.CharField(max_length=30, blank=True, null=True)
    deleted = models.NullBooleanField()
    seq_region_start = models.BigIntegerField(blank=True, null=True)
    seq_region_end = models.BigIntegerField(blank=True, null=True)
    seq_region_strand = models.BigIntegerField(blank=True, null=True)
    biotype = models.CharField(max_length=40, blank=True, null=True)
    time_loaded = models.DateTimeField(blank=True, null=True)
    gene_symbol = models.CharField(max_length=30, blank=True, null=True)
    gene_accession = models.CharField(max_length=30, blank=True, null=True)
    source = models.CharField(max_length=30, blank=True, null=True)

    # history is not a column
    history = models.ManyToManyField(
        EnsemblSpeciesHistory,
        through='GeneHistory'
    )

    def __str__(self):
        return "{0} - {1} ({2})".format(self.gene_id, self.ensg_id, self.gene_name)

    class Meta:
        managed = False
        db_table = 'ensembl_gene'


class EnsemblTranscriptQuerySet(PostgresQuerySet):  # models.query.QuerySet
    """
    A specialised query set to be able to deal with groupings
    of transcripts based on their corresponding gene.

    Used for either efficiently paginate the unmapped ensembl entries
    """

    _counts = None

    def grouped_counts(self):
        """
        Retrieve a list of unique gene counts from a queryset.
        """

        if self._counts is None:
            self._counts = self.values(
                'gene'
            ).annotate(
                total=Count('gene')
            ).order_by('gene')

        return self._counts

    @property
    def grouped_count(self):
        """
        Retrieve the total number of transcript groups (i.e. genes) from a queryset.
        """

        return len(self.grouped_counts())

    def grouped_slice(self, offset, limit):
        """
        Fetch a subset of EnsemblTranscript instances grouped by gene.
        """

        counts = self.grouped_counts()

        if offset == 0:
            qs_offset = 0
        else:
            qs_offset = sum(int(row['total']) for row in counts[:offset])

        qs_limit = sum(int(row['total']) for row in counts[offset:offset+limit])

        sub_qs = self.order_by('gene')[qs_offset:qs_offset+qs_limit]

        grouped_results = defaultdict(list)
        for result in sub_qs:
            grouped_results[result.gene.ensg_id].append(result)

        return grouped_results


class EnsemblTranscriptManager(PostgresManager):
    def get_queryset(self):
        return EnsemblTranscriptQuerySet(self.model, using=self._db)


class EnsemblTranscript(PostgresModel):
    objects = EnsemblTranscriptManager()

    transcript_id = models.BigAutoField(primary_key=True)
    gene = models.ForeignKey(EnsemblGene, models.DO_NOTHING, blank=True, null=True)
    enst_id = models.CharField(unique=True, max_length=30, blank=True, null=True)
    enst_version = models.SmallIntegerField(blank=True, null=True)
    ccds_id = models.CharField(max_length=30, blank=True, null=True)
    uniparc_accession = models.CharField(max_length=30, blank=True, null=True)
    biotype = models.CharField(max_length=40, blank=True, null=True)
    deleted = models.NullBooleanField()
    seq_region_start = models.BigIntegerField(blank=True, null=True)
    seq_region_end = models.BigIntegerField(blank=True, null=True)
    supporting_evidence = models.CharField(max_length=45, blank=True, null=True)
    userstamp = models.CharField(max_length=30, blank=True, null=True)
    time_loaded = models.DateTimeField(blank=True, null=True)
    select = models.NullBooleanField()
    ensp_id = models.CharField(max_length=30, blank=True, null=True)
    ensp_len = models.IntegerField(blank=True, null=True)
    source = models.CharField(max_length=30, blank=True, null=True)

    # history is not a column
    history = models.ManyToManyField(
        EnsemblSpeciesHistory,
        through='TranscriptHistory'
    )

    def __str__(self):
        return "{0} - {1} ({2})".format(self.transcript_id, self.enst_id, self.gene)

    class Meta:
        managed = False
        db_table = 'ensembl_transcript'


class EnspUCigar(models.Model):
    alignment = models.OneToOneField(
        'Alignment',
        primary_key=True,
        on_delete=CASCADE,
        related_name='pairwise'
    )
    cigarplus = models.TextField(blank=True, null=True)
    mdz = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ensp_u_cigar'


class GeneHistory(PostgresModel):
    objects = PostgresManager()

    ensembl_species_history = models.ForeignKey(
        EnsemblSpeciesHistory,
        models.DO_NOTHING,
        primary_key=True
    )
    gene = models.ForeignKey(EnsemblGene, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'gene_history'
        unique_together = (('ensembl_species_history', 'gene'),)


class TranscriptHistory(PostgresModel):
    objects = PostgresManager()

    ensembl_species_history = models.ForeignKey(
        EnsemblSpeciesHistory,
        models.DO_NOTHING,
        primary_key=True
    )
    transcript = models.ForeignKey(EnsemblTranscript, models.DO_NOTHING)
    grouping_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transcript_history'
        unique_together = (('ensembl_species_history', 'transcript'),)
