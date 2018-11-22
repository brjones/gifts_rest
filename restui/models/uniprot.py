from django.db import models
from restui.models.annotations import CvEntryType

class Isoform(models.Model):
    isoform_id = models.BigAutoField(primary_key=True)
    uniprot_id = models.BigIntegerField(blank=True, null=True)
    accession = models.CharField(max_length=30, blank=True, null=True)
    sequence = models.CharField(max_length=200, blank=True, null=True)
    uniparc_accession = models.CharField(max_length=30, blank=True, null=True)
    embl_acc = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'isoform'

class Domain(models.Model):
    domain_id = models.BigAutoField(primary_key=True)
    isoform = models.ForeignKey('Isoform', models.DO_NOTHING, blank=True, null=True)
    start = models.BigIntegerField(blank=True, null=True)
    end = models.BigIntegerField(blank=True, null=True)
    description = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'domain'

class Ptm(models.Model):
    ptm_id = models.BigAutoField(primary_key=True)
    domain = models.ForeignKey(Domain, models.DO_NOTHING, blank=True, null=True)
    description = models.CharField(max_length=45, blank=True, null=True)
    start = models.BigIntegerField(blank=True, null=True)
    end = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ptm'

class UniprotEntry(models.Model):
    uniprot_id = models.BigAutoField(primary_key=True)
    uniprot_acc = models.CharField(max_length=30, blank=True, null=True)
    uniprot_tax_id = models.BigIntegerField(blank=True, null=True)
    userstamp = models.CharField(max_length=30, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    sequence_version = models.SmallIntegerField(blank=True, null=True)
    upi = models.CharField(max_length=13, blank=True, null=True)
    md5 = models.CharField(max_length=32, blank=True, null=True)
    canonical_uniprot_id = models.IntegerField(blank=True, null=True)
    ensembl_derived = models.NullBooleanField()
    alias = models.CharField(max_length=30, blank=True, null=True)
    gene_symbol = models.CharField(max_length=30, blank=True, null=True)
    chromosome_line = models.CharField(max_length=30, blank=True, null=True)
    entry_type = models.ForeignKey('CvEntryType', models.DO_NOTHING, blank=True, null=True, db_column="entry_type")
    length = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "{0} - {1}".format(self.uniprot_id, self.uniprot_acc)

    class Meta:
        managed = False
        db_table = 'uniprot_entry'
        unique_together = (('uniprot_acc', 'sequence_version'),)

class UniprotEntryHistory(models.Model):
    release_version = models.CharField(max_length=30)
    uniprot = models.ForeignKey(UniprotEntry, models.DO_NOTHING, primary_key=True)
    grouping_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'uniprot_entry_history'
        unique_together = (('uniprot', 'release_version'),)
