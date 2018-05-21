from django.db import models
from psqlextra.models import PostgresModel
from psqlextra.manager import PostgresManager

class EnsemblGene(PostgresModel):
    # override default Django manager
    objects = PostgresManager()
    
    gene_id = models.BigAutoField(primary_key=True)
    ensg_id = models.CharField(unique=True, max_length=30, blank=True, null=True)
    gene_name = models.CharField(max_length=30, blank=True, null=True)
    chromosome = models.CharField(max_length=50, blank=True, null=True)
    region_accession = models.CharField(max_length=50, blank=True, null=True)
    mod_id = models.CharField(max_length=30, blank=True, null=True)
    deleted = models.NullBooleanField()
    seq_region_start = models.BigIntegerField(blank=True, null=True)
    seq_region_end = models.BigIntegerField(blank=True, null=True)
    seq_region_strand = models.BigIntegerField(blank=True, null=True)
    biotype = models.CharField(max_length=40, blank=True, null=True)
    time_loaded = models.DateTimeField(blank=True, null=True)
    history = models.ManyToManyField(EnsemblSpeciesHistory, through='GeneHistory')
    
    class Meta:
        managed = False
        db_table = 'ensembl_gene'


class EnsemblSpeciesHistory(models.Model):
    ensembl_species_history_id = models.BigAutoField(primary_key=True)
    species = models.CharField(max_length=30, blank=True, null=True)
    assembly_accession = models.CharField(max_length=30, blank=True, null=True)
    ensembl_tax_id = models.BigIntegerField(blank=True, null=True)
    ensembl_release = models.BigIntegerField(blank=True, null=True)
    status = models.CharField(max_length=30, blank=True, null=True)
    time_loaded = models.DateTimeField(blank=True, null=True)
    
    
    class Meta:
        managed = False
        db_table = 'ensembl_species_history'


class EnsemblTranscript(models.Model):
    transcript_id = models.BigAutoField(primary_key=True)
    gene = models.ForeignKey(EnsemblGene, models.DO_NOTHING, blank=True, null=True)
    enst_id = models.CharField(max_length=30, blank=True, null=True)
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
    history = models.ManyToManyField(EnsemblSpeciesHistory, through='TranscriptHistory')
    
    class Meta:
        managed = False
        db_table = 'ensembl_transcript'




class EnspUCigar(models.Model):
    ensp_u_cigar_id = models.BigAutoField(primary_key=True)
    cigarplus = models.TextField(blank=True, null=True)
    mdz = models.TextField(blank=True, null=True)
    uniprot_acc = models.CharField(max_length=30)
    uniprot_seq_version = models.SmallIntegerField()
    ensp_id = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'ensp_u_cigar'


class GeneHistory(models.Model):
    ensembl_species_history = models.ForeignKey(EnsemblSpeciesHistory, models.DO_NOTHING, primary_key=True)
    gene = models.ForeignKey(EnsemblGene, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'gene_history'
        unique_together = (('ensembl_species_history', 'gene'),)

class TranscriptHistory(models.Model):
    ensembl_species_history = models.ForeignKey(EnsemblSpeciesHistory, models.DO_NOTHING, primary_key=True)
    transcript = models.ForeignKey(EnsemblTranscript, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'transcript_history'
        unique_together = (('ensembl_species_history', 'transcript'),)
