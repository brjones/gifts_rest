from restui.models.ensembl import EnsemblGene, EnsemblTranscript, EnsemblSpeciesHistory
from restui.models.mappings import EnsemblUniprot, TaxonomyMapping, MappingHistory
from restui.models.uniprot import UniprotEntry, UniprotEntryType
from restui.models.other import CvEntryType, CvUeStatus, UeMappingStatus
from restui.serializers.mappings import MappingSerializer

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
        # TODO
        #
        # Not sure I'm doing the correct thing. A mapping shouldn't be uniquely identified by the transcript_id/uniprot_acc pair,
        # as there could be several mappings associated to the given pair.
        # 
        #
        try:
            mapping_status = UeMappingStatus.objects.get(uniprot_acc=uniprot_entry.uniprot_acc, enst_id=ensembl_transcript.enst_id)
            status = CvUeStatus.objects.get(pk=mapping_status.id).description
        except (UeMappingStatus.DoesNotExist, CvUeStatus.DoesNotExist):
            # TODO: should log this anomaly or do something else
            status = None

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
                     'entryVersion':None, # TODO: there's no uniprot_entry_type.entry_version any more?!
                     'sequenceVersion':uniprot_entry.sequence_version,
                     'upi':uniprot_entry.upi,
                     'md5':uniprot_entry.md5,
                     'ensemblDerived':uniprot_entry.ensembl_derived,
                     'isoform':None # TODO
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
        Return the list of mappings sharing the same ENST or Uniprot accession.
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


