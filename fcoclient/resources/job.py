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
Module with job related functionality.
"""

import time

from requests import codes

from fcoclient.resources.base import JobStatus  # noqa
from fcoclient.resources.base import BaseClient, Job


class JobClient(BaseClient):
    """
    Job client.

    This class groups all operations that can be executed on jobs.
    """

    klass = Job

    def wait(self, job):
        while not job.status.is_terminal:
            time.sleep(3)
            job = self.get(uuid=job.uuid)
        return job

    def delete(self, uuid, cascade=False):
        """
        Delete job.

        Job is deleted synchronously and thus needs it's own delete
        implementation.

        Args:
            uuid (str): UUID of the job being deleted.
            cascade (bool): Control whether child resources are also deleted
                or not. This parameter is ignored and set to ``False``
                unconditionally.
        """
        endpoint = "{}/{}".format(self.endpoint, uuid)
        data = {"cascade": False}
        self.client.delete(endpoint, data, codes.ok)
