#!/usr/bin/python

import sys
from makefile_builder import MakefileBuilder
from builder_data import sphinx as sphinx_targets
from mongodb_docs_meta import PUBLISHED_BRANCHES, get_branch

# to add a symlink build process, add a tuple to the ``links`` in the builder definitions file.

m = MakefileBuilder()

def make_all_sphinx(sphinx):
    m.section_break('sphinx related variables', block='header')
    m.var(variable='SPHINXBUILD',
          value='sphinx-build',
          block='vars')

    m.comment('defines a nitpick mode for sphinx\'s more verbose reporting', block='vars')
    m.raw(['ifdef NITPICK'], block='vars')
    m.append_var(variable='SPHINXOPTS',
                 value='-n -w $(branch-output)/build.$(shell date +%Y%m%d%H%M).log',
                 block='vars')
    m.raw(['endif'], block='vars')

    m.comment('variables related to paper sizing for the latex output', block='vars')
    m.var(variable='PAPER', value='letter', block='vars')
    m.var(variable='PAPEROPT_a4', value='-D latex_paper_size=a4', block='vars')
    m.var(variable='PAPEROPT_letter', value='-D latex_paper_size=letter', block='vars')

    m.var(variable='epub-filter',
          value="sed $(SED_ARGS_REGEX) -e '/^WARNING: unknown mimetype.*ignoring$$/d' -e '/^WARNING: search index.*incomplete.$$/d'",
          block='epub-vars')

    m.section_break('sphinx targets', block='sphinx')
    m.comment('each sphinx target invokes and controls the sphinx build.', block='sphinx')
    m.newline(block='sphinx')

    branches = PUBLISHED_BRANCHES
    branches.append(None)

    for builder in sphinx:
        for branch in branches:
            sphinx_builder(builder, branch)

    m.target('.PHONY', '$(sphinx-targets) $(branch-output)/source.tar $(branch-source) $(branch-output)/conf-tmp.py $(branch-output)/bin', block='footer')

def build_kickoff(target, env, block):
    m.job('mkdir -p $(branch-output)/' + target, block=block)
    m.msg('[' + target + ']: created $(branch-output)/' + target, block)
    m.msg('[' + target + ']: starting ' + target + ' build', block)
    m.msg('[' + target + ']: build \(' + env + '\) started at `date`.', block)

def get_sphinx_options(branch_out, target, source_info):
    middle = '/ $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) '
    return '-q -d ' + branch_out + '/doctrees-' + target + ' -c ' + branch_out + middle + source_info

def sphinx_builder(target, branch):
    b = 'production'

    if branch is None:
        branch_output = '$(branch-output)'
        output_loc = '$(branch-source-current)'
        sphinx_options = get_sphinx_options(branch_output, target, output_loc)
        tag = '-current'
        sphinx_dependency = 'generated-content-current sphinx-prerequisites-current'
    else:
        branch_output = '$(output)/' + branch
        output_loc = branch_output + '/branch-source'
        sphinx_options = get_sphinx_options(branch_output, target, output_loc)
        target += '-' + branch
        tag = '-prod'
        sphinx_dependency = 'generated-content-' + branch + 'sphinx-prerequisites-' + branch

    m.append_var('sphinx-targets', target)
    m.target(target, sphinx_dependency, block=b)
    target_build = target.split('-')[0]

    if target.startswith('epub'):
        build_kickoff(target_build, output_loc, block=b)
        m.job('{ $(SPHINXBUILD) -b epub ' + sphinx_options + ' ' + branch_output + '/epub 2>&1 1>&3 | $(epub-filter) 1>&2; } 3>&1', block=b)
    else:
        build_kickoff(target_build, output_loc, block=b)
        m.job('$(SPHINXBUILD) -b ' + target_build + ' ' + sphinx_options + ' ' + branch_output + '/' + target_build, block=b)

    if target.startswith('linkcheck'):
        m.msg('[' + target_build + ']: Link check complete at `date`. See "' + branch_output + '/linkcheck/output.txt".', block=b)
    else:
        m.msg('[' + target_build + ']: build finished at `date`.', block=b)

    m.newline(block=b)

def main():
    make_all_sphinx(sphinx_targets)

    m.write(sys.argv[1])

    print('[meta-build]: built "' + sys.argv[1] + '" to specify sphinx builders.')

if __name__ == '__main__':
    main()
