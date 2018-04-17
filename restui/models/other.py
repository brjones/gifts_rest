from django.db import models

class CvEntryType(models.Model):
    id = models.BigIntegerField(primary_key=True)
    description = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cv_entry_type'


class CvUeLabel(models.Model):
    id = models.BigIntegerField(primary_key=True)
    description = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'cv_ue_label'


class CvUeStatus(models.Model):
    id = models.BigIntegerField(primary_key=True)
    description = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'cv_ue_status'

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

class UeMappingComment(models.Model):
    id = models.BigAutoField(primary_key=True)
    uniprot_acc = models.CharField(max_length=30)
    enst_id = models.CharField(max_length=30)
    time_stamp = models.DateTimeField()
    user_stamp = models.CharField(max_length=20)
    comment = models.TextField()

    class Meta:
        managed = False
        db_table = 'ue_mapping_comment'


class UeMappingLabel(models.Model):
    id = models.BigAutoField(primary_key=True)
    uniprot_acc = models.CharField(max_length=30)
    enst_id = models.CharField(max_length=30)
    time_stamp = models.DateTimeField()
    user_stamp = models.CharField(max_length=20)
    label = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'ue_mapping_label'


class UeMappingStatus(models.Model):
    id = models.BigAutoField(primary_key=True)
    uniprot_acc = models.CharField(max_length=30)
    enst_id = models.CharField(max_length=30)
    time_stamp = models.DateTimeField()
    user_stamp = models.CharField(max_length=20)
    status = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'ue_mapping_status'
