from django.db import models

class Alignment(models.Model):
    alignment_id = models.BigAutoField(primary_key=True)
    alignment_run = models.ForeignKey('AlignmentRun', models.DO_NOTHING)
    uniprot_id = models.BigIntegerField(blank=True, null=True)
    transcript = models.ForeignKey('EnsemblTranscript', models.DO_NOTHING, blank=True, null=True)
    mapping = models.ForeignKey('Mapping', models.DO_NOTHING, blank=True, null=True)
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
    release_mapping_history = models.ForeignKey('ReleaseMappingHistory', models.DO_NOTHING)
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

class Mapping(models.Model):
    mapping_id = models.BigAutoField(primary_key=True)
    uniprot = models.ForeignKey('UniprotEntry', models.DO_NOTHING, blank=True, null=True)
    transcript = models.ForeignKey('EnsemblTranscript', models.DO_NOTHING, blank=True, null=True)
    grouping_id = models.BigIntegerField(blank=True, null=True)

    def __str__(self):
        return "{0} - ({1}, {2})".format(self.mapping_id, self.uniprot, self.transcript)

    class Meta:
        managed = False
        db_table = 'mapping'


class MappingHistory(models.Model):
    mapping_history_id = models.BigAutoField(primary_key=True)
    release_mapping_history = models.ForeignKey('ReleaseMappingHistory', models.DO_NOTHING)
    sequence_version = models.SmallIntegerField()
    entry_type = models.SmallIntegerField()
    entry_version = models.IntegerField()
    enst_version = models.SmallIntegerField()
    mapping = models.ForeignKey(Mapping, models.DO_NOTHING)
    sp_ensembl_mapping_type = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mapping_history'

class ReleaseMappingHistory(models.Model):
    release_mapping_history_id = models.BigAutoField(primary_key=True)
    ensembl_species_history = models.ForeignKey('EnsemblSpeciesHistory', models.DO_NOTHING, blank=True, null=True)
    time_mapped = models.DateTimeField()
    entries_mapped = models.BigIntegerField(blank=True, null=True)
    entries_unmapped = models.BigIntegerField(blank=True, null=True)
    uniprot_release = models.CharField(max_length=7, blank=True, null=True)
    uniprot_taxid = models.BigIntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'release_mapping_history'
