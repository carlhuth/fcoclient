
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

import json

from fcoclient import utils
from fcoclient.commands.base import Command


class DiskCmd(Command):

    @staticmethod
    def add_subparser(subparsers):
        parser = subparsers.add_parser("disk", help="Manage disks")
        subs = parser.add_subparsers()

        Command.create_get_parser(subs, "disk")
        Command.create_list_parser(subs, "disks")
        Command.create_skeleton_parser(subs, "disk")
        Command.create_new_parser(subs, "disk")
        Command.create_delete_parser(subs, "disk")

        return parser

    @property
    def resource_client(self):
        return self.client.disk

    def create(self, args):
        self.logger.info("Creating new disk")
        skeleton = json.load(args.skeleton)
        job = self.client.disk.create(skeleton)
        if args.wait:
            self.logger.info("Waiting for disk creation to terminate")
            job = self.client.job.wait(job)
            utils.output_json(job)
            self.logger.info("Disk creation terminated")
        else:
            utils.output_json(job)
            self.logger.info("Disk creation scheduled")

    def delete(self, args):
        self.logger.info("Deleting disk")
        job = self.client.disk.delete(args.uuid)
        if args.wait:
            self.logger.info("Waiting for disk deletion to terminate")
            job = self.client.job.wait(job)
            utils.output_json(job)
            self.logger.info("Disk deletion terminated")
        else:
            utils.output_json(job)
            self.logger.info("Disk deletion scheduled")
