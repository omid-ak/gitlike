"""
v1.0

Users controlling of Server Side part of GitLike Project.

"""

_author = "omid"

import pam
import os
import pwd
import crypt
import shutil
import re

class User:
    def __init__(self, username, password):
        self.username   = username
        self.password   = password
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
            pass
        if os.path.exists(f"/repositories/{self.username}") is False:
            os.mkdir(f"/repositories/{self.username}")
        if os.path.exists(f"/repositories/{self.username}/contributors/") is False:
            os.mkdir(f"/repositories/{self.username}/contributors/")

    def delete_user(self):

        try:
            os.system(f"userdel {self.username}")
        except:
            print(f"user {self.username} not found")
            pass
        try:
            shutil.rmtree(f"/home/{self.username}")
        except:
            print(f"home user directory for user {self.username} not found")
        try:
            shutil.rmtree(f"/repositories/{self.username}/")
        except:
            print(f"directory for user {self.username} not found")

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

