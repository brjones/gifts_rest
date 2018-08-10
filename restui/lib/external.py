from django.http import Http404
import requests

from gifts_rest.settings.base import TARK_SERVER, ENSEMBL_REST_SERVER

def tark_transcript(enst_id, release):
    url = "{}/api/transcript/?stable_id={}&release_short_name={}&expand=sequence"

    r = requests.get(url.format(TARK_SERVER, enst_id, release))
    if not r.ok:
        raise Http404

    response = r.json()
    if not response:
        raise Exception("Couldn't get a response from TaRK for {}".format(enst_id))
    if response['count'] > 1:
        raise Exception("Couldn't get a/or unique answer from TaRK for {}".format(enst_id))
    if not 'results' in response or not response['results']:
        raise Exception("Empty result set from TaRK for {}".format(enst_id))

    return response['results'][0]

def ensembl_current_release():
    """
    Return current Ensembl release number.
    """
    
    r = requests.get("{}/info/software".format(ENSEMBL_REST_SERVER), headers={ "Content-Type" : "application/json"})
    if not r.ok:
        r.raise_for_status()

    return r.json()['release']

def ensembl_sequence(enst_id, release):
    e_current_release = ensembl_current_release()
    server = ENSEMBL_REST_SERVER if release == e_current_release else "http://e{}.rest.ensembl.org".format(release)

    r = requests.get("{}/sequence/id/{}?content-type=text/plain".format(server, enst_id))
    if not r.ok:
        r.raise_for_status()

    return r.text

def ensembl_protein(enst_id, release):
    e_current_release = ensembl_current_release()
    server = ENSEMBL_REST_SERVER if release == e_current_release else "http://e{}.rest.ensembl.org".format(release)

    r = requests.get("{}/lookup/id/{}?expand=1&content-type=application/json".format(server, enst_id))
    if not r.ok:
        r.raise_for_status()

    ensembl_json = r.json()

    return ensembl_json['Translation']['id']
