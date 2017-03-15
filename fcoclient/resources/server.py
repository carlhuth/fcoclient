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
Module with server related functionality.
"""

from requests import codes

from fcoclient.resources.base import BaseClient, Resource, ResourceType
from fcoclient.resources.job import Job


class Server(Resource):
    """
    Class representing server resource.
    """

    resource_type = ResourceType.server

    @staticmethod
    def skeleton():
        return Server("{SERVER PRODUCT OFFER UUID}", "{SERVER NAME}",
                      "{VDC UUID}")

    def __init__(self, productOfferUUID, resourceName, vdcUUID, **rest):
        """
        Create new server resource.

        Detailed description of available fields can be found at server_ docs.

        .. _server: http://docs.flexiant.com/display/DOCS/REST+Server

        Args:
            productOfferUUID: UUID of the offer
            resourceName: Name of new server
            vdcUUID: UUID of the VDC where server will reside
            **rest: Additional skeleton fields
        """
        super(Server, self).__init__({
            "productOfferUUID": productOfferUUID,
            "resourceName": resourceName,
            "vdcUUID": vdcUUID,
        }, **rest)


class ServerClient(BaseClient):
    """
    Client that provides access to server-specific functionality.
    """

    klass = Server

    def create(self, skeleton):
        """
        Create new server.

        Server creation is asynchronous operation and needs to be tracked
        using job object that is returned.

        Args:
            skeleton (:obj:`Server`): Server skeleton.

        Returns:
           :obj:`Job`: New job, describing creation progress.
        """
        data = {"skeletonServer": skeleton}
        return Job(self.client.post(self.endpoint, data, codes.accepted))
