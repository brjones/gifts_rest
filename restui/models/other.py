from django.db import models

class PdbEns(models.Model):
    pdb_ens_id = models.BigAutoField(primary_key=True)
    pdb_acc = models.CharField(max_length=45)
    pdb_release = models.CharField(max_length=11)
    uniprot_acc = models.CharField(max_length=30)
    enst_id = models.CharField(max_length=30)
    enst_version = models.BigIntegerField(blank=True, null=True)
    ensp_id = models.CharField(max_length=30)
    ensp_start = models.BigIntegerField(blank=True, null=True)
    ensp_end = models.BigIntegerField(blank=True, null=True)
    pdb_start = models.BigIntegerField(blank=True, null=True)
    pdb_end = models.BigIntegerField(blank=True, null=True)
    pdb_chain = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'pdb_ens'

class TaxonomyMapping(models.Model):
    taxonomy_mapping_id = models.BigAutoField(primary_key=True)
    ensembl_tax_id = models.BigIntegerField(blank=True, null=True)
    uniprot_tax_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'taxonomy_mapping'

class TempMap(models.Model):
    uniprot_id = models.BigIntegerField()
    uniprot_entry_version_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'temp_map'

class Users(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    elixir_id = models.CharField(max_length=50, blank=True, null=True)
    is_admin = models.NullBooleanField()
    validated = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'users'
