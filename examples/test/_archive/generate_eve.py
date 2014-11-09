from JumpScale import j

import pystache

j.application.start("osistest")
import JumpScale.grid.osis

# cl=j.core.osis.getOsisModelClass("test_complextype","project")

import time

client = j.core.osis.getClientByInstance('main')

json=client.getOsisSpecModel("oss")

from IPython import embed
print "DEBUG NOW ooo"
embed()



def testHB():

    clienthb=j.core.osis.getClientForCategory(client,"system","user")

# print client.listNamespaces()

# clientnode=j.core.osis.getClientForCategory(client,"system","node")

# clientvfs=j.core.osis.getClientForCategory(client,"osismodel","vfs")
# vfs=clientvfs.new()

# obj=testSet(clientnode)


j.application.stop()

#@todo (P2) create test suite on znode (auto tests)
#@todo (P2) patch pyelasticsearch to work well in gevent so it does not block (monkey patching of socket)
#@todo (P2) patch & check osisclient to work non blocking when in gevent
#@todo (P3) put arakoon as backend (in stead of filesystem db)
#@todo (P3) refactor arakoon client to have nice config files in hrd format (see osis dir)
