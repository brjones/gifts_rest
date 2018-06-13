from restui.models.ensembl import EnsemblGene, EnsemblTranscript, EnsemblSpeciesHistory
from restui.models.mappings import EnsemblUniprot, TaxonomyMapping, MappingHistory
from restui.models.uniprot import UniprotEntry, UniprotEntryType
from restui.models.other import CvEntryType, CvUeStatus, UeMappingStatus, UeMappingComment, UeMappingLabel
from restui.serializers.mappings import MappingSerializer, MappingCommentsSerializer

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

def get_ensembl_uniprot(pk):
    try:
        return EnsemblUniprot.objects.get(pk=pk)
    except EnsemblUniprot.DoesNotExist:
        raise Http404

def get_mapping_history(mapping):
    try:
        return MappingHistory.objects.get(pk=mapping.mapping_history_id)
    except MappingHistory.DoesNotExist:
        raise Http404

class Mapping(APIView):
    """
    Retrieve a single mapping.
    """

    def get_taxonomy(self, mapping_history):
        try:
            ensembl_species_history = EnsemblSpeciesHistory.objects.get(pk=mapping_history.ensembl_species_history_id)
        except EnsemblSpeciesHistory.DoesNotExist:
            raise Http404
        
        return { 'species':ensembl_species_history.species,
                 'ensemblTaxId':ensembl_species_history.ensembl_tax_id,
                 'uniprotTaxId':mapping_history.uniprot_taxid }

    def get_mapping(self, mapping, mapping_history):
        try:
            ensembl_species_history = EnsemblSpeciesHistory.objects.get(pk=mapping_history.ensembl_species_history_id)
        except EnsemblSpeciesHistory.DoesNotExist:
            raise Http404

        ensembl_release, uniprot_release = ensembl_species_history.ensembl_release, mapping_history.uniprot_release

        try:
            ensembl_transcript = EnsemblTranscript.objects.get(ensembluniprot=mapping)
            uniprot_entry_type = UniprotEntryType.objects.get(ensembluniprot=mapping)
            uniprot_entry = UniprotEntry.objects.get(uniprotentrytype=uniprot_entry_type)
        except (EnsemblTranscript.DoesNotExist, UniprotEntryType.DoesNotExist, UniprotEntry.DoesNotExist):
            raise Http404
        except MultipleObjectsReturned:
            raise Exception('Should not be here')

        #
        # fetch status
        #
        # NOTE
        #   There's no way to get to the specific mapping from the upacc/enst pair in UeMappingStatus table.
        #   Mappings sharing the same upacc/enst are technically the same pair, so status for a given mapping
        #   is simply reported as being the most recent status associated to the given pair. Moreover, users
        #   are likely to be not interested to see the status history, i.e. who when changed status.
        #
        try:
            mapping_status = UeMappingStatus.objects.filter(uniprot_acc=uniprot_entry.uniprot_acc, enst_id=ensembl_transcript.enst_id).order_by('-time_stamp')[0]
            status = CvUeStatus.objects.get(pk=mapping_status.status).description
        except (IndexError, CvUeStatus.DoesNotExist):
            # TODO: should log this anomaly or do something else
            status = None

        #
        # fetch entry_type
        #
        # NOTE
        #  Specs at https://github.com/ebi-uniprot/gifts-mock/blob/master/data/mapping.json
        #  prescribe to report isoform as boolean flag separate from entry_type.
        #  Here we don't do that, as isoform is an entry type, e.g. Swiss-Prot isoform, so isoform
        #  status is implicitly reported by entryType.
        #
        #
        try:
            entry_type = CvEntryType.objects.get(pk=uniprot_entry_type.entry_type).description
        except CvEntryType.DoesNotExist:
            raise Http404
        
        return { 'mappingId':mapping.mapping_id,
                 'timeMapped':mapping.timestamp,
                 'ensemblRelease':ensembl_release,
                 'uniprotRelease':uniprot_release,
                 'uniprotEntry': {
                     'uniprotAccession':uniprot_entry.uniprot_acc,
                     'entryType':entry_type, 
                     'sequenceVersion':uniprot_entry.sequence_version,
                     'upi':uniprot_entry.upi,
                     'md5':uniprot_entry.md5,
                     'ensemblDerived':uniprot_entry.ensembl_derived,
                 },
                 'ensemblTranscript': {
                     'enstId':ensembl_transcript.enst_id,
                     'enstVersion':ensembl_transcript.enst_version,
                     'upi':ensembl_transcript.uniparc_accession,
                     'biotype':ensembl_transcript.biotype,
                     'deleted':ensembl_transcript.deleted,
                     'seqRegionStart':ensembl_transcript.seq_region_start,
                     'seqRegionEnd':ensembl_transcript.seq_region_end,
                     'ensgId':EnsemblGene.objects.get(ensembltranscript=ensembl_transcript).ensg_id,
                     'sequence':None # TODO
                 },
                 'status':status
        }

    def get_related_mappings(self, mapping):
        """
        Return the list of mappings sharing the same ENST or Uniprot accession of the given mapping.
        """
        
        mappings = EnsemblUniprot.objects.filter(transcript=mapping.transcript).filter(uniprot_entry_type=mapping.uniprot_entry_type).exclude(pk=mapping.mapping_id)

        return list(map(lambda m: self.get_mapping(m, get_mapping_history(m)), mappings))
                                    
    def get(self, request, pk):
        ensembl_uniprot = get_ensembl_uniprot(pk)
        mapping_history = get_mapping_history(ensembl_uniprot)

        data = { 'taxonomy':self.get_taxonomy(mapping_history),
                 'mapping':self.get_mapping(ensembl_uniprot, mapping_history),
                 'relatedMappings':self.get_related_mappings(ensembl_uniprot) }
        
        serializer = MappingSerializer(data)

        return Response(serializer.data)


class MappingComments(APIView):
    """
    Retrieve all comments relative to a given mapping.
    """

    def get(self, request, pk):
        mapping = get_ensembl_uniprot(pk)

        try:
            ensembl_transcript = EnsemblTranscript.objects.get(ensembluniprot=mapping)
            uniprot_entry_type = UniprotEntryType.objects.get(ensembluniprot=mapping)
            uniprot_entry = UniprotEntry.objects.get(uniprotentrytype=uniprot_entry_type)
        except (EnsemblTranscript.DoesNotExist, UniprotEntryType.DoesNotExist, UniprotEntry.DoesNotExist):
            raise Http404
        except MultipleObjectsReturned:
            raise Exception('Should not be here')

        # fetch latest mapping status (see comments in class Mapping)
        try:
            mapping_status = UeMappingStatus.objects.filter(uniprot_acc=uniprot_entry.uniprot_acc, enst_id=ensembl_transcript.enst_id).order_by('-time_stamp')[0]
            status = CvUeStatus.objects.get(pk=mapping_status.status).description
        except (IndexError, CvUeStatus.DoesNotExist):
            status = None

        # fetch mapping comment history
        mapping_comments = UeMappingComment.objects.filter(uniprot_acc=uniprot_entry.uniprot_acc, enst_id=ensembl_transcript.enst_id).order_by('-time_stamp')
        comments = map(lambda c: { 'text':c.comment, 'timeAdded':c.time_stamp, 'user':c.user_stamp }, mapping_comments)

        # fetch mapping label history
        mapping_labels = UeMappingLabel.objects.filter(uniprot_acc=uniprot_entry.uniprot_acc, enst_id=ensembl_transcript.enst_id).order_by('time_stamp')
        try:
            labels = map(lambda l: { 'text':CvUeLabel.objects.get(pk=l.label).description, 'timeAdded':l.time_stamp, 'user':l.user_stamp }, mapping_labels)
        except CvUeLabel.DoesNotExist:
            raise Http404

        data = { 'mappingId':mapping.mapping_id,
                 'status':status,
                 'user':mapping.userstamp,
                 'comments':list(comments),
                 'labels':list(labels)
        }

        serializer = MappingCommentsSerializer(data)
        return Response(serializer.data)
