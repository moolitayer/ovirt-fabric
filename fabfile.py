#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
# Refer to the README and COPYING files for full details of the license
#
import fabric
import functools
import os
import sys

(
    GIT,
    FAB,
) = range(2)


@fabric.api.parallel
def deploy_vdsm(src='${HOME}/dev/vdsm', ):
    _deploy(
        {
            'src': src,
            'dest': '~/.ovirt_fabric/vdsm',
            'put_method': GIT,
            'rpms': (
                ('noarch/', 'vdsm-bootstrap'),
                ('noarch/', 'vdsm-cli'),
                ('noarch/', 'vdsm-debug-plugin'),
                ('noarch/', 'vdsm-gluster'),
                ('noarch/', 'vdsm-hook-ethtool-options'),
                ('noarch/', 'vdsm-hook-faqemu'),
                ('noarch/', 'vdsm-hook-ipv6'),
                ('noarch/', 'vdsm-hook-macspoof'),
                ('noarch/', 'vdsm-hook-openstacknet'),
                ('noarch/', 'vdsm-hook-qemucmdline'),
                ('noarch/', 'vdsm-infra'),
                ('noarch/', 'vdsm-jsonrpc'),
                ('noarch/', 'vdsm-python'),
                ('noarch/', 'vdsm-python'),
                ('noarch/', 'vdsm-reg'),
                ('noarch/', 'vdsm-tests'),
                ('noarch/', 'vdsm-xmlrpc'),
                ('noarch/', 'vdsm-xmlrpc'),
                ('noarch/', 'vdsm-yajsonrpc'),
                ('x86_64/', 'vdsm'),
                ('x86_64/', 'vdsm-debuginfo'),
            ),
            'local_cmd': 'make check NOSE_EXCLUDE=\'.*\'',
            'remote_cmd': (
                "./autogen.sh --system",
                "make rpm NOSE_EXCLUDE='protocoldetectorTests'"
            ),
            'post': (
                "sudo vdsm-tool configure --force",
                "sudo service vdsmd start",
                "sudo tail -f /var/log/vdsm/vdsm.log",
            )

        }
    )


@fabric.api.parallel
def deploy_engine(src='${HOME}/dev/ovirt-engine'):
    _deploy(
        {
            'src': src,
            'dest': '~/.ovirt_fabric/ovirt-engine',
            'put_method': GIT,
            'rpms': (
                ('noarch', 'ovirt-engine'),
                ('noarch', 'ovirt-engine-backend'),
                ('noarch', 'ovirt-engine-dbscripts'),
                ('noarch', 'ovirt-engine-extensions-api-impl'),
                ('noarch', 'ovirt-engine-extensions-api-impl-javadoc'),
                ('noarch', 'ovirt-engine-lib'),
                ('noarch', 'ovirt-engine-restapi'),
                ('noarch', 'ovirt-engine-setup'),
                ('noarch', 'ovirt-engine-setup-base'),
                ('noarch', 'ovirt-engine-setup-plugin-ovirt-engine'),
                ('noarch', 'ovirt-engine-setup-plugin-ovirt-engine-common'),
                ('noarch', 'ovirt-engine-setup-plugin-websocket-proxy'),
                ('noarch', 'ovirt-engine-tools'),
                ('noarch', 'ovirt-engine-userportal'),
                ('noarch', 'ovirt-engine-webadmin-portal'),
                ('noarch', 'ovirt-engine-websocket-proxy'),
            ),
            'remote_cmd': (
                "make dist",
                "rpmbuild -D'ovirt_build_minimal 1' -tb *.tar.gz "
            ),

            }
    )


@fabric.api.parallel
def deploy_extension(src='${HOME}/dev/ovirt-engine-extension-aaa-jdbc'):
    _deploy(
        {
            'src': src,
            'dest': '~/.ovirt_fabric/ovirt-engine-extension',
            'put_method': GIT,
            'dependencies': (
                "apache-commons-codec",
                "ovirt-engine-extensions-api",
                "junit",
                "slf4j",
            ),

            'rpms': (
                ('noarch', os.path.basename(src)),
            ),
            'remote_cmd': (
                "make dist",
                "rpmbuild  -tb *.tar.gz "
            ),
            'post': (
                "sudo service ovirt-engine stop",
                "sudo su - -c \"echo ''  > /var/log/ovirt-engine/engine.log\"",
                "sudo su - -c \"echo ''  > /var/log/ovirt-engine/server.log\"",
                "sudo service ovirt-engine start",
                "sudo tail -f /var/log/ovirt-engine/engine.log",
            )
        }
    )

@fabric.api.parallel
def vdsm_developers_fe20():
    # useradd, passwd, ssh-
    # copy-id
    _deploy(
        {
            'dependencies': (
                "http://resources.ovirt.org/releases/ovirt-release/ovirt-release-master.rpm",
            ),
        }
    )
    _deploy(
        {
            'dependencies': (
                "make", "autoconf", "automake", "pyflakes", "logrotate",
                "gcc", "python-pep8", "libvirt-python", "python-devel",
                "python-nose", "rpm-build", "sanlock-python", "genisoimage",
                "python-ordereddict", "python-pthreading", "libselinux-python",
                "python-ethtool", "m2crypto", "python-dmidecode", "python-netaddr",
                "python-inotify", "python-argparse", "git", "python-cpopen",
                "bridge-utils", "libguestfs-tools-c", "pyparted", "openssl",
                "libnl3", "libtool", "gettext-devel", "python-ioprocess",
                "policycoreutils-python", "python-simplejson", "vim-enhanced"
            ),
            }
    )


@fabric.api.parallel
def engine_developers_fe20():
    fabric.api.run("sudo yum install -y http://resources.ovirt.org/releases/ovirt-release/ovirt-release-master.rpm || true")
    fabric.api.run("""
sudo yum install -y git java-devel maven openssl postgresql-server rpm-build \
m2crypto python-psycopg2 python-cheetah python-daemon libxml2-python \
unzip patternfly1 jboss-as
""")


#
# Experimental!
#
@fabric.api.parallel
def update_vdsm():

    fab_host_string = fabric.state.env.host_string
    local_git = "~/dev/vdsm"
    remote_git = "~/dev/vdsm"
    remote_repo = "/var/www/html/my-vdsm-changes"
    local_git = fabric.api.local("readlink -f %s" % local_git, capture=True)

    fabric.api.run("mkdir -p %s" % remote_git)
    remote_git = fabric.api.run("readlink -f %s" % remote_git)

    # TODO: build to a differrent lib, and delete only that.
    # Delete stuff before cd..
    fabric.api.run("rm -rf %s ~/rpmbuild/RPMS && mkdir %s" % (
        remote_git,
        remote_git)
    )

    fabric.api.run("sudo rm -rf %s ~/rpmbuild/RPMS && sudo mkdir %s" % (
        remote_repo,
        remote_repo)
    )

    with fabric.context_managers.cd(remote_git), fabric.api.local_cd(local_git):

        fabric.api.run("git init")

        fabric.api.run("git config --add 'receive.denyCurrentBranch' 'ignore' ")

        branch = fabric.api.local("git branch | grep '^*' | cut -d ' ' -f2",
                           capture=True)
        if "no branch" in branch:

            print("ERROR: no branch.")
            sys.exit()

        fabric.api.local("make check NOSE_EXCLUDE"
                  "='.*'")  # if pep or pyflakes fail don't continue.

        fabric.api.local("git push --mirror %s:%s" % (fab_host_string, remote_git))

        fabric.api.run("git checkout %s" % (branch,))

        fabric.api.run("./autogen.sh --system && make rpm NOSE_EXCLUDE='protocoldetectorTests'  ")

        fabric.api.run("sudo cp ~/rpmbuild/RPMS/noarch/* ~/rpmbuild/RPMS/x86_64/* %s" % remote_repo )

        fabric.api.run("sudo createrepo %s" % remote_repo )

        fabric.api.run("sudo yum clean all ")


def _get_dir(path, location, recreate=False):
    if recreate:
        location("rm -rf %s" % path)
        location("mkdir -p %s" % path)

    return location("readlink -f %s" % path)


def _deploy(descriptor):
    remote_rpms = _get_dir(
        "${HOME}/rpmbuild/RPMS",
        fabric.api.run,
        recreate=True
    )

    local_git = _get_dir(
        descriptor['src'],
        functools.partial(fabric.api.local, capture=True)
    )
    remote_git = _get_dir(
        descriptor['dest'],
        fabric.api.run, recreate=True
    )

    if 'dependencies' in descriptor:
        _fab_execute(
            fabric.api.local,
            "echo sudo yum install -y %s" % ' '.join(descriptor['dependencies']),
            local_git,
            remote_git
        )

    if 'local_cmd' in descriptor:
        _fab_execute(
            fabric.api.local,
            descriptor['local_cmd'],
            local_git,
            remote_git
        )

    if 'put_method' in descriptor:
        _put_code(
            local_git,
            remote_git,
            descriptor['put_method']
        )

    if 'remote_cmd' in descriptor:
        _fab_execute(
            fabric.api.run,
            descriptor['remote_cmd'],
            local_git,
            remote_git
        )

    if 'rpms' in descriptor:
        _rpms(descriptor['rpms'], remote_rpms, install=False)
        _rpms(descriptor['rpms'], remote_rpms)

    if 'post' in descriptor:
        _fab_execute(
            fabric.api.run,
            descriptor['post'],
        )


def _fab_execute(func, commands, local_git="~", remote_git="~"):
    with fabric.context_managers.lcd(local_git), fabric.context_managers.cd(remote_git):
        if type(commands) == str:
            commands = (commands,)
        for cmd in commands:
            func(cmd)


def _put_code(local_git, remote_git, method=FAB):
    def local_changes(local_git):
        with fabric.context_managers.settings(
            fabric.context_managers.hide('warnings', 'running', 'stdout', 'stderr'),
            warn_only=True
        ), fabric.context_managers.lcd(
                local_git
        ):
            cmd = fabric.api.local("git diff-index --name-only --exit-code HEAD", capture=True)
            return [cmd.return_code != 0, cmd.stdout]

    if method == FAB:
        with fabric.context_managers.lcd(local_git), fabric.context_managers.cd(remote_git):
            fabric.api.put(local_git, remote_git)

    elif method == GIT:

        with fabric.context_managers.lcd(local_git), fabric.context_managers.cd(remote_git):
            branch = fabric.api.local("git branch | grep '^*' | cut -d ' ' -f2", capture=True)

            fabric.api.run("git init")
            fabric.api.run("git config --add 'receive.denyCurrentBranch' 'ignore' ")
            if "no branch" in branch:
                raise ValueError("ERROR: no branch. \n %s" % local_git)
            has_changes, changes = local_changes(local_git)
            # print("has_changes: %s, changes: %s" % (has_changes, changes))
            if has_changes:
                raise ValueError("ERROR: local changes detected in %s:\n %s" % (local_git, changes))

            fabric.api.local("git push --mirror %s:%s" % (
                fabric.state.env.host_string,
                remote_git)
            )

            fabric.api.run("git checkout %s " % branch)

    else:
        raise ValueError("illegal method.")


def _rpms(rpms, path, install=True):
    arch, name = zip(*rpms)
    with fabric.context_managers.cd(path):
        if install:
            exper = ''
            for rpm in name:
                if exper != '':
                    exper += '|'
                exper += '%s-[0-9]+\.[0-9]+' % rpm
            names = [
                s.strip() for s in
                fabric.api.run("find . -type f| grep -E '%s'" % exper).splitlines()
            ]
            command = 'install'
        else:
            names = name
            command = 'remove'
        fabric.api.run(
            'sudo yum %s -y %s' % (
                command,
                ' '.join(names)
            )
        )


