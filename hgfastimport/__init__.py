''' import Git fast-import streams '''
from __future__ import absolute_import

from mercurial import (
    encoding,
    util,
    cmdutil,
)

from mercurial.i18n import _

from hgext.convert import (
    convcmd,
    hg,
)

from .hgimport import fastimport_source


# XXX sort options copied straight from hgext/convert/__init__.py
cmdtable = {}
command = cmdutil.command(cmdtable)

testedwith = '4.1'


@command("fastimport",
         [('', 'branchsort', None, _('try to sort changesets by branches')),
          ('', 'datesort', None, _('try to sort changesets by date')),
          ('', 'sourcesort', None, _('preserve source changesets order'))],
         _('hg fastimport SOURCE ...'),
         norepo=False)
def fastimport(ui, repo, *sources, **opts):
    """Convert a git fastimport dump into Mercurial changesets.

    Reads a series of SOURCE fastimport dumps and adds the resulting
    changes to the current Mercurial repository.
    """
    # Would be nice to just call hgext.convert.convcmd.convert() and let
    # it take care of things.  But syntax and semantics are just a
    # little mismatched:
    #   - fastimport takes multiple source paths (mainly because cvs2git
    #     produces 2 dump files)
    #   - fastimport's dest is implicitly the current repo
    #
    # So for the time being, I have copied bits of convert() over here.
    # Boo, hiss.

    if not sources:
        sources = ("-")

    # assume fastimport metadata (usernames, commit messages) are
    # encoded UTF-8
    convcmd.orig_encoding = encoding.encoding
    encoding.encoding = 'UTF-8'

    # sink is the current repo, src is the list of fastimport streams
    destc = hg.mercurial_sink(ui, repo.root)
    srcc = fastimport_source(ui, repo, sources)

    # XXX figuring out sortmode copied straight from hgext/convert/convcmd.py
    defaultsort = 'branchsort'          # for efficiency and consistency
    sortmodes = ('branchsort', 'datesort', 'sourcesort')
    sortmode = [m for m in sortmodes if opts.get(m)]
    if len(sortmode) > 1:
        raise util.Abort(_('more than one sort mode specified'))
    sortmode = sortmode and sortmode[0] or defaultsort

    # not implemented: filemap, revmapfile
    revmapfile = destc.revmapfile()
    c = convcmd.converter(ui, srcc, destc, revmapfile, opts)
    c.convert(sortmode)
