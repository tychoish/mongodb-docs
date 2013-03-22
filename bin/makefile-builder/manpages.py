#!/usr/bin/python

from makefile_builder import MakefileBuilder
from mongodb_docs_meta import get_build_envs, PUBLISHED_BRANCHES, get_branch
from releases import env_to_branch, is_current_build
import sys

m = MakefileBuilder()

def generate_man_builder_0(base, branch, includes_dir):
    target = includes_dir + 'manpage-options-auth-mongo.rst'
    m.target(target=target,
             dependency=includes_dir + 'manpage-options-auth.rst',
             block=base)
    m.job('cp $< $@', block=base)
    m.job('sed $(SED_ARGS_FILE) -e "s/fact-authentication-source-tool/fact-authentication-source-mongo/" $@', block=base)
    m.job('git update-index --assume-unchanged', ignore=True, block=base)
    m.msg('[generator]: generated the "$@" file.', block=base)
    m.append_var('manpage-auto', target, block=base )

    if is_current_build(base): 
        m.append_var('manpage-auto-current', target, block=base)
    else:
        m.append_var('manpage-auto-' + branch, target, block=base)
    
    m.newline(block=base)

   
def generate_man_builder_1(base, branch, includes_dir):
    target = includes_dir + 'manpage-options-ssl-settings.rst'

    m.append_var('manpage-auto', target, block=base )
    if is_current_build(base): 
        m.append_var('manpage-auto-current', target, block=base)
    else:
        m.append_var('manpage-auto-' + branch, target, block=base)

    m.target(target=target,
             dependency=includes_dir + 'manpage-options-ssl.rst',
             block=base)
    m.job('cp $< $@', block=base)
    m.job('sed $(SED_ARGS_FILE) -e "s/\.\. option:: \-\-/.. setting:: /" -e "s/setting:: (.*) .*/setting:: \1/" -e "s/:option:\\`\-\-/:setting:\\`/g" $@', block=base)
    m.msg('[generator]: generated the "$@" file.', block=base)


    m.newline(block=base)

def main():
    for base in get_build_envs():
        branch = env_to_branch(base) 
        if branch == 'v2.2': 
            pass
        else: 
            includes_dir = base + 'includes/'
            generate_man_builder_0(base, branch, includes_dir)
            generate_man_builder_1(base, branch, includes_dir)
            m.newline(block=base)
        
    m.write(sys.argv[1])
    print('[meta-build]: built "' + sys.argv[1] + '" to autogenerate manpages.')

if __name__ == '__main__':
    main()
