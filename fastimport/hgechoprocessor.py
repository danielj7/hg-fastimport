# Copyright (C) 2008 Canonical Ltd
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""Processor of import commands.

This module provides core processing functionality including an abstract class
for basing real processors on. See the processors package for examples.
"""


import processor

class HgEchoProcessor(processor.ImportProcessor):
    
    def __init__(self, ui, repo, **opts):
        self.ui = ui
        self.repo = repo
        self.opts = opts
        self.finished = False
        
    def progress_handler(self, cmd):
        self.ui.write(cmd.dump_str(verbose=True) + "\n")

    def blob_handler(self, cmd):
        self.ui.write(cmd.dump_str(verbose=True) + "\n")

    def checkpoint_handler(self, cmd):
        self.ui.write(cmd.dump_str(verbose=True) + "\n")

    def commit_handler(self, cmd):
        commit_handler = HgEchoCommitHandler(cmd, self.ui, self.repo, **self.opts)
        commit_handler.process()
        self.ui.write(cmd.dump_str(verbose=True) + "\n")

    def reset_handler(self, cmd):
        self.ui.write(cmd.dump_str(verbose=True) + "\n")

    def tag_handler(self, cmd):
        self.ui.write(cmd.dump_str(verbose=True) + "\n")

class HgEchoCommitHandler(processor.CommitHandler):

    def __init__(self, command, ui, repo, **opts):
        self.command = command
        self.ui = ui
        self.repo = repo
        self.opts = opts

    def modify_handler(self, filecmd):
        self.ui.write(filecmd.dump_str(verbose=True) + "\n")

    def delete_handler(self, filecmd):
        self.ui.write(filecmd.dump_str(verbose=True) + "\n")

    def copy_handler(self, filecmd):
        self.ui.write(filecmd.dump_str(verbose=True) + "\n")

    def rename_handler(self, filecmd):
        self.ui.write(filecmd.dump_str(verbose=True) + "\n")

    def deleteall_handler(self, filecmd):
        self.ui.write(filecmd.dump_str(verbose=True) + "\n")
