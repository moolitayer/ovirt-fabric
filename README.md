Streamline ovirt & vdsm developer workflows.

### Perquisites
* fabric 
~~~.bash
yum install fabric     # redhat
apt-get install fabric # debian, untested fabric version
~~~

* make sure the remote host is reachable by ssh and that it
requires no password using something like ssh-copy-id or kinit.

* sudo is required for various administrative operations
(install & remove rpms, view logs, etc.)

### Usage
Push code[1], build rpms, remove existing rpms and install
vdsm on fe20.example.com and el6.example.com,
run vdsm-tool and attach to log:
~~~.bash
fab -H fe20.example.com,el6.example.com deploy_vdsm
~~~

There is one parameter to all deployment scripts denoting the
repository location:
~~~.bash
fab -H localhost deploy_engine:src=/home/mtayer/ovirt-engine
~~~

Next two are used to install build dependencies on remote.
Currently only fe20 supported[2].
~~~.bash
fab -H fe20.example.com engine_developers_fe20
fab -H fe20.example.com vdsm_developers_fe20
~~~

### Git hook
TBD

#### TODO
* work with fab as library and not with a fabfiles. 
* do not delete rpmbuild, instead build to a different location?
* demand force for rpm removal?

[1] code is pushed using git, since vdsm uses git tags for it's
build.

[2] to install build dependencies on other systems follow
http://www.ovirt.org/Vdsm_Developers
