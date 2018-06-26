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

class UeMappingComment(models.Model):
    id = models.BigAutoField(primary_key=True)
    time_stamp = models.DateTimeField()
    user_stamp = models.CharField(max_length=20)
    comment = models.TextField()
    mapping = models.ForeignKey('Mapping', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ue_mapping_comment'


class UeMappingLabel(models.Model):
    id = models.BigAutoField(primary_key=True)
    time_stamp = models.DateTimeField()
    user_stamp = models.CharField(max_length=20)
    label = models.BigIntegerField()
    mapping = models.ForeignKey('Mapping', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'ue_mapping_label'


class UeMappingStatus(models.Model):
    id = models.BigAutoField(primary_key=True)
    time_stamp = models.DateTimeField()
    user_stamp = models.CharField(max_length=20)
    status = models.BigIntegerField()
    mapping = models.ForeignKey('Mapping', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'ue_mapping_status'
