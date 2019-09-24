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


class GiftsRouter(object):
    """
    This is for use when there are multiple databases and deciding on which of
    the dbs should be searched
    """

    def db_for_read(self, model, **hints):
        "Point all operations on restui models to 'gifts'"
        if model._meta.app_label == 'restui':
            return 'gifts'
        return 'default'

    def db_for_write(self, model, **hints):
        "Point all operations on restui models to 'gifts'"
        if model._meta.app_label == 'restui':
            return 'gifts'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation if a both models in restui app"
        if obj1._meta.app_label == 'restui' and obj2._meta.app_label == 'restui':
            return True
        # Allow if neither is chinook app
        elif 'restui' not in [obj1._meta.app_label, obj2._meta.app_label]:
            return True
        return False

    def allow_syncdb(self, db, model):
        if db == 'gifts' or model._meta.app_label == "restui":
            return False  # we're not using syncdb on our legacy database
        else:  # but all other models/databases are fine
            return True
