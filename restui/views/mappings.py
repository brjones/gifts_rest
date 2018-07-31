import pprint
import re
import requests

from restui.models.ensembl import EnsemblGene, EnsemblTranscript, EnsemblSpeciesHistory
from restui.models.mappings import Mapping, MappingHistory, ReleaseMappingHistory
from restui.models.uniprot import UniprotEntry
from restui.models.annotations import CvEntryType, CvUeStatus, CvUeLabel, UeMappingStatus, UeMappingComment, UeMappingLabel
from restui.serializers.mappings import MappingSerializer, MappingCommentsSerializer, MappingsSerializer
from restui.serializers.annotations import StatusSerializer, CommentSerializer, LabelSerializer
from restui.pagination import FacetPagination
from restui.lib.external import ensembl_sequence

from django.http import Http404
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Max, F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from rest_framework.permissions import IsAuthenticated


def get_mapping(pk):
    try:
        return Mapping.objects.get(pk=pk)
    except Mapping.DoesNotExist:
        raise Http404

def get_mapping_history(mapping):
    # A mapping can have multiple entries in mapping history and it is not clear which one to go for.
    # The assumption would be that when mapping is curated it is always related to latest status
    #
    # just pick latest mapping_history entry (the one with the highest id)
    #
    try:
        return MappingHistory.objects.filter(mapping=mapping).order_by('-mapping_history_id')[0]
    except MappingHistory.DoesNotExist:
        raise Http404

def get_status(mapping):
    try:
        # status is assumed to be the latest associated to the given mapping
        mapping_status = UeMappingStatus.objects.filter(mapping=mapping).order_by('-time_stamp')[0]
        status = CvUeStatus.objects.get(pk=mapping_status.status).description
    except (IndexError, CvUeStatus.DoesNotExist):
        # TODO: should log this anomaly or do something else
        status = None

    return status

def get_label(label):
    """
    Retrieve the label object associated to the given description
    """

    try:
        return CvUeLabel.objects.get(description=label)
    except CvUeLabel.DoesNotExist:
        raise Http404("Couldn't get label object for {}".format(label))
    except MultipleObjectsReturned:
        raise Http404("Couldn't get unique label object for {}".format(label))
    
def build_taxonomy_data(mapping):
    # Find the ensembl tax id via one ensembl species history associated to transcript
    # associated to the given mapping.
    # Relationship between transcript and history is many to many but we just fetch one history
    # as the tax id remains the same across all of them
    try:
        ensembl_species_history = EnsemblSpeciesHistory.objects.get(transcripthistory__transcript=mapping.transcript)
    except EnsemblSpeciesHistory.DoesNotExist:
        raise Http404("Couldn't find an ensembl species history associated to mapping {}".format(mapping.mapping_id))
    
    try:
        return { 'species':ensembl_species_history.species,
                 'ensemblTaxId':ensembl_species_history.ensembl_tax_id,
                 'uniprotTaxId':mapping.uniprot.uniprot_tax_id }
    except:
        raise Http404("Couldn't find uniprot tax id as I couldn't find a uniprot entry associated to the mapping")

def build_mapping_data(mapping, mapping_history, fetch_sequence=True):
    #
    # get ensembl/uniprot release
    #
    # to get ensembl release, we need the ensembl species history associated to the mapping_history
    #
    try:
        ensembl_species_history = EnsemblSpeciesHistory.objects.get(releasemappinghistory__mappinghistory=mapping_history)
    except EnsemblSpeciesHistory.DoesNotExist:
        raise Http404("Could't fetch ensembl species history from mapping history {}".format(mapping_history.mapping_history_id))
    except MultipleObjectsReturned:
        raise Http404("Shouldn't be here")

    # uniprot release is an attribute of the associated release mapping history
    try:
        release_mapping_history = ReleaseMappingHistory.objects.get(mappinghistory=mapping_history)
    except ReleaseMappingHistory.DoesNotExist:
        raise Http404("Couldn't fetch ReleaseMappingHistory from mapping history {}".format(mapping_history.mapping_history_id))
    
    ensembl_release, uniprot_release = ensembl_species_history.ensembl_release, release_mapping_history.uniprot_release

    try:
        ensembl_transcript = mapping.transcript
        uniprot_entry = mapping.uniprot
    except ObjectDoesNotExist:
        raise Http404("Couldn't find either transcript or uniprot entry")

    # fetch status
    status = get_status(mapping)

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
        entry_type = CvEntryType.objects.get(pk=mapping_history.entry_type).description
    except CvEntryType.DoesNotExist:
        raise Http404

    #
    # fetch transcript sequence from TaRK
    #
    sequence = None
    if fetch_sequence:
        try:
            sequence = ensembl_sequence(ensembl_transcript.enst_id, ensembl_release)
        except Exception as e:
            print(e) # TODO: log
            sequence = None

    return { 'mappingId':mapping.mapping_id,
             'timeMapped':release_mapping_history.time_mapped,
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
                 'sequence':sequence
             },
             'status':status
    }

def build_related_mappings_data(mapping):
    """
    Return the list of mappings sharing the same ENST or Uniprot accession of the given mapping.
    """

    # related mapping share the same group_id and tax id
    mappings = Mapping.objects.filter(grouping_id=mapping.grouping_id,
                                      uniprot__uniprot_tax_id=mapping.uniprot.uniprot_tax_id).exclude(pk=mapping.mapping_id)

    return list(map(lambda m: build_mapping_data(m, get_mapping_history(m), fetch_sequence=False), mappings))


##########################
#                        #
# The front-end read API #
#                        #
##########################

class MappingView(APIView):
    """
    Retrieve a single mapping, includes related mappings and taxonomy information.
    """


    def get(self, request, pk):
        mapping = get_mapping(pk)
        mapping_history = get_mapping_history(mapping)

        data = { 'taxonomy':build_taxonomy_data(mapping),
                 'mapping':build_mapping_data(mapping, mapping_history),
                 'relatedMappings':build_related_mappings_data(mapping) }
        
        serializer = MappingSerializer(data)

        return Response(serializer.data)

class MappingCommentsView(APIView):
    """
    Retrieve all comments relative to a given mapping, includes mapping labels.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        mapping = get_mapping(pk)

        try:
            ensembl_transcript = mapping.transcript
        except ObjectDoesNotExist:
            raise Http404("Couldn't find transcript entry associated to mapping {}".format(mapping.mapping_id))

        # fetch latest mapping status
        status = get_status(mapping)

        # fetch mapping comment history
        mapping_comments = UeMappingComment.objects.filter(mapping=mapping).order_by('-time_stamp')
        comments = map(lambda c: { 'text':c.comment, 'timeAdded':c.time_stamp, 'user':c.user_stamp }, mapping_comments)

        # fetch mapping label history
        mapping_labels = UeMappingLabel.objects.filter(mapping=mapping).order_by('-time_stamp')
        try:
            labels = map(lambda l: { 'text':CvUeLabel.objects.get(pk=l.label).description, 'timeAdded':l.time_stamp, 'user':l.user_stamp }, mapping_labels)
        except CvUeLabel.DoesNotExist:
            raise Http404("Couldn't fetch label")

        data = { 'mappingId':mapping.mapping_id,
                 'status':status,
                 'comments':list(comments),
                 'labels':list(labels)
        }

        serializer = MappingCommentsSerializer(data)
        return Response(serializer.data)


#
# TODO
#
# - Filter based on other facets, besides organism/status
#
# - Group mappings if they share ENST or UniProt accessions,
#   see https://github.com/ebi-uniprot/gifts-mock/blob/master/data/mappings.json
#
# - What does it mean to search with a given mapping ID, return just that mapping
#   or all 'related' mappings?
#   We're returning only that mapping at the moment, to discuss with Uniprot
#
# - facet filtering based on mapping status: consider query potential values and DB values might be different
#   |
#   --> Action: agree with Uniprot on a common vocabulary
#
class MappingsView(generics.ListAPIView):
    """
    Search/retrieve all mappings. Mappings are grouped if they share ENST or UniProt accessions.
    'Facets' are used for filtering and returned by the service based on the result set.
    """

    serializer_class = MappingsSerializer
    pagination_class = FacetPagination
    
    def get_queryset(self):
        # the ENSG, ENST, UniProt accession or mapping id. If none are provided all mappings are returned
        search_term = self.request.query_params.get('searchTerm', None)
        
        # filters for the given query, taking the form facets=organism:9606,status:unreviewed
        facets_params = self.request.query_params.get('facets', None)

        # search the mappings according to the search term 'type'
        queryset = None
        if search_term:
            if search_term.isdigit(): # this is a mapping ID
                # TODO
                #  what does it mean to search with a given mapping ID, return just that mapping
                #  or all 'related' mappings? We're returning only that mapping at the moment
                queryset = [ get_mapping(search_term) ]
            else: # this is either an ENSG/ENST or UniProt accession
                if re.compile(r"^ENS[A-Z]*?G[0-9]+?$").match(search_term):
                    queryset = Mapping.objects.filter(transcript__gene__ensg_id=search_term)
                elif re.compile(r"^ENS[A-Z]*?T[0-9]+?$").match(search_term):
                    queryset = Mapping.objects.filter(transcript__enst_id=search_term)
                else:
                    queryset = Mapping.objects.filter(uniprot__uniprot_acc=search_term)
        else:
            # no search term: return all mappings
            #
            # WARNING!! This is massively hitting the database
            #
            # See Matt's June 19 Matt's comments on slack for a possible direction
            # e.g. https://github.com/encode/django-rest-framework/issues/1721
            #
            # Can return an iterator, but this is not compatible with pagination, see comments below
            # queryset = Mapping.objects.all().iterator()
            queryset = Mapping.objects.all()

        #
        # Apply filters based on facets parameters
        #
        # TODO: consider other filters besides organism/status
        #
        if facets_params:
            queryset = queryset.all()
            # create facets dict from e.g. 'organism:9606,status:unreviewed'
            facets = dict( tuple(param.split(':')) for param in facets_params.split(',') )

            # follow the relationships up to ensembl_species_history to filter based on taxid
            if 'organism' in facets:
                queryset = queryset.filter(transcript__transcripthistory__ensembl_species_history__ensembl_tax_id=facets['organism'])

            # filter queryset based on status
            # NOTE: cannot directly filter by following relationships,
            #       have to fetch latest status associated to each mapping
            if 'status' in facets:
                # create closure to be used in filter function to filter queryset based on status
                # binds to given status so filter can pass each mapping which is compared against binding param
                try:
                    status_id = CvUeStatus.objects.get(description=facets['status'].upper()).id
                except:
                    raise Http404("Invalid status type")
                    # TODO Should be a 400, how do we make this work with pagination?
                    #return Response(status=status.HTTP_400_BAD_REQUEST)

                # Left join on the status table, find the 'newest' status only and filter out all other joined rows
                queryset = queryset.annotate(latest_status=Max('status__time_stamp')).filter(status__time_stamp=F('latest_status')).filter(status__status=status_id)

        #
        # Take the first xxx results in case of no search term, as discussed with UniProt
        # It's done here as Django doesn't allow to filter (based on facets above ) a query once a slice has been taken.
        #
        if not search_term:
            queryset_truncated = []
            count = 0
            for result in queryset:
                queryset_truncated.append(result)
                count += 1
                if count >= 100:
                    break
            queryset = queryset_truncated

        # group the result set
        # results in each group share the same ENST or UniProt accession, i.e. the same grouping_id
        queryset_groups = {}
        for result in queryset:
            try:
                queryset_groups[result.grouping_id].append(result)
            except (KeyError, AttributeError):
                queryset_groups[result.grouping_id] = [ result ]


        #
        # Return the result set according to the (latest) specification, i.e.
        # https://github.com/ebi-uniprot/gifts-mock/blob/master/data/db.json#L159
        #
        # NOTES (Important)
        #
        # Unfortunately, we have to 'evaluate' the queryset since we need assemble and serialise
        # objects which do not come straight from the DB. This is a problem when there's no search
        # term specified, as we're forced to iterate over gazillions of rows.
        #
        # I've tried making the queryset an iterator and returning a generator expression,
        # but pagination in these cases won't work as it expects itself to be able to
        # compute the length of the given data.
        #
        # return ( {'taxonomy':get_taxonomy(mapping),
        #           'mapping':get_mapping(result, get_mapping_history(mapping)) } for mapping in queryset )
        results = []
        for grouping_id in queryset_groups:
            mapping_group = queryset_groups[grouping_id]
            results.append({ 'taxonomy':build_taxonomy_data(mapping_group[0]), # taxonomy is supposed to be same for all mappings in the group
                              'entryMappings':list(map(lambda m: build_mapping_data(m, get_mapping_history(m), fetch_sequence=False), mapping_group))
            })

        return results

###########################
#                         #
# The front-end write API #
#                         #
###########################

#
# TODO
#
# - handle transactions when writing/updating content, see
#   https://docs.djangoproject.com/en/2.0/topics/db/transactions/
#

class MappingStatusView(APIView):
    """
    Change the status of a mapping
    """

    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        mapping = get_mapping(pk)

        # retrieve the status object associated to the given description
        try:
            s = CvUeStatus.objects.get(description=request.data['status'])
        except KeyError:
            raise Http404("Payload should have 'status'")
        except CvUeStatus.DoesNotExist:
            raise Http404("Couldn't get status object for {}".format(request.data['status']))
        except MultipleObjectsReturned:
            raise Http404("Couldn't get unique status for {}".format(request.data['status']))

        # If the mapping has already been assigned that status, update the timestamp,
        # otherwise create one from scratch
        try:
            mapping_status = UeMappingStatus.objects.get(mapping=mapping, status=s.id)
        except UeMappingStatus.DoesNotExist:
            # create new mapping status
            serializer = StatusSerializer(data={ 'time_stamp':timezone.now(),
                                                 'user_stamp':request.user,
                                                 'status':s.id,
                                                 'mapping':mapping.mapping_id })

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except MultipleObjectsReturned:
            raise Http404("Couldn't get unique status for mapping {}".format(mapping.mapping_id))
        else:
            # mapping status already exist, update timestamp
            serializer = StatusSerializer(mapping_status, data={ 'time_stamp':timezone.now(),
                                                                 'user_stamp':request.user,
                                                                 'status':s.id,
                                                                 'mapping':mapping.mapping_id })
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MappingCommentView(APIView):
    """
    Add a comment to a mapping
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        mapping = get_mapping(pk)

        try:
            serializer = CommentSerializer(data={ 'time_stamp':timezone.now(),
                                                  'user_stamp':request.user,
                                                  'comment':request.data['text'],
                                                  'mapping':mapping.mapping_id })
        except KeyError:
            raise Http404("Must provide comment")

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateMappingLabelView(APIView):
    """
    Add a label associated to a mapping
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        mapping = get_mapping(pk)

        try:
            label = get_label(request.data['label'])
        except KeyError:
            raise Http404("Should provide 'label' in payload")

        # If the mapping has already assigned that label, update the timestamp,
        # otherwise create one from scratch
        try:
            mapping_label = UeMappingLabel.objects.get(mapping=mapping, label=label.id) # user_stamp=request.user,
        except UeMappingLabel.DoesNotExist:
            # create new label associated to the mapping
            serializer = LabelSerializer(data={ 'time_stamp':timezone.now(),
                                                'user_stamp':request.user,
                                                'label':label.id,
                                                'mapping':mapping.mapping_id })
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status.HTTP_201_CREATED)

        else:
            # mapping label already exists, update timestamp
            # NOTE: have to provide all fields anyway othewise serializer complains
            serializer = LabelSerializer(mapping_label, data={ 'time_stamp':timezone.now(),
                                                               'user_stamp':request.user,
                                                               'label':label.id,
                                                               'mapping':mapping.mapping_id })

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#
# TODO: should remove only the label attached to the mapping by the given user
#
class DeleteMappingLabelView(APIView):
    """
    Delete label a associated to the given mapping
    """

    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk, label):
        mapping = get_mapping(pk)

        # delete all labels with the given description attached to the mapping
        # TODO: only those associated to the given user
        mapping_labels = UeMappingLabel.objects.filter(mapping=mapping,label=get_label(label).id)
        if mapping_labels:
            mapping_labels.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        raise Http404
