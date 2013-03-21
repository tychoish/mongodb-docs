#!/usr/bin/python

from makefile_builder import MakefileBuilder
from mongodb_docs_meta import PUBLISHED_BRANCHES
import sys
import os.path

m = MakefileBuilder()

def generate_table_source_references():
    m.section_break('table sources', block='src')
    m.var(variable='table-output-source-tree',
          value='$(subst yaml,rst,$(shell find $(rst-include) -name "table-*.yaml"))', 
          block='src')

    outputs = ''
    for branch in PUBLISHED_BRANCHES:
        sources = [
            'build/' + branch + '/source/includes',
            'build/' + branch + '/branch-source/includes',
        ]

        for source_tree in sources:
            if os.path.isdir(source_tree): 
                m.append_var(variable='table-output-' + branch, 
                             value='$(subst yaml,rst,$(shell find ' + source_tree + '/ -name "table-*.yaml"))',
                             block='src')

        current_dir = 'build/' + branch + '/branch-source-current/includes'
        if os.path.isdir(current_dir): 
            m.append_var(variable='table-output-current',
                         value='$(subst yaml,rst,$(shell find ' + current_dir + '/ -name "table-*.yaml"))',
                         block='src')

        outputs += '$(table-output-' + branch + ') '

    m.var('table-output', '$(table-output-source-tree) ' + outputs, block='src' )

def generate_table_builders():
    m.section_break('table generator', block='gen')
    m.target('table-%.rst', 'table-%.yaml', block='gen')
    m.job('$(PYTHONBIN) bin/table_builder.py $< $@', block='gen')
    m.msg('[table-builder]: generated $@ table for inclusion')

    m.section_break('table builder helper targets', block='gen')

    phony_targets = 'clean-tables'

    builder_groups = PUBLISHED_BRANCHES 
    builder_groups.append('')

    m.newline(block='gen')
    for branch in builder_groups:
        if branch == '':
            args = ('tables', '$(table-output)')
        else:
            args = ('tables-' + branch, '$(table-output-' + branch + ')')

        phony_targets += ' ' + args[0]
        m.target(args[0], args[1], block='gen')
        m.job('git update-index --assume-unchanged', ignore=True, block='gen')
        m.msg('[' + args[0] + ']: cleansing git index of compiled tables', block='gen')
    
        phony_targets += ' clean-' + args[0]
        m.target('clean-' + args[0], block='gen')
        m.job('rm -rf ' + args[1], ignore=True, block='gen')
        m.newline(block='gen')

    phony_targets += ' tables-current clean-tables-current'  
    m.target('tables-current', '$(table-output-current)', block='gen')
    m.job('git update-index --assume-unchanged', ignore=True, block='gen')
    m.msg('[table-current]: cleansing git index of compiled tables', block='gen')

    m.target('clean-tables-current', block='gen')
    m.job('rm -rf $(tables-output-current)', ignore=True, block='gen')
    m.newline(block='gen')
    
    
    m.newline(block='gen')
    m.target('.PHONY', phony_targets, block='gen')

def main():
    generate_table_source_references()
    generate_table_builders()

    m.write(sys.argv[1])
    print('[meta-build]: built "' + sys.argv[1] + '" to build tables.')

if __name__ == '__main__':
    main()
