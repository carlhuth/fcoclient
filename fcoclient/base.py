# Copyright (c) 2017 XLAB d.o.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Module with base types.

Classes in this module serve as a base for all other resources and clients.
"""

from requests import codes

from fcoclient import exceptions


class Resource(dict):
    """
    Resource is simple data container with few additional helpers.
    """

    resource_type = None
    skeleton_args = None

    @property
    def uuid(self):
        """
        Convenience accessor for resourceUUID.
        """
        return self["resourceUUID"]

    @property
    def name(self):
        """
        Convenience accessor for resourceName.
        """
        return self["resourceName"]

    @staticmethod
    def normalize(data):
        """
        Replace shorthands 'uuid' and 'name' with full names. All other key
        value pairs are left intact. This is another convenience for writing
        filter experessions using name and uuid keys.
        """
        reps = {
            "name": "resourceName",
            "uuid": "resourceUUID",
        }
        return {reps.get(k, k): v for k, v in data.items()}

    def __str__(self):
        return "{}({})".format(self.resource_type, self.uuid)


class BaseClient(object):
    """
    Base client that contains common functionality for all FCO clients.
    """

    _prefix = "resources"
    klass = None

    @staticmethod
    def _get_filter(conditions):
        """
        Construct a filter expression for FCO API.
        """
        conds = [{"field": k, "value": [v], "condition": "IS_EQUAL_TO"}
                 for k, v in conditions.items()]
        return {"filterConditions": conds}

    @staticmethod
    def _get_query_limit(no_items):
        """
        Construct query limit expression for FCO API.
        """
        return {
            "from": 0,
            "to": no_items,
            "maxRecords": no_items,
            "loadChildren": True,
            "orderBy": [{
                "aggregationFunction": None,
                "fieldName": "resourceName",
                "sortOrder": "ASC",
            }],
        }

    def __init__(self, client):
        assert self.klass is not None, \
            "'klass' not set for '{}'.".format(self.__class__)
        assert self.klass.resource_type is not None, \
            "'resource_type' not set for '{}'.".format(self.klass)
        self.client = client
        self.endpoint = "{}/{}".format(self._prefix, self.klass.resource_type)

    def list(self, no_items=200, **conditions):
        """
        List items that match conditions.

        Use this method to retrieve list of resources from FCO API that match
        all of the conditions. This method does not raise any exception when
        no resource matches conditions specified.

        Args:
            no_items (int): Maximum number of items to return.
            **conditions: Conditions that are used to filter the resources.

        Returns:
            List of resources that match conditions.
        """
        endpoint = self.endpoint + "/list"
        data = {}
        conditions = Resource.normalize(conditions)
        data["searchFilter"] = self._get_filter(conditions)
        data["queryLimit"] = self._get_query_limit(no_items)
        resources = self.client.post(endpoint, data, codes.ok)["list"]
        return [self.klass(**r) for r in resources]

    def get(self, **conditions):
        """
        Retrieve single resource that matches conditions.

        Use this method to retrieve single resource from FCO API that match
        all of the conditions. If the conditions do not describe a resource
        uniquely, exception is raised.

        Args:
            **conditions: Conditions that are used to filter the resources.

        Returns:
            List of resources that match conditions.

        Raises:
            NonUniqueResourceError: If more than one resource matches.
            NoSuchResourceError: If no resource matches conditions.
        """
        data = self.list(**conditions)
        if len(data) > 1:
            raise exceptions.NonUniqueResourceError(conditions)
        elif len(data) < 1:
            raise exceptions.NoSuchResourceError(conditions)
        return data[0]

    def skeleton(self):
        """
        Produce resource skeleton object.

        Skeletons are bare bones resources that have only bare minimum of
        parameters set in order to be fully functional. These skeletons are
        used in resource creation process.

        In order to make this skeleton useful, ``{REPLACE_ME}`` placeholders
        need to be replaced by actual, valid data from FCO.

        Returns:
            Skeleton object for resource that client handles.
        """
        args = ["{REPLACE_ME}"] * self.klass.skeleton_args
        return self.klass(*args)
