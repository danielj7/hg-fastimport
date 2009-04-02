from mercurial import commands

import parser
import hgechoprocessor
import hgimport

def fastimport(ui, repo, *sources, **opts):
    proc = hgimport.HgImportProcessor(ui, repo, **opts)
    #proc = hgechoprocessor.HgEchoProcessor(ui, repo, **opts)
    proc.setup()
    try:
        for source in sources:
            ui.write("Reading source: %s\n" % source)
            f = open(source)
            p = parser.ImportParser(f)
            proc._process(p.iter_commands)
            f.close()
    finally:
        proc.teardown()

cmdtable = {
    "fastimport":
        (fastimport,
         [],
         'hg fastimport SOURCE ...')
}
