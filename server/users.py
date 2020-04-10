"""
v1.0.2
GiLike Project
Copyleft (C) 2020 GitLike. All Rights Reserved.
Licence: GPL3
Email: omid7798@gmail.com
"""

"""
Users controlling of Server Side part of GitLike Project.
"""

__author__ = 'omid <omid7798@gmail.com>'

import pam
import os
import pwd
import re
import grp
from shutil import rmtree
from enum import Enum
from baseconf import Os_Type

class User_Types(Enum):
    ADMIN       = "admin"
    GIT_USER    = "git_user"

class User():
    def __init__(self, **kwargs):
        self.username   = kwargs.get("username", None)
        self.os_type    = kwargs.get("os_type", None)
        self.shell_name = kwargs.get("shell_name", None)
        self.group_name = kwargs.get("group_name", None)
        if isinstance(kwargs.get("password", None), list):
            self.passwords      = kwargs.get("password", None)
            if self.password_match():
                self.password       = self.passwords[0]
            else:
                self.password       = None
        else:
            self.password       = kwargs.get("password", None)
        self.passwords  = kwargs.get("passwords", None)
        self.home_user_path = os.path.join(f"/home",f"{self.username}")
        self.all_repos  = list()
        self.show_repos()
    
    def username_validation(self):
        if re.match("^[a-zA-Z0-9_.-]+$", self.username):
            return True
        else:
            return False

    def user_existence(self):
        if self.username in [entry.pw_name for entry in pwd.getpwall()]:
            return True
        else:
            return False

    def password_match(self):
        if self.passwords:
            if len(self.passwords) == 2 and self.passwords[0] == self.passwords[1]:
                return True
            else:
                return False

    def user_authentication(self):
        if pam.authenticate(self.username, self.password):
            return True
        else:
            return False

    def create_user(self):
        if self.os_type is Os_Type.LINUX:
            try:
                os.system(f"useradd -G {self.group_name} --shell={self.shell_name} -p $(openssl passwd -1 {self.password}) {self.username}")
            except:
                print(f"user {self.username} exists.")

        # TODO: Add FreeBSD create user

        if os.path.exists(self.home_user_path) is False:
            os.mkdir(self.home_user_path)

    def delete_user(self):
        if self.os_type is Os_Type.LINUX:
            try:
                os.system(f"userdel -fr {self.username}")
            except:
                print(f"user {self.username} not found")
        
        # TODO: Add FreeBSD delete user part

        if os.path.exists(self.home_user_path):
            try:
                rmtree(self.home_user_path)
            except:
                print(f"an issue occure while removing {self.username}")


    def show_repos(self):
        self.all_repos.clear()
        dirs = list()
        try:
            dirs = os.listdir(self.home_user_path)

        except:
            pass

        if len(dirs) > 0:
            for d in dirs:
                if re.match("^[a-zA-Z0-9_-]+\.git$", d):
                    self.all_repos.append(d)
        else:
            self.all_repos = []


    def is_admin(self):
        global root_access_group
        try:
            root_access_group = grp.getgrnam("wheel")
        except :
            try:
                root_access_group  = grp.getgrnam("sudo")
            except:
                root_access_group = None
        
        if self.username in root_access_group.gr_mem:
            return True
        else:
            return False