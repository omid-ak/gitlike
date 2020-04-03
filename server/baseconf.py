"""
v1.0
GiLike Project
Copyleft (C) 2020 omid akhgary. All Rights Reserved.
Licence: GPL3
Email: omid7798@gmail.com
"""
__author__ = 'omid <omid7798@gmail.com>'

# Basic configuration of Server Side part of GitLike Project.

from enum import Enum
import platform
import socket
import os
import grp
import subprocess

"""define multiple distribution and OS"""

class Distro_Type(Enum):
    REDHAT  = ['fedora', 'centos', 'suse']
    DEBIAN  = ['ubuntu', 'debian'] 


class Shell:
    def __init__(self, sh_name):
        self.sh_name                = sh_name
        self.shell_existence_status = None
        self.shell_existence()

    def shell_existence(self):
        if os.path.exists(self.sh_name) or self.sh_name in open("/etc/shells", "r").read().split("\n"):
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
        self.calc_ip()
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

    def calc_ip(self):
        self.ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    
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

    def firewall_check(self):
        try:
            res = subprocess.check_output(f"iptables -nL | grep 'tcp spt:{self.server_port}'", shell=True)
            if res:
                return True
            else:
                return False
        except subprocess.CalledProcessError:
            return False

    def firewall_conf(self):
        """ Openning 7920 port if rule not exists for received connections """
        if self.firewall_check() is False:
            os.system(f"iptables -A INPUT -p tcp --sport {self.server_port} -j ACCEPT")

    def detect_distro_type(self):
        distro_found = platform.linux_distribution()[0]

        for distrotypes in Distro_Type:
            for entry in distrotypes.value:
                if entry in distro_found.lower():
                    self.distro_type = distrotypes