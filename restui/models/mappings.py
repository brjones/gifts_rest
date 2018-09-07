from django.db import models
from django.db.models import Count

from restui.lib.alignments import calculate_difference

class Alignment(models.Model):
    alignment_id = models.BigAutoField(primary_key=True)
    alignment_run = models.ForeignKey('AlignmentRun', models.DO_NOTHING)
    uniprot_id = models.BigIntegerField(blank=True, null=True)
    transcript = models.ForeignKey('EnsemblTranscript', models.DO_NOTHING, blank=True, null=True)
    mapping = models.ForeignKey('Mapping', models.DO_NOTHING, blank=True, null=True, related_name='alignments')
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

class MappingQuerySet(models.query.QuerySet):
    _counts = None

    def grouped_counts(self):
        """
        Retrieve a list of unique_grouping_id counts from a queryset.
        eg
        [{'unique_grouping_id': 1, 'total': 19}, {'unique_grouping_id': 2, 'total': 6}, {'unique_grouping_id': 3, 'total': 4},...]
        """
        if self._counts is None:
            self._counts = self.values('unique_grouping_id').annotate(total=Count('unique_grouping_id')).order_by('unique_grouping_id')

        return self._counts

    @property
    def grouped_count(self):
        """
        Retrieve the total number of groups based on unique_grouping_id from a queryset
        """
        counts = self.grouped_counts()
        
        return len(counts)

    def grouped_slice(self, offset, limit):
        """
        Fetch a subset of Mapping records grouped by unique_grouping_id.
        We first find how many records in to the queryset, counting by
        unique_grouping_id intervals. Then find the number of records to extract
        to scoop up limit number of groups.
        
        Finally return the groups all nicely packaged up in a dict of lists,
        where the dict key is the unique_grouping_id and the value is a list of
        Mapping objects associated with that unique_grouping_id
        """
        counts = self.grouped_counts()
        
        if offset == 0:
            qs_offset = 0
        else:
            qs_offset = sum(int(row['total']) for row in counts[:offset])
            
        qs_limit = sum(int(row['total']) for row in counts[offset:offset+limit])

        print(qs_offset)
        print(qs_limit)

        sub_qs = self.select_related('uniprot').select_related('transcript').select_related('transcript__gene').order_by('unique_grouping_id')[qs_offset:qs_offset+qs_limit]
        
        grouped_results = {}
        for result in sub_qs:
            try:
                grouped_results[result.unique_grouping_id].append(result)
            except (KeyError, AttributeError):
                grouped_results[result.unique_grouping_id] = [ result ]

        return grouped_results

    def statuses(self):
        """
        Return a list of all the statuses represented in this queryset
        """
        status_set = self.values('status__status_id').distinct()
        
        status_list = []
        for status in status_set:
            status_list.append(status['status__status_id'])
            
        return status_list

    def species(self):
        """
        Return a list of tuples, of all the tax_id and species in this queryset
        """
#        species_set = self.values('transcript__history__ensembl_species_history__ensembl_tax_id', 'transcript__transcripthistory__ensembl_species_history__species').distinct()
        species_set = self.values('transcript__transcripthistory__ensembl_species_history__ensembl_tax_id', 'transcript__transcripthistory__ensembl_species_history__species').distinct()

        species_list = []
        for species in species_set:
            species_list.append((species['transcript__transcripthistory__ensembl_species_history__ensembl_tax_id'],
                                 species['transcript__transcripthistory__ensembl_species_history__species']))

        return species_list

    def divergences(self):
        """
        Return a list of all the alignment differences levels represented in the queryset 
        """
        identical = self.filter(alignment_difference=0).count()
        small = self.filter(alignment_difference__gt=0, alignment_difference__lte=5).count()
        large = self.filter(alignment_difference__gt=5).count()
        
        return [identical, small, large]

class MappingManager(models.Manager):
    def get_queryset(self):
        return MappingQuerySet(self.model, using=self._db)

class Mapping(models.Model):
    objects = MappingManager()

    mapping_id = models.BigAutoField(primary_key=True)
    uniprot = models.ForeignKey('UniprotEntry', models.DO_NOTHING, blank=True, null=True)
    transcript = models.ForeignKey('EnsemblTranscript', models.DO_NOTHING, blank=True, null=True)
    grouping_id = models.BigIntegerField(blank=True, null=True)
    unique_grouping_id = models.BigIntegerField(blank=True, null=True)
    alignment_difference = models.IntegerField(blank=True, null=True)

    @property
    def difference(self):
        diff_count = None
        
        for alignment in self.alignments.all():
            if alignment.alignment_run.score1_type == 'perfect_match' and alignment.score1 == 1:
                return 0;
            
            elif alignment.alignment_run.score1_type == 'identity':
                diff_count = calculate_difference(alignment.pairwise.cigarplus)
                
        if diff_count:
            return diff_count
        
        return None

    def __str__(self):
        return "{0} - ({1}, {2})".format(self.mapping_id, self.uniprot, self.transcript)

    class Meta:
        managed = False
        db_table = 'mapping'


class MappingHistory(models.Model):
    mapping_history_id = models.BigAutoField(primary_key=True)
    release_mapping_history = models.ForeignKey('ReleaseMappingHistory', models.DO_NOTHING, related_name='mapping_history')
    sequence_version = models.SmallIntegerField()
    entry_type = models.ForeignKey('CvEntryType', models.DO_NOTHING, blank=True, null=True, db_column="entry_type")
    entry_version = models.IntegerField()
    enst_version = models.SmallIntegerField()
    mapping = models.ForeignKey(Mapping, models.DO_NOTHING, related_name='mapping_history')
    sp_ensembl_mapping_type = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mapping_history'

class ReleaseMappingHistory(models.Model):
    release_mapping_history_id = models.BigAutoField(primary_key=True)
    ensembl_species_history = models.ForeignKey('EnsemblSpeciesHistory', models.DO_NOTHING, related_name='release_mapping_history', blank=True, null=True)
    time_mapped = models.DateTimeField()
    entries_mapped = models.BigIntegerField(blank=True, null=True)
    entries_unmapped = models.BigIntegerField(blank=True, null=True)
    uniprot_release = models.CharField(max_length=7, blank=True, null=True)
    uniprot_taxid = models.BigIntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'release_mapping_history'
