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
from fcoclient.resources.server import ServerStatus


class ServerCmd(Command):

    @staticmethod
    def add_subparser(subparsers):
        parser = subparsers.add_parser("server", help="Manage servers")
        subs = parser.add_subparsers()

        Command.create_get_parser(subs, "server")
        Command.create_list_parser(subs, "servers")
        Command.create_skeleton_parser(subs, "server")
        Command.create_new_parser(subs, "server")
        Command.create_delete_parser(subs, "server")

        sub = subs.add_parser("start", help="Start server")
        sub.add_argument("uuid", help="UUID of the server")
        sub.add_argument("-w", "--wait", action="store_true",
                         help="Wait for server to start")

        sub = subs.add_parser("stop", help="Stop server")
        sub.add_argument("uuid", help="UUID of the server")
        sub.add_argument("-w", "--wait", action="store_true",
                         help="Wait for server to stop")

        return parser

    @property
    def resource_client(self):
        return self.client.server

    def create(self, args):
        self.logger.info("Creating new server")
        skeleton = json.load(args.skeleton)
        job = self.client.server.create(skeleton)
        if args.wait:
            self.logger.info("Waiting for server creation to terminate")
            job = self.client.job.wait(job.uuid)
            utils.output_json(job)
            self.logger.info("Server creation terminated")
        else:
            utils.output_json(job)
            self.logger.info("Server creation scheduled")

    def delete(self, args):
        self.logger.info("Deleting server")
        job = self.client.server.delete(args.uuid, cascade=args.cascade)
        if args.wait:
            self.logger.info("Waiting for server deletion to terminate")
            job = self.client.job.wait(job.uuid)
            utils.output_json(job)
            self.logger.info("Server deletion terminated")
        else:
            utils.output_json(job)
            self.logger.info("Server deletion scheduled")

    def start(self, args):
        self.logger.info("Starting server")
        job = self.client.server.start(args.uuid)
        if args.wait:
            self.logger.info("Waiting for server to start")
            server = self.client.server.wait(job.monitored_item_uuid,
                                             ServerStatus.running)
            utils.output_json(server)
            self.logger.info("Server started")
        else:
            utils.output_json(job)
            self.logger.info("Server start scheduled")

    def stop(self, args):
        self.logger.info("Stopping server")
        job = self.client.server.stop(args.uuid)
        if args.wait:
            self.logger.info("Waiting for server to stop")
            server = self.client.server.wait(job.monitored_item_uuid,
                                             ServerStatus.stopped)
            utils.output_json(server)
            self.logger.info("Server stopped")
        else:
            utils.output_json(job)
            self.logger.info("Server stop scheduled")
