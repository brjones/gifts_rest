"""
.. See the NOTICE file distributed with this work for additional information
   regarding copyright ownership.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import requests
from django.http import Http404
from gifts_rest.settings.base import TARK_SERVER
from gifts_rest.settings.base import ENSEMBL_REST_SERVER


def tark_transcript(enst_id, release):
    """
    Retrieve the TARK entry for a given ensembl id and release number

    Parameters
    ----------
    enst_id : str
        This needs to be the e! stable ID (eg ENST...)
    release : int

    Returns
    -------
    dict
    """
    url = "{}/api/transcript/?stable_id={}&release_short_name={}&expand=sequence"

    result = requests.get(url.format(TARK_SERVER, enst_id, release))
    if not result.ok:
        raise Http404

    response = result.json()
    if not response:
        raise Exception(
            "Couldn't get a response from TaRK for {}".format(enst_id)
        )

    if response['count'] > 1:
        raise Exception(
            "Couldn't get a/or unique answer from TaRK for {}".format(enst_id)
        )

    if 'results' not in response or not response['results']:
        raise Exception(
            "Empty result set from TaRK for {}".format(enst_id)
        )

    return response['results'][0]


def ensembl_current_release():
    """
    Get the current Ensembl release number.

    Returns
    -------
    release : int
    """

    result = requests.get(
        "{}/info/software".format(ENSEMBL_REST_SERVER),
        headers={
            "Content-Type": "application/json"
        }
    )
    if not result.ok:
        result.raise_for_status()

    return result.json()['release']


def ensembl_sequence(enst_id, release):
    """
    Get the sequence for an ensembl ID in a given release

    Parameters
    ----------
    enst_id : str
        This needs to be the e! stable ID (eg ENST...)
    release : int

    Returns
    -------
    sequence : str
    """

    e_current_release = ensembl_current_release()

    server = "http://e{}.rest.ensembl.org".format(release)
    if release == e_current_release:
        server = ENSEMBL_REST_SERVER

    result = requests.get(
        "{}/sequence/id/{}?content-type=text/plain".format(server, enst_id)
    )
    if not result.ok:
        result.raise_for_status()

    return result.text


def ensembl_protein(enst_id, release):
    """
    Get the protein ensembl ID in a given transcript id and release number

    Parameters
    ----------
    enst_id : str
        This needs to be the e! stable ID (eg ENST...)
    release : int

    Returns
    -------
    protein_id : str
    """

    e_current_release = ensembl_current_release()

    server = "http://e{}.rest.ensembl.org".format(release)
    if release == e_current_release:
        server = ENSEMBL_REST_SERVER

    result = requests.get(
        "{}/lookup/id/{}?expand=1&content-type=application/json".format(server, enst_id)
    )

    if not result.ok:
        result.raise_for_status()

    ensembl_json = result.json()
    return ensembl_json['Translation']['id']
