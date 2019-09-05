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

    def __init__(self):
        pass

    def build_comments_email(self, request, mapping, action_type='added'):

        self.subject = "Comment {} for a mapping {}".format(action_type, mapping.mapping_id)

        recipient_details = settings.EMAIL_LIST.get(request.data.get('email_recipient_id'))
        self.to = [recipient_details.get('email')]

        self.from_email = "{} via Gifts <{}>".format(request.user.full_name, request.user.email)

        mapping_url = request.build_absolute_uri(reverse('add_retrieve_comments', args=[mapping.mapping_id]))

        self.body = "User: {} \n Comment: {} \n Action: {} \n Mapping URL: {}".format(
            request.user.full_name,
            request.data['text'],
            action_type.title(),
            mapping_url
        )

    def build_staus_email(self, request, mapping, action_type='added'):
        pass

    def send(self):

        email = EmailMessage(self.subject, self.body, self.from_email, self.to)
        email.send()