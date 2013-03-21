#!/usr/bin/python

import sys
from makefile_builder import MakefileBuilder
from builder_data import install_guides, subscription_build
from mongodb_docs_meta import get_build_envs, PUBLISHED_BRANCHES, get_branch

m = MakefileBuilder()

def env_to_branch(env):
    return env.split('/')[1]

def is_current_branch(env):
    if env_to_branch(env) == get_branch():
        return True
    else:
        return False

def is_current_build(env):
    if env.split('/')[2] == 'branch-source-current':
        return True
    else:
        return False

def build_all_install_guides(install_guides):
    m.comment('to render the install guides properly, we have to bake in the version number.', block='header')
    m.newline(block='header')

    for build in install_guides:
        if build[1] is None:
            for env in get_build_envs():
                target = env + 'includes/install-curl-release-' + build[0] + '.rst '
                if is_current_build(env) and not is_current_branch(env):
                    pass
                else:
                    makefile_core(target, build[0], env)
        else:
            for env in get_build_envs():
                target = env + build[0]
                dependency = ''
                for dep in build[1]: 
                    dependency += env + dep + ' '
        
                if is_current_build(env) and not is_current_branch(env):
                    pass
                else:
                    makefile_restat(target, dependency, env)
            
    for build in subscription_build:
        for env in get_build_envs():
            target = env + 'includes/install-curl-release-ent-' + build[1] + '.rst'

            if is_current_build(env) and not is_current_branch(env):
                pass
            else:
                makefile_enterprise(target, build[0], build[1], env)

    m.comment('integration target for the installation guides:', block='meta')
    m.newline(block='meta')

    phony = '$(installation-guides) installation-guides installation-guides-current'

    m.target(target='installation-guides-current',
             dependency='$(installation-guides-current)',
             block='meta')
    m.target(target='installation-sources-current',
             dependency='$(installation-sources-current)',
             block='meta')
    m.job('git update-index --assume-unchanged $(installation-sources)', ignore=True, block='meta')
    m.msg('[build]: cleansing git index of installation sources.', block='meta')
    phony += ' installation-sources-current'


    for branch in PUBLISHED_BRANCHES:
        m.target(target='installation-sources-' + branch,
                 dependency='$(installation-sources-' + branch + ')', block='meta')
        phony += ' $(installation-sources-' + branch + ')'

        m.job('git update-index --assume-unchanged $(installation-sources)', ignore=True, block='meta')
        m.msg('[build]: cleansing git index of installation sources.', block='meta')

        phony += ' installation-guides-' + branch

        m.target(target='installation-guides-' + branch,
                 dependency='$(installation-guides' + branch + ')',
                 block='meta')

    m.newline(block='meta')
    m.target(target='.PHONY',
             dependency=phony,
             block='meta')

    m.newline(block='meta')

def makefile_core(target, builder, env):
    # this is one of the included source files.
    branch = env_to_branch(env)
    
    if is_current_build(env):
        m.append_var(variable='installation-sources-current',
                     value=target,
                     block='source')
    else:
        m.append_var(variable='installation-sources-' + branch,
                     value=target,
                     block='source')
    m.target(target=target, dependency=None, block='source')
    m.job('$(PYTHONBIN) bin/update_release.py %s %s %s' % (builder, 'core', target), block='source')
    m.msg('[build]: \(re\)generated $@.', block='source')
    m.newline(block='source')

def makefile_enterprise(target, builder, release, env):
    # instructions for the enterprise build

    if is_current_build(env):
        m.append_var(variable='installation-sources-current',
                     value=target,
                     block='ent')
    else:
        m.append_var(variable='installation-sources-' + env_to_branch(env),
                     value=target,
                     block='source')

    m.target(target=target, dependency=env, block='ent')
    m.job('$(PYTHONBIN) bin/update_release.py %s %s $@' % (builder, release), block='ent')
    m.msg('[build]: \(re\)generated $@.', block='ent')
    m.newline(block='ent')

def makefile_restat(target, dependency, env):
    # this is an installation guide.
    branch = env_to_branch(env)

    dependency += ' ' + env
    if is_current_build(env) and is_current_branch(env):
        m.append_var(variable='installation-guides-current', value=target, block='guide')

    m.append_var(variable='installation-guides-' + branch, value=target, block='guide')
    m.target(target=target, dependency=dependency, block='guide')

    m.job('touch $@', block='guide')

    m.msg('[build]: touched $@ to ensure a clean build.', block='guide')
    m.newline(block='guide')

def main():
    build_all_install_guides(install_guides)

    m.write(sys.argv[1])
    print('[meta-build]: built "' + sys.argv[1] + '" to specify install guides.')

if __name__ == '__main__':
    main()
