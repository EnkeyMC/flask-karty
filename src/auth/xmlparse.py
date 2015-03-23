# -*- coding: utf-8 -*-
"""

    ~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2012 by Aukce Elevo s.r.o.
"""
import xmltodict
#from xml.etre
class RemoveFirstLine:
    def __init__(self, f):
        self.f = f
        self.xmlTagFound = False

    def __getattr__(self, attr):
        return getattr(self, self.f)

    def write(self, s):
        if not self.xmlTagFound:
            x = 0 # just to be safe
            for x, c in enumerate(s):
                if c == '>':
                    self.xmlTagFound = True
                    break
            self.f.write(s[x+1:])
        else:
            self.f.write(s)

def mujxmlparse(data):
    doc=xmltodict.parse(RemoveFirstLine(data), xml_attribs=True)
    print doc['DATAPACKET']['METADATA']
    print doc['DATAPACKET']['ROWDATA']['ROW']
    return True