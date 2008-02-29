from mercurial import commands

import parser
import hgechoprocessor
import hgimport

def fastimport(ui, repo, source, **opts):
    ui.write("Source is %s\n" % source)
    f = open(source)
    proc = hgimport.HgImportProcessor(ui, repo, **opts)
    #proc = hgechoprocessor.HgEchoProcessor(ui, repo, **opts)
    p = parser.ImportParser(f)
    proc.process(p.iter_commands)

cmdtable = {
    "fastimport":
        (fastimport,
         [],
         'hg fastimport SOURCE')
}
