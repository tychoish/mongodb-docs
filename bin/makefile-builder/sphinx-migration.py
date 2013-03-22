#!/usr/bin/python

import sys
from makefile_builder import MakefileBuilder
from builder_data import sphinx_migrations as migrations
from mongodb_docs_meta import PUBLISHED_BRANCHES, get_branch

m = MakefileBuilder()

def build_all_sphinx_migrations(migrations):
    m.comment('Establish basic dependencies.', block='deps')

    branches = PUBLISHED_BRANCHES
    branches.append(str(get_branch()))

    for branch in branches:
        target_loc = '$(output)/' + branch
        m.target(target_loc + '/singlehtml/contents.html', target_loc + '/singlehtml', block='deps')
        m.target(target_loc + '/epub/mongodb-manual.epub', 'epub', block='deps')
        m.target('$(public-output)/' + branch + '/MongoDB-Manual.epub', '$(public-output)/' + branch + '/MongoDB-Manual-' + branch + '.epub', block='deps')

    m.comment('targets to establish to ensure clean builds and sphinx content.', block='header')
    m.newline(block='header')

    block='build'

    for branch in branches:
        for migration in migrations:
            if False is True:
                dep = migration[1] + '-' + branch
            else:
                dep = migration[1]
            target = str('$(output)/' + branch + '/' + migration[1])

            generate_build_rule(target, dep, block)


def generate_build_rule(target, dep, block):
    m.target(target=target,
             dependency=dep,
             block=block)
    m.job('touch $@', block=block)
    m.msg('[build]: touched $@ to ensure proper migration', block=block)
    m.newline(block=block)

def main():
    build_all_sphinx_migrations(migrations)

    m.write(sys.argv[1])

    print('[meta-build]: built "' + sys.argv[1] + '" to specify sphinx migrations.')

if __name__ == '__main__':
    main()
