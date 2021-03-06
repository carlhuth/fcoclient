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
Module with virtual data center related functionality.
"""

from fcoclient.resources.base import BaseClient, Resource, ResourceType


class Vdc(Resource):
    """
    Class representing virtual data center.
    """

    resource_type = ResourceType.vdc


class VdcClient(BaseClient):
    """
    Client providing access to virtual data centers.
    """

    klass = Vdc
