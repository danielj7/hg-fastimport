from mercurial import encoding
from hgext.convert import convcmd, hg

from fastimport import parser
from hgfastimport.hgimport import fastimport_source

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

    # assume fastimport metadata (usernames, commit messages) are
    # encoded UTF-8
    convcmd.orig_encoding = encoding.encoding
    encoding.encoding = 'UTF-8'

    # sink is the current repo, src is the list of fastimport streams
    destc = hg.mercurial_sink(ui, repo.root)
    srcc = fastimport_source(ui, repo, sources)

    # TEMP hack to keep old behaviour and minimize test churn
    # (this should be an option to fastimport)
    opts['datesort'] = True

    # not implemented: filemap, revmapfile
    revmapfile = destc.revmapfile()
    c = convcmd.converter(ui, srcc, destc, revmapfile, opts)
    c.convert()

cmdtable = {
    "fastimport":
        (fastimport,
         [],
         'hg fastimport SOURCE ...')
}
