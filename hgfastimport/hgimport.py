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

import os
import os.path
import errno
import shutil

import mercurial.hg
import mercurial.commands
from mercurial import util
from mercurial.node import nullrev, hex

from fastimport import processor
from hgfastimport import hgechoprocessor

class HgImportProcessor(processor.ImportProcessor):
    
    def __init__(self, ui, repo, **opts):
        super(HgImportProcessor, self).__init__()
        self.ui = ui
        self.repo = repo
        self.opts = opts
        self.last_commit = None         # CommitCommand object
        self.mark_map = {}              # map mark (e.g. ":1") to revision number
        self.branch_map = {}            # map git branch name to revision number
        self.lightweight_tags = []      # list of (ref, mark) tuples

        self.numblobs = 0               # for progress reporting
        self.blobdir = None

    def setup(self):
        """Setup before processing any streams."""
        pass

    def teardown(self):
        """Cleanup after processing all streams."""
        # Hmmm: this isn't really a cleanup step, it's a post-processing
        # step.  But we currently have one processor per input
        # stream... despite the fact that state like mark_map,
        # branch_map, and lightweight_tags really should span input
        # streams.
        self.write_lightweight_tags()

        if self.blobdir and os.path.exists(self.blobdir):
            self.ui.status("Removing blob dir %r ...\n" % self.blobdir)
            shutil.rmtree(self.blobdir)

    def progress_handler(self, cmd):
        self.ui.write("Progress: %s\n" % cmd.message)

    def blob_handler(self, cmd):
        if self.blobdir is None:        # no blobs seen yet
            # XXX cleanup?
            self.blobdir = os.path.join(self.repo.root, ".hg", "blobs")
            os.mkdir(self.blobdir)

        fn = self.getblobfilename(cmd.id)
        blobfile = open(fn, "wb")
        #self.ui.debug("writing blob %s to %s (%d bytes)\n"
        #              % (cmd.id, fn, len(cmd.data)))
        blobfile.write(cmd.data)
        blobfile.close()

        self.numblobs += 1
        if self.numblobs % 500 == 0:
            self.ui.status("%d blobs read\n" % self.numblobs)

    def getblobfilename(self, blobid):
        if self.blobdir is None:
            raise RuntimeError("no blobs seen, so no blob directory created")
        # XXX should escape ":" for windows
        return os.path.join(self.blobdir, "blob-" + blobid)

    def checkpoint_handler(self, cmd):
        # This command means nothing to us
        pass

    def committish_rev(self, committish):
        if committish.startswith(":"):
            return self.mark_map[committish]
        else:
            return self.branch_map[committish]
        
    def commit_handler(self, cmd):
        # XXX this assumes the fixup branch name used by cvs2git.  In
        # contrast, git-fast-import(1) recommends "TAG_FIXUP" (not under
        # refs/heads), and implies that it can be called whatever the
        # creator of the fastimport dump wants to call it.  So the name
        # of the fixup branch should be configurable!
        fixup = (cmd.ref == "refs/heads/TAG.FIXUP")

        if fixup and self.last_commit is not None:
            # If this is a fixup commit, pretend it is on the same
            # branch as the previous commit.  This gives sensible
            # behaviour for selecting the first parent and for
            # determining the Mercurial branch name.
            cmd.ref = self.last_commit.ref

        if cmd.from_:
            first_parent = self.committish_rev(cmd.from_)
        else:
            first_parent = self.branch_map.get(cmd.ref, nullrev)
        #self.ui.write("First parent: %s\n" % first_parent)
        # Update to the first parent
        mercurial.hg.clean(self.repo, self.repo.lookup(first_parent))
        #self.ui.write("Bing\n")
        if cmd.merges:
            #self.ui.write("foo")
            if len(cmd.merges) > 1:
                raise NotImplementedError("Can't handle more than two parents")
            second_parent = self.committish_rev(cmd.merges[0])
            #self.ui.write("Second parent: %s\n" % second_parent)
            mercurial.commands.debugsetparents(self.ui, self.repo, 
                first_parent, second_parent)
        #self.ui.write("Bing\n")
        if cmd.ref == "refs/heads/master":
            branch = "default"
        else:
            branch = cmd.ref[len("refs/heads/"):]
        #self.ui.write("Branch: %s\n" % branch)
        self.repo.dirstate.setbranch(branch)
        #self.ui.write("Bing\n")
        #print "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv"
        commit_handler = HgImportCommitHandler(
            self, cmd, self.ui, self.repo, **self.opts)
        commit_handler.process()
        #print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
        #self.ui.write(cmd.dump_str(verbose=True))

        # in case we are converting from git or bzr, prefer author but
        # fallback to committer (committer is required, author is
        # optional)
        userinfo = cmd.author or cmd.committer
        user = "%s <%s>" % (userinfo[0], userinfo[1])

        # Blech: have to monkeypatch mercurial.encoding to ensure that
        # everything under rawcommit() assumes the same encoding,
        # regardless of current locale.
        from mercurial import encoding
        encoding.encoding = "UTF-8"

        files = commit_handler.filelist()
        assert type(cmd.message) is unicode
        text = cmd.message.encode("utf-8") # XXX cmd.message is unicode
        date = self.convert_date(userinfo)
        node = self.repo.rawcommit(
            files=files, text=text, user=user, date=date)
        rev = self.repo.changelog.rev(node)
        if cmd.mark is not None:
            self.mark_map[":" + cmd.mark] = rev
        if not fixup:
            self.branch_map[cmd.ref] = rev
            self.last_commit = cmd
        self.ui.write("Done commit of rev %d\n" % rev)
        #self.ui.write("%s\n" % self.mark_map)

    def convert_date(self, c):
        res = (int(c[2]), int(c[3]))
        #print c, res
        #print type((0, 0)), type(res), len(res), type(res) is type((0, 0))
        #if type(res) is type((0, 0)) and len(res) == 2:
        #    print "go for it"
        #return res
        return "%d %d" % res
        
    def reset_handler(self, cmd):
        if cmd.ref.startswith("refs/heads/"):
            # The usual case for 'reset': (re)create the named branch.
            # XXX what should we do if cmd.from_ is None?
            if cmd.from_ is not None:
                self.branch_map[cmd.ref] = self.committish_rev(cmd.from_)
            #else:
            #    # XXX filename? line number?
            #    self.ui.warn("ignoring branch reset with no 'from'\n")
        elif cmd.ref.startswith("refs/tags/"):
            # Create a "lightweight tag" in Git terms.  As I understand
            # it, that's a tag with no description and no history --
            # rather like CVS tags.  cvs2git turns CVS tags into Git
            # lightweight tags, so we should make sure they become
            # Mercurial tags.  But we don't have to fake a history for
            # them; save them up for the end.
            self.lightweight_tags.append((cmd.ref, cmd.from_))

    def tag_handler(self, cmd):
        pass

    def write_lightweight_tags(self):
        if not self.lightweight_tags:   # avoid writing empty .hgtags
            return

        # XXX what about duplicate tags?  lightweight_tags is
        # deliberately a list, to preserve order ... but do we need to
        # worry about repeated tags?  (Certainly not for cvs2git output,
        # since CVS has no tag history.)

        # Create Mercurial tags from git-style "lightweight tags" in the
        # input stream.
        self.ui.status("updating tags\n")
        mercurial.hg.clean(self.repo, self.repo.lookup("default"))
        tagfile = open(self.repo.wjoin(".hgtags"), "ab")
        for (ref, mark) in self.lightweight_tags:
            tag = ref[len("refs/tags/"):]
            rev = self.mark_map[mark]
            node = self.repo.changelog.node(rev)
            tagfile.write("%s %s\n" % (hex(node), tag))
        tagfile.close()

        files = [".hgtags"]
        self.repo.rawcommit(
            files=files, text="update tags", user="convert-repo", date=None)

class HgImportCommitHandler(processor.CommitHandler):

    def __init__(self, parent, command, ui, repo, **opts):
        self.parent = parent            # HgImportProcessor running the show
        self.command = command
        self.ui = ui
        self.repo = repo
        self.opts = opts
        self.files = set()

    def _make_container(self, path):
        if '/' in path:
            d = os.path.dirname(path)
            if not os.path.isdir(d):
                os.makedirs(d)
        
    def modify_handler(self, filecmd):
        #print "============================" + filecmd.path
        # FIXME: handle mode
        self.files.add(filecmd.path)
        fullpath = os.path.join(self.repo.root, filecmd.path)
        self._make_container(fullpath)
        #print "made dirs, writing file"
        if filecmd.dataref:
            # reference to a blob that has already appeared in the stream
            fn = self.parent.getblobfilename(filecmd.dataref)
            if os.path.exists(fullpath):
                os.remove(fullpath)
            try:
                os.link(fn, fullpath)
            except OSError, err:
                if err.errno == errno.ENOENT:
                    # if this happens, it's a problem in the fast-import
                    # stream
                    raise util.Abort("bad blob ref %r (no such file %s)"
                                     % (filecmd.dataref, fn))
                else:
                    # anything else is a bug in this extension
                    # (cross-device move, permissions, etc.)
                    raise
        elif filecmd.data:
            f = open(fullpath, "w")
            f.write(filecmd.data)
            f.close()
        else:
            raise RuntimeError("either filecmd.dataref or filecmd.data must be set")
        #print self.repo.add([filecmd.path])
        #print "Done:", filecmd.path

    def delete_handler(self, filecmd):
        self.files.add(filecmd.path)
        self.repo.remove([filecmd.path], unlink=True)

    #def copy_handler(self, filecmd):
    #    self.files.add(filecmd.path)
    #    """Handle a filecopy command."""
    #    self.ui.write("Cmd: %s\n" % repr(filecmd))

    #def rename_handler(self, filecmd):
    #    self.files.add(filecmd.path)
    #    """Handle a filerename command."""
    #    self.ui.write("Cmd: %s\n" % repr(filecmd))

    def filelist(self):
        return list(self.files)
