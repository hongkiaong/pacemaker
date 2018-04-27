''' Corosync-specific class for Pacemaker's Cluster Test Suite (CTS)
'''

# Pacemaker targets compatibility with Python 2.7 and 3.2+
from __future__ import print_function, unicode_literals, absolute_import, division

__copyright__ = "Copyright 2007-2018 Andrew Beekhof <andrew@beekhof.net>"
__license__ = "GNU General Public License version 2 or later (GPLv2+) WITHOUT ANY WARRANTY"

from cts.CTSvars import *
from cts.CM_common  import crm_common
from cts.CTS     import Process
from cts.patterns    import PatternSelector

class crm_corosync(crm_common):
    '''
    Corosync version 2 cluster manager class
    '''
    def __init__(self, Environment, randseed=None, name=None):
        if not name: name="crm-corosync"
        crm_common.__init__(self, Environment, randseed=randseed, name=name)

        self.fullcomplist = {}
        self.templates = PatternSelector(self.name)

    def Components(self):
        complist = []
        if not len(list(self.fullcomplist.keys())):
            for c in ["cib", "lrmd", "crmd", "attrd" ]:
                self.fullcomplist[c] = Process(
                    self, c, 
                    pats = self.templates.get_component(self.name, c),
                    badnews_ignore = self.templates.get_component(self.name, "%s-ignore" % c),
                    common_ignore = self.templates.get_component(self.name, "common-ignore"))

            # pengine uses dc_pats instead of pats
            self.fullcomplist["pengine"] = Process(
                self, "pengine", 
                dc_pats = self.templates.get_component(self.name, "pengine"),
                badnews_ignore = self.templates.get_component(self.name, "pengine-ignore"),
                common_ignore = self.templates.get_component(self.name, "common-ignore"))

            # stonith-ng's process name is different from its component name
            self.fullcomplist["stonith-ng"] = Process(
                self, "stonith-ng", process="stonithd", 
                pats = self.templates.get_component(self.name, "stonith"),
                badnews_ignore = self.templates.get_component(self.name, "stonith-ignore"),
                common_ignore = self.templates.get_component(self.name, "common-ignore"))

            # add (or replace) extra components
            self.fullcomplist["corosync"] = Process(
                self, "corosync", 
                pats = self.templates.get_component(self.name, "corosync"),
                badnews_ignore = self.templates.get_component(self.name, "corosync-ignore"),
                common_ignore = self.templates.get_component(self.name, "common-ignore")
            )

        # Processes running under valgrind can't be shot with "killall -9 processname",
        # so don't include them in the returned list
        vgrind = self.Env["valgrind-procs"].split()
        for key in list(self.fullcomplist.keys()):
            if self.Env["valgrind-tests"]:
                if key in vgrind:
                    self.log("Filtering %s from the component list as it is being profiled by valgrind" % key)
                    continue
            if key == "stonith-ng" and not self.Env["DoFencing"]:
                continue
            complist.append(self.fullcomplist[key])

        return complist