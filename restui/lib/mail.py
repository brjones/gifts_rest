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

    def build_subject(self, subject="Notification from Gifts"):
        self.subject = subject

    def build_to_list(self):
        recipient_ids = self.request.data.get('email_recipient_ids')
        if not recipient_ids:
            return False
        self.to = [settings.EMAIL_RECIPIENT_LIST.get(recipient_id).get('email') for recipient_id in recipient_ids]
        return True

    def build_from_address(self):
        self.from_email = "{} via Gifts <{}>".format(self.request.user.full_name, self.request.user.email)

    def build_comments_email(self, mapping):

        self.build_subject("Comment added for mapping {}".format(mapping.mapping_id))
        self.build_from_address()

        if not self.build_to_list():
            return False

        mapping_url = self.request.build_absolute_uri(reverse('get_mapping', args=[mapping.mapping_id]))

        self.body = "User: {} \n Comment: {} \n Mapping URL: {}".format(
            self.request.user.full_name,
            self.request.data['text'],
            mapping_url
        )
        return True


    def build_unmapped_comments_email(self, mapping_view_id):

        self.build_subject("Comment added for unmapped entry {}".format(mapping_view_id))
        self.build_from_address()

        if not self.build_to_list():
            return False

        unmapped_entry_url = self.request.build_absolute_uri(reverse('get_unmapped_entry', args=[mapping_view_id]))

        self.body = "User: {} \n Comment: {} \n Unmapped Entry URL: {}".format(
            self.request.user.full_name,
            self.request.data['text'],
            unmapped_entry_url
        )
        return True

    def build_status_change_email(self, mapping, prev_status, current_status):

        self.build_subject("Status changed for mapping {}".format(mapping.mapping_id))
        self.build_from_address()

        if not self.build_to_list():
            return False

        mapping_url = self.request.build_absolute_uri(reverse('get_mapping', args=[mapping.mapping_id]))

        self.body = "User: {} \n Previous status: {} \n Current status: {} \n Mapping URL: {}".format(
            self.request.user.full_name,
            prev_status,
            current_status,
            mapping_url
        )
        return True


    def build_unmapped_status_change_email(self, mapping_view_id, prev_status, current_status):

        self.build_subject("Status changed for unmapped entry {}".format(mapping_view_id))
        self.build_from_address()

        if not self.build_to_list():
            return False

        unmapped_entry_url = self.request.build_absolute_uri(reverse('get_unmapped_entry', args=[mapping_view_id]))

        self.body = "User: {} \n Previous status: {} \n Current status: {} \n Unmapped entry URL: {}".format(
            self.request.user.full_name,
            prev_status,
            current_status,
            unmapped_entry_url
        )
        return True



    def send(self):
        email = EmailMessage(self.subject, self.body, self.from_email, self.to)
        email.send()