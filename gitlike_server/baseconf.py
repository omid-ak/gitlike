"""
-*- coding: utf-8 -*-
v1.0.2
GiLike Project
Copyright (C) 2020 GitLike, omid akhgary. All Rights Reserved.
Licence: GPL3
Email: omid7798@gmail.com
"""
__author__ = 'omid <omid7798@gmail.com>'

# Basic configuration of Server Side part of GitLike Project.

from enum import Enum
import distro
import socket
import os
import grp
import subprocess


"""define multiple distribution and Operating Systems"""


class Os_Type(Enum):
    LINUX       = "Linux"
    FREE_BSD    = "FreeBSD"
    UNSUPPORTED     = "Unsupported"


class Linux_Distro_Type(Enum):
    REDHAT  = ['Fedora', 'CentOS', 'CentOS Linux']
    DEBIAN  = ['Ubuntu', 'Debian', 'Debian GNU/Linux']
    UNSUPPORTED = "Unsupported"


class Shell:
    def __init__(self, sh_name):
        self.sh_name                = sh_name
        self.shell_existence_status = None
        self.shell_existence()

    def shell_existence(self):
        if os.path.exists(self.sh_name) or self.sh_name in open("/etc/shells", "r").read().splitlines():
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

    def get_group_members(self):
        return grp.getgrnam(self.grp_name).gr_mem

    def create_group(self, os_type):
        if self.grp_existence_status is False:
            if os_type is Os_Type.LINUX:
                os.system(f"groupadd {self.grp_name}")
            elif os_type is Os_Type.FREE_BSD:
                os.system(f"pw group add {self.grp_name}")


class Config:
    def __init__(self):

        self.ip                                 = None
        self.git_port                           = 22
        self.server_port                        = 7920
        self.company_name                       = None
        self.group                              = None
        self.shell                              = None
        self.os_type                            = None
        self.distro_type                        = None
        self.dependencies_installation_status   = None
        self.shell_name                         = None
        self.group_name                         = None
        self.detect_os_type()
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
        self.shell = Shell("/bin/git-shell")
        self.shell.create_shell()
        self.shell_name = self.shell.sh_name

    def init_group(self):
        # init group
        self.group = Group('git_users')
        self.group.create_group(self.os_type)
        self.group_name = self.group.grp_name

    def calc_ip(self):
        self.ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

    def dependencies_installation_check(self):
        if os.path.exists("/usr/bin/git"):
            self.dependencies_installation_status  = True
        else:
            self.dependencies_installation_status  = False

    def install_dependencies(self):
        if self.dependencies_installation_status is False:
            if self.os_type.name is Os_Type.LINUX:
                if self.distro_type.name is Linux_Distro_Type.REDHAT.name:
                    os.system('yum update -y && yum install git -y')
                if self.distro_type.name is Linux_Distro_Type.DEBIAN.name:
                    os.system('apt update -y && apt install git -y')
            elif self.os_type.name is Os_Type.FREE_BSD:
                os.system("pkg update && pkg upgrade -y && pkg install git -y")

    def firewall_check(self):
        global res
        if self.os_type.name is Os_Type.LINUX.name:
            if self.distro_type is Linux_Distro_Type.REDHAT:
                try:
                    res = subprocess.check_output("systemctl is-active firewalld", shell=True)
                except subprocess.CalledProcessError:
                    res = None
                if res is not None:
                    if res.decode().strip() == 'active':
                        try:
                            res = subprocess.check_output(f"firewall-cmd --list-ports", shell=True).decode().split()
                        except subprocess.CalledProcessError:
                            res = None
                    if res is not None:
                        if f"{self.server_port}/tcp" in res:
                            return True
            try:
                res = subprocess.check_output(f"iptables -nL | grep 'tcp dpt:{self.server_port}'", shell=True)
            except subprocess.CalledProcessError:
                res = None

        elif self.os_type.name is Os_Type.FREE_BSD.name:
            try:
                res = subprocess.check_output(f"ipfw list | grep 'allow tcp from any to any {self.server_port}'", shell=True)
            except subprocess.CalledProcessError:
                res = None

        if res is not None:
            return True
        else:
            return False

    def firewall_conf(self):
        """ Openning 7920 port if rule not exists for received connections """
        if self.firewall_check() is False:
            if self.os_type.name is Os_Type.LINUX.name:
                if self.distro_type.name is Linux_Distro_Type.REDHAT.name:
                    try:
                        res = subprocess.check_output("systemctl is-active firewalld", shell=True)
                    except subprocess.CalledProcessError:
                        res = None
                    if res is not None:
                        if res.decode().strip() == 'active':
                            os.system(f"firewall-cmd --zone=public --add-port={self.server_port}/tcp")
                os.system(f"iptables -I INPUT -p tcp -m tcp --dport {self.server_port} -j ACCEPT")
            elif self.os_type.name is Os_Type.FREE_BSD.name:
                os.system(f"ipfw -q add allow tcp from any to any {self.server_port}")

    def detect_os_type(self):
        os_type = os.uname().sysname
        if os_type == Os_Type.LINUX.value:
            self.os_type = Os_Type.LINUX
            distro_type = distro.name()
            if distro_type:
                if distro_type in Linux_Distro_Type.DEBIAN.value:
                    self.distro_type = Linux_Distro_Type.DEBIAN
                elif distro_type in Linux_Distro_Type.REDHAT.value:
                    self.distro_type = Linux_Distro_Type.REDHAT
                else:
                    self.distro_type = Linux_Distro_Type.UNSUPPORTED
            else:
                self.distro_type = Linux_Distro_Type.UNSUPPORTED

        elif os_type == Os_Type.FREE_BSD.value:
            self.os_type = Os_Type.FREE_BSD
        else:
            self.os_type = Os_Type.UNSUPPORTED
