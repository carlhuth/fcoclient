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

from fcoclient.commands.base import Command
from fcoclient.config import Config


class ConfigureCmd(Command):

    require_client = False

    @staticmethod
    def add_subparser(subparsers):
        parser = subparsers.add_parser("configure", help="Configure client")
        parser.add_argument("url", help="FCO URL")
        parser.add_argument("username", help="FCO username")
        parser.add_argument("customer", help="FCO customer")
        parser.add_argument("password", help="FCO password")
        return parser

    def configure(self, args):
        self.logger.info("Configuring client")
        config = Config(url=args.url, username=args.username,
                        customer=args.customer, password=args.password)
        config.save(args.config)
        self.logger.info("Client configured")