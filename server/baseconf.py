"""
v1.0

Basic configuration of Server Side part of GitLike Project.

"""
_author = 'omid'

from enum import Enum
import platform
import socket
import os
import grp

class Distro_Type(Enum):
    REDHAT  = ['fedora', 'centos', 'suse']
    DEBIAN  = ['ubuntu', 'debian'] 


class Shell:
    def __init__(self, sh_name):
        self.sh_name                = sh_name
        self.shell_existence_status = None
        self.shell_existence()

    def shell_existence(self):
        if os.path.exists(self.sh_name):
            self.shell_existence_status = True
        else:
            self.shell_existence_status = False

    def create_shell(self):
        if self.shell_existence_status is False:
            os.system(f"echo {self.sh_name} >> /etc/shells")


class Group:

    def __init__(self, grp_name):
        self.grp_name               = grp_name
        self.grp_existence_status   = None
        self.group_existence()

    def group_existence(self):
        if self.grp_name in [entry.gr_name for entry in grp.getgrall()]:
            self.grp_existence_status = True
        else:
            self.grp_existence_status = False
    
    def create_group(self):
        if self.grp_existence_status is False:
            os.system(f"groupadd {self.grp_name}")


class Config:
    def __init__(self):

        self.ip                                 = None
        self.git_port                           = 22
        self.server_port                        = 7920
        self.company_name                       = None
        self.distro_type                        = None
        self.dependencies_installation_status   = None
        self.shell_name                         = None
        self.group_name                         = None
        self.detect_distro_type()
        self.calc_IP()
        self.init_repo_dir()
        self.init_shell()
        self.init_group()
        self.dependencies_installation_check()
        self.firewall_conf()

    def init_repo_dir(self):
        if os.path.exists("/repositories") is False:
            os.mkdir("/repositories")

    def init_shell(self):
        # init shell
        shell = Shell("/bin/git-shell")
        shell.create_shell()
        self.shell_name = shell.sh_name

    def init_group(self):
        # init group
        group = Group('git_users')
        group.create_group()
        self.group_name = group.grp_name

    def calc_IP(self):
        self.IP = socket.gethostbyname(socket.gethostname())
    
    def dependencies_installation_check(self):
        if os.path.exists("/usr/bin/git") is True:
            self.dependencies_installation_status  = True
        else:
            self.dependencies_installation_status  = False

    def install_dependencies(self):
        if self.dependencies_installation_status is False:
            if self.distro_type.name is Distro_Type.REDHAT.name:
                os.system('yum update -y && yum install git -y')
            if self.distro_type.name is Distro_Type.DEBIAN.name:
                os.system('apt update -y && apt install git -y')

    def firewall_conf(self):
        """ Openning 7920 port if rule not exists for received connections """
        if not [f"$(cat /sbin/iptables --list | grep -- {self.server_port})"]:
            os.system(f"iptables -A INPUT -p tcp --sport {self.server_port} -j ACCEPT")

    def detect_distro_type(self):
        distro_found = platform.linux_distribution()[0]

        for distrotypes in Distro_Type:
            for entry in distrotypes.value:
                if entry in distro_found.lower():
                    self.distro_type = distrotypes