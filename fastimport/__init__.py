from mercurial import commands

import parser
#import dates
#import commands
#from fastimport.hgechoprocessor import HgEchoProcessor
import hgechoprocessor
#import hhhh
#from hhhh import HgEchoProcessor

def fastimport(ui, repo, source, **opts):
    ui.write("Source is %s\n" % source)
    f = open(source)
    proc = hgechoprocessor.HgEchoProcessor(ui, repo, **opts)
    p = parser.ImportParser(f)
    proc.process(p.iter_commands)

cmdtable = {
    "fastimport":
        (fastimport,
         [],
         'hg fastimport SOURCE')
}
