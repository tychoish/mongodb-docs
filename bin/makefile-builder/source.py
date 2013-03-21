#!/usr/bin/python

import sys
from makefile_builder import MakefileBuilder
from mongodb_docs_meta import PUBLISHED_BRANCHES, get_branch

m = MakefileBuilder()
abs_branch = str(get_branch())

def generate_cache(branch, branch_output, branch_source, branch_source_current):
    def get_deps_list(branch_output):
        return ' setup ' + branch_output  + '/conf.py ' + branch_output + '/bin ' + branch_output + '/meta.yaml intersphinx '

    if branch == '$(current-branch)': 
        m.section_break(abs_branch + ' branch (current) sphinx prerequisites')
        m.var('generated-content-current', 'tables-current generate-manpages-current installation-guides-current')
        m.target('$(generated-content-current)', branch_source_current)
        m.newline()
        m.target('generated-content-current', '$(generated-content-current)')
        m.target(target='kickoff-current', 
                 dependency=branch_source_current + ' generated-content-current', 
                 block='depchain')
        m.target('sphinx-prerequisites-current', 'kickoff-current')
        m.newline()
    else: 
        m.section_break(branch + ' branch sphinx prerequisites')

    m.var('generated-content-' + branch, 'tables-' + branch + ' generate-manpages-' + branch + ' installation-guides-' + branch)
    m.newline()
    m.target(target='sphinx-prerequisites-' + branch, 
             dependency=get_deps_list(branch_output) + '$(output)/' + branch + '/branch-source $(generated-content-' + branch + ')', 
             block='prereq')
    m.msg('[sphinx-prep]: completed $@ buildstep.', block='prereq')

    m.target(target=branch_output + '/source.tar ' + branch_source, 
             dependency=branch_output + ' ' + get_deps_list('$(branch-output)'), 
             block='prereq')
    m.job('mkdir -p ' + branch_source, block='prereq')
    m.msg('[sphinx-prep]: created ' + branch_source, block='prereq')
    m.job('git archive --prefix=source/ -o ' + branch_output + '/source.tar ' + branch + ':source/', block='prereq')
    m.msg('[sphinx-prep]: generated source.tar from git', block='prereq')
    m.job('mkdir -p ' + branch_source, block='prereq')
    m.msg('[sphinx-prep]: created ' + branch_source, block='prereq')
    m.job('$(TARBIN) -U  -C $(branch-output) --no-overwrite-dir --keep-newer-files -xf ' + branch_output + '/source.tar', block='prereq')
    m.msg('[sphinx-prep]: UNPACKED ' + branch_output + '/source', block='prereq' )
    m.job('rsync --ignore-times --recursive --times --delete $(output)/' + branch + '/source/ '+ branch_source, block='prereq')
    m.msg('[sphinx-prep]: updated source in $(branch-source)', block='prereq')

    m.target(target=branch_source_current, 
             dependency=get_deps_list('$(branch-output)'),
             block='prereq')
    m.job('rsync --ignore-times --recursive --times --delete source/ $@', block='prereq')
    m.msg('[sphinx-prep]: YEAHHHHH created and synced $@', block='prereq')

    m.target(target=branch_output + '/conf-tmp.py', 
             block='prereq')
    m.job('git show ' + branch + ':conf.py > $@', block='prereq')
    m.msg('[sphinx-prep]: checked out ' + branch + ':conf.py for build.')

    m.target(target=branch_output + '/bin', 
             block='prereq')
    m.job('rm -f $@', ignore=True, block='prereq')
    m.job('cd $(branch-output) ; ln -s "../../bin"', block='prereq')
    m.msg('[sphinx-prep]: created $@ link')

    m.target(target=branch_output + '/conf.py',
            dependency= branch_output + '/conf-tmp.py', 
            block='prereq')
    m.job('$(PYTHONBIN) $(build-tools)/copy-if-needed.py -i $< -o $@ -b sphinx-prep', block='prereq')
    m.job('rm -f $<', ignore=True, block='prereq')
    m.msg('[sphinx-prep]: updated cached $@ build file', block='prereq')

def main():
    for branch in PUBLISHED_BRANCHES:

        if branch == get_branch():
            branch = '$(current-branch)'
            branch_output = '$(branch-output)'
            branch_source = branch_output + '/branch-source'
            branch_source_current = '$(branch-source-current)'
        else: 
            branch_output = '$(output)/' + branch 
            branch_source = branch_output + '/branch-source'
            branch_source_current = branch_source + '-current'

        generate_cache(branch, branch_output, branch_source, branch_source_current)

    m.write(sys.argv[1])
    print('[meta-build]: built "' + sys.argv[1] + '" to maintain the source cache.')

if __name__ == '__main__':
    main()
