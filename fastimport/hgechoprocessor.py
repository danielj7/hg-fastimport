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
        """Process a ProgressCommand."""
        self.ui.write("Cmd: %s\n" % repr(cmd))

    def blob_handler(self, cmd):
        """Process a BlobCommand."""
        self.ui.write("Cmd: %s\n" % repr(cmd))

    def checkpoint_handler(self, cmd):
        """Process a CheckpointCommand."""
        self.ui.write("Cmd: %s\n" % repr(cmd))

    def commit_handler(self, cmd):
        """Process a CommitCommand."""
        self.ui.write("Commit: %s\n" % repr(cmd))
        commit_handler = HgEchoCommitHandler(cmd, self.ui, self.repo, **self.opts)
        commit_handler.process()
        self.ui.write("Done commit\n")

    def reset_handler(self, cmd):
        """Process a ResetCommand."""
        self.ui.write("Cmd: %s\n" % repr(cmd))

    def tag_handler(self, cmd):
        """Process a TagCommand."""
        self.ui.write("Cmd: %s\n" % repr(cmd))

    def finished(self):
        self.ui.write("Finished")

    def pre_handler(self, cmd):
        self.ui.write("Pre-handler: %s\n" % repr(cmd))

    def post_handler(self, cmd):
        self.ui.write("Post-handler: %s\n" % repr(cmd))

class HgEchoCommitHandler(processor.CommitHandler):

    def __init__(self, command, ui, repo, **opts):
        self.command = command
        self.ui = ui
        self.repo = repo
        self.opts = opts

    def process(self):
        self.pre_process_files()
        for fc in self.command.file_iter():
            try:
                handler = self.__class__.__dict__[fc.name[4:] + "_handler"]
            except KeyError:
                raise errors.MissingHandler(fc.name)
            else:
                handler(self, fc)
        self.post_process_files()

    def pre_process_files(self):
        """Prepare for committing."""
        pass

    def post_process_files(self):
        """Save the revision."""
        pass

    def modify_handler(self, filecmd):
        """Handle a filemodify command."""
        self.ui.write("Cmd: %s\n" % repr(filecmd))

    def delete_handler(self, filecmd):
        """Handle a filedelete command."""
        self.ui.write("Cmd: %s\n" % repr(filecmd))

    def copy_handler(self, filecmd):
        """Handle a filecopy command."""
        self.ui.write("Cmd: %s\n" % repr(filecmd))

    def rename_handler(self, filecmd):
        """Handle a filerename command."""
        self.ui.write("Cmd: %s\n" % repr(filecmd))

    def deleteall_handler(self, filecmd):
        """Handle a filedeleteall command."""
        self.ui.write("Cmd: %s\n" % repr(filecmd))
