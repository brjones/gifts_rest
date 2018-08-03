from django.db import models
from django.conf import settings

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
    user_stamp = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='user_stamp')
    comment = models.TextField()
    mapping = models.ForeignKey('Mapping', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ue_mapping_comment'


class UeMappingLabel(models.Model):
    id = models.BigAutoField(primary_key=True)
    time_stamp = models.DateTimeField()
    user_stamp = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='user_stamp')
    label = models.BigIntegerField()
    mapping = models.ForeignKey('Mapping', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'ue_mapping_label'


class UeMappingStatus(models.Model):
    id = models.BigAutoField(primary_key=True)
    time_stamp = models.DateTimeField()
    user_stamp = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, db_column='user_stamp')
    status = models.ForeignKey('CvUeStatus', db_column='status', to_field='id', on_delete=models.CASCADE)
    mapping = models.ForeignKey('Mapping', related_name='status', on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'ue_mapping_status'
