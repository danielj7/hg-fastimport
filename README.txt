hg-fastimport
-------------

WARNING: this extension is incomplete and lightly tested.  It is
currently intended for Mercurial developers or particularly daring
users.

hg-fastimport is a Mercurial extension for importing Git's fast-import
dumps into Mercurial.  fast-import is a file format for representing the
entire history of a version control repository.

This file format was designed to make it easier to write tools which
convert from foreign (non-Git) VCS repository formats into Git; such
tools exist for CVS, Mercurial, Darcs, and Perforce.

However, there's no reason Git should be the only VCS to read
git-fast-import files; for example, Bazaar has a fastimport extension
similar in scope and aim to hg-fastimport.  (In fact, hg-fastimport
draws heavily on the work done for bzr-fastimport.)

The goal of hg-fastimport is to make it just as easy to populate a
Mercurial repository from a fastimport dump as it is for Bazaar or Git.


DEPENDENCIES
------------

hg-fastimport requires Mercurial 1.3.

hg-fastimport depends on the python-fastimport library (which was extracted
from bzr-fastimport).  python-fastimport lives on launchpad.net at

  https://code.launchpad.net/python-fastimport

To make the 'fastimport' package provided by python-fastimport available
to hg-fastimport, you need to add the python-fastimport directory to
PYTHONPATH, e.g.

  PYTHONPATH=$HOME/src/pyfastimport

It should also be possible to install python-fastimport from cheeshop:

 $ easy_install install python-fastimport

And most Linux distributions have it packaged.

USAGE
-----

To use hg-fastimport, add a line like

  fastimport = /path/to/hg-fastimport/hgfastimport

to the [extensions] section of your hgrc.  Don't forget to set
PYTHONPATH as explained above.

To import into a brand-new Mercurial repository:

  hg init new
  hg -R new fastimport FILE...

where FILE... is a list of one or more fast-import dumps.


TESTING
-------

hg-fastimport uses Mercurial's own testing infrastructure, so you will
need a copy of the Mercurial source handy.  For example, I keep a clone
of Mercurial "crew" in ~/src/hg-crew.  To test hg-fastimport:

  cd tests
  ~/src/hg-crew/tests/run-tests.py --local


FURTHER READING
---------------

The fast-import format is documented in the git-fast-import(1) man page:

  http://www.kernel.org/pub/software/scm/git-core/docs/git-fast-import.html

Tools to convert various version control repositories to
fast-import format:

  http://cvs2svn.tigris.org/cvs2git.html    (CVS)
  http://repo.or.cz/w/fast-export.git       (Mercurial, Subversion)
  http://repo.or.cz/w/darcs2git.git         (Darcs)


AVAILABILITY
------------

You can get the latest copy of hg-fastimport from its public Mercurial
repository:

  hg clone http://vc.gerg.ca/hg/hg-fastimport


AUTHORS
-------

original author:
  Paul Crowley <paul at lshift dot net>
  LShift Ltd

derived from bzr-fastimport by:
  Ian Clatworthy <ian.clatworthy at internode dot on dot net>
  Canonical Ltd

current maintainer:
  Greg Ward <greg-hg at gerg dot ca>

contributors:
  Paul Aurich <paul at darkrain42 dot org>
  Jelmer Vernooij <jelmer at samba dot org>


COPYRIGHT
---------

Copyright (C) 2008 Canonical Ltd
Copyright (C) 2008 LShift Ltd.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
