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

from django.core.mail import EmailMessage
from django.conf import settings
from django.urls import reverse


class GiftsEmail(object):

    def __init__(self, request):
        self.request = request
        self.subject = None
        self.to = None
        self.from_email = None
        self.body = None

    def build_comments_email(self, mapping, action_type='added'):

        self.subject = "Comment {} for a mapping {}".format(action_type, mapping.mapping_id)

        recipient_ids = self.request.data.get('email_recipient_ids')

        if not recipient_ids:
            return False

        self.to = [settings.EMAIL_RECIPIENT_LIST.get(recipient_id).get('email') for recipient_id in recipient_ids]

        self.from_email = "{} via Gifts <{}>".format(self.request.user.full_name, self.request.user.email)

        mapping_url = self.request.build_absolute_uri(reverse('add_retrieve_comments', args=[mapping.mapping_id]))

        self.body = "User: {} \n Comment: {} \n Action: {} \n Mapping URL: {}".format(
            self.request.user.full_name,
            self.request.data['text'],
            action_type.title(),
            mapping_url
        )

        return True

    def build_status_email(self, status, action_type='added'):
        pass

    def send(self):

        email = EmailMessage(self.subject, self.body, self.from_email, self.to)
        email.send()