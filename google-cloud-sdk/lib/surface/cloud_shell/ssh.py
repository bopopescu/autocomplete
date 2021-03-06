# Copyright 2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""cloud-shell ssh command."""

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.cloud_shell import util
from googlecloudsdk.command_lib.util.ssh import containers
from googlecloudsdk.command_lib.util.ssh import ssh
from googlecloudsdk.core import log


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class SshAlpha(base.Command):
  """Allows you to establish an interactive SSH session with Cloud Shell."""

  detailed_help = {
      'DESCRIPTION':
          """\
        *{command}* lets you remotely log in to Cloud Shell. If your Cloud Shell
        is not currently running, this will cause it to be started before
        establishing the SSH session.
        """,
      'EXAMPLES':
          """\
        To SSH into your Cloud Shell, run:

            $ {command}

        To run a remote command in your Cloud Shell, run:

            $ {command} --command=ls
        """,
  }

  @staticmethod
  def Args(parser):
    util.ParseCommonArgs(parser)
    parser.add_argument(
        '--command',
        help="""\
        A command to run in Cloud Shell.

        Runs the command in Cloud Shell and then exits.
        """)
    parser.add_argument(
        '--dry-run',
        help="""\
        If provided, prints the command that would be run to standard out
        instead of executing it.
        """,
        action='store_true')
    parser.add_argument(
        '--ssh-flag',
        help='Additional flags to be passed to *ssh(1)*.',
        action='append')

  def Run(self, args):
    command_list = args.command.split(' ') if args.command else None
    connection_info = util.PrepareEnvironment(args)
    command = ssh.SSHCommand(
        remote=ssh.Remote(host=connection_info.host, user=connection_info.user),
        port=str(connection_info.port),
        identity_file=connection_info.key,
        remote_command=containers.GetRemoteCommand(None, command_list),
        extra_flags=args.ssh_flag,
        tty=containers.GetTty(None, args.command),
        options={'StrictHostKeyChecking': 'no'},
    )

    if args.dry_run:
      log.Print(' '.join(command.Build(connection_info.ssh_env)))
    else:
      command.Run(connection_info.ssh_env)
