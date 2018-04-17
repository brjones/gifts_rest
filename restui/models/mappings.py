from django.db import models

class Alignment(models.Model):
    alignment_id = models.BigAutoField(primary_key=True)
    alignment_run = models.ForeignKey('AlignmentRun', models.DO_NOTHING)
    uniprot = models.ForeignKey('Uniprot', models.DO_NOTHING, blank=True, null=True)
    transcript = models.ForeignKey('EnsemblTranscript', models.DO_NOTHING, blank=True, null=True)
    mapping = models.ForeignKey('EnsemblUniprot', models.DO_NOTHING, blank=True, null=True)
    score1 = models.FloatField(blank=True, null=True)
    report = models.CharField(max_length=300, blank=True, null=True)
    is_current = models.NullBooleanField()
    score2 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alignment'


class AlignmentRun(models.Model):
    alignment_run_id = models.BigAutoField(primary_key=True)
    userstamp = models.CharField(max_length=30, blank=True, null=True)
    time_run = models.DateTimeField(blank=True, null=True)
    score1_type = models.CharField(max_length=30, blank=True, null=True)
    report_type = models.CharField(max_length=30, blank=True, null=True)
    pipeline_name = models.CharField(max_length=30)
    pipeline_comment = models.CharField(max_length=300)
    mapping_history = models.ForeignKey('MappingHistory', models.DO_NOTHING)
    ensembl_release = models.BigIntegerField()
    uniprot_file_swissprot = models.CharField(max_length=300, blank=True, null=True)
    uniprot_file_isoform = models.CharField(max_length=300, blank=True, null=True)
    uniprot_dir_trembl = models.CharField(max_length=300, blank=True, null=True)
    logfile_dir = models.CharField(max_length=300, blank=True, null=True)
    pipeline_script = models.CharField(max_length=300)
    score2_type = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alignment_run'

class EnsemblUniprot(models.Model):
    mapping_id = models.BigAutoField(primary_key=True)
    uniprot = models.ForeignKey('Uniprot', models.DO_NOTHING, blank=True, null=True)
    userstamp = models.CharField(max_length=30, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    mapping_history_id = models.BigIntegerField(blank=True, null=True)
    transcript = models.ForeignKey('EnsemblTranscript', models.DO_NOTHING, blank=True, null=True)
    sp_ensembl_mapping_type = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ensembl_uniprot'

class GeneName(models.Model):
    gene_name_id = models.BigAutoField(primary_key=True)
    uniprot = models.ForeignKey('Uniprot', models.DO_NOTHING, blank=True, null=True)
    gene_symbol = models.CharField(max_length=45, blank=True, null=True)
    gene_name_type_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gene_name'


class Isoform(models.Model):
    isoform_id = models.BigAutoField(primary_key=True)
    uniprot = models.ForeignKey('Uniprot', models.DO_NOTHING, blank=True, null=True)
    accession = models.CharField(max_length=30, blank=True, null=True)
    sequence = models.CharField(max_length=200, blank=True, null=True)
    uniparc_accession = models.CharField(max_length=30, blank=True, null=True)
    embl_acc = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'isoform'

class MappingHistory(models.Model):
    mapping_history_id = models.BigAutoField(primary_key=True)
    ensembl_species_history_id = models.BigIntegerField(blank=True, null=True)
    time_mapped = models.DateTimeField()
    entries_mapped = models.BigIntegerField(blank=True, null=True)
    entries_unmapped = models.BigIntegerField(blank=True, null=True)
    uniprot_release = models.CharField(max_length=7, blank=True, null=True)
    uniprot_taxid = models.BigIntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mapping_history'

class TaxonomyMapping(models.Model):
    taxonomy_mapping_id = models.BigAutoField(primary_key=True)
    ensembl_tax_id = models.BigIntegerField(blank=True, null=True)
    uniprot_tax_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'taxonomy_mapping'

class UniprotUnmapped(models.Model):
    uniprot_id = models.BigAutoField(primary_key=True)
    uniprot_acc = models.CharField(max_length=30, blank=True, null=True)
    protein_existence_id = models.BigIntegerField(blank=True, null=True)
    species = models.CharField(max_length=30, blank=True, null=True)
    uniprot_tax_id = models.BigIntegerField(blank=True, null=True)
    entry_type = models.CharField(max_length=30, blank=True, null=True)
    release_version = models.CharField(max_length=30, blank=True, null=True)
    userstamp = models.CharField(max_length=30, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    entry_version = models.BigIntegerField(blank=True, null=True)
    mapping_history_id = models.BigIntegerField(blank=True, null=True)
    sequence_version = models.SmallIntegerField(blank=True, null=True)
    upi = models.CharField(max_length=13, blank=True, null=True)
    md5 = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'uniprot_unmapped'
