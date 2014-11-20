"""
Original code Copyright 2009 [Waylan Limberg](http://achinghead.com)

All changes Copyright 2008-2014 The Python Markdown Project

Changed by Mohammad Tayseer to add CSS classes to table

License: [BSD](http://www.opensource.org/licenses/bsd-license.php)

"""

from __future__ import absolute_import
from __future__ import unicode_literals
from markdown import Extension
from markdown.extensions.tables import TableProcessor
from markdown.util import etree

class BootstrapTableProcessor(TableProcessor):

    # This method actually was copied from TableProcessor.run. The only change is adding
    # `table.set('class', 'table')` to set Bootstrap table class
    def run(self, parent, blocks):
        """ Parse a table block and build table. """
        block = blocks.pop(0).split('\n')
        header = block[0].strip()
        seperator = block[1].strip()
        rows = block[2:]
        # Get format type (bordered by pipes or not)
        border = False
        if header.startswith('|'):
            border = True
        # Get alignment of columns
        align = []
        for c in self._split_row(seperator, border):
            if c.startswith(':') and c.endswith(':'):
                align.append('center')
            elif c.startswith(':'):
                align.append('left')
            elif c.endswith(':'):
                align.append('right')
            else:
                align.append(None)
        # Build table
        table = etree.SubElement(parent, 'table')
        table.set('class', 'table')
        thead = etree.SubElement(table, 'thead')
        self._build_row(header, thead, align, border)
        tbody = etree.SubElement(table, 'tbody')
        for row in rows:
            self._build_row(row.strip(), tbody, align, border)

class BootstrapTableExtension(Extension):
    """ Add tables to Markdown. """

    def extendMarkdown(self, md, md_globals):
        """ Add an instance of TableProcessor to BlockParser. """
        md.parser.blockprocessors.add('bootstraptable', 
                                      BootstrapTableProcessor(md.parser),
                                      '<hashheader')


def makeExtension(*args, **kwargs):
    return BootstrapTableExtension(*args, **kwargs)

