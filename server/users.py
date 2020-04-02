"""
v1.0
GiLike Project
Copyleft (C) 2020 GitLike. All Rights Reserved.
Licence: GPL3
Email: omid7798@gmail.com
"""

"""
Users controlling of Server Side part of GitLike Project.
"""

_author = "omid"

import pam
import os
import pwd
import crypt
import re

class User():
    def __init__(self, username, password):

        self.username   = username
        if isinstance(password, list):
            self.passwords  = password
            self.password   = self.passwords[0]
        else:
            self.password   = password
            self.passwords  = []
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
        encPass = crypt.crypt(self.password, "22")
        try:
            os.system(f"useradd -p {encPass} {self.username}")
        except:
            print(f"user {self.username} exists.")

        if os.path.exists(f"/repositories/{self.username}") is False:
            os.mkdir(f"/repositories/{self.username}")
        if os.path.exists(f"/repositories/{self.username}/contributors/") is False:
            os.mkdir(f"/repositories/{self.username}/contributors/")
        if os.path.exists(f"/home/{self.username}") is False:
            os.mkdir(f"/home/{self.username}")

    def delete_user(self):

        try:
            os.system(f"userdel -r {self.username}")
        except:
            print(f"user {self.username} not found")

        try:
            os.system(f"rm -rf /repositories/{self.username}")
        except:
            print(f"directory for user {self.username} not found")
        try:
            os.system(f"rm -rf /home/{self.username}")
        except:
            print(f"an issue occure while removing {self.username}")

    def change_shell(self, shell):
        os.system(f"usermod --shell {shell} {self.username}")

    def add_to_group(self, group_name):
        os.system(f"usermod -aG {group_name} {self.username}")

    def show_repos(self):
        self.all_repos.clear()
        dirs = list()
        try:
            dirs = os.listdir(f"/repositories/{self.username}/")
            dirs.remove('contributors')

        except:
            pass

        if len(dirs) > 0:
            for d in dirs:
                self.all_repos.append(d)
        else:
            self.all_repos = []

