"""
v1.0.1
GiLike Project
Copyleft (C) 2020 GitLike. All Rights Reserved.
Licence: GPL3
Email: omid7798@gmail.com
"""

# Repository management of Server Side part of GitLike Project.

__author__ = "omid <omid7798@gmail.com>"

from users import User
from baseconf import Config, Group
import os
import pwd
import grp
import re
import pickle

class Repository(User, Group, Config):
    def __init__(self, repo_name, username, password, group_name):
        self.repo_name = repo_name
        User.__init__(self, username, password)
        Group.__init__(self, group_name)
        Config.__init__(self)
        self.repo_link = None
        self.repo_main_path = None
        self.repo_bare_files_path = None
        self.home_user_path = None
        self.repo_contributors_db = None
        self.get_repo_link_and_path_and_contributors_db()
        self.contributors = dict()
        self.show_contributors()

    def get_repo_link_and_path_and_contributors_db(self):
        self.repo_main_path = f"/repositories/{self.repo_name}/"
        self.repo_contributors_db = f"{self.repo_main_path}contributors/{self.repo_name}.json"
        self.repo_bare_files_path = f"{self.repo_main_path}{self.repo_name}.git/"
        self.home_user_path = f"/home/{self.username}/"
        self.repo_link = f"ssh://{self.username}@{self.ip}:{self.git_port}{self.home_user_path}{self.repo_name}.git/"

    def repo_existence(self):
        if os.path.exists(self.repo_main_path) is True:
            return True
        else:
            return False

    def repo_name_validation(self):
        if re.match("^[a-zA-Z0-9_-]+$", self.repo_name):
            return True
        else:
            return False

    def create_repository(self):
        os.mkdir(f"{self.repo_main_path}")
        os.mkdir(f"{self.repo_bare_files_path}")
        os.mkdir(f"{self.repo_main_path}contributors/")
        
        self.contributors = {"owner": self.username, "others": []}
        pickle.dump(self.contributors, open(self.repo_contributors_db, "wb"))

        os.system(f"git init --bare --share=group {self.repo_bare_files_path}")
        os.system(f"chgrp -R {self.group_name} {self.repo_bare_files_path}")
        os.system(f"ln -s {self.repo_bare_files_path} {self.home_user_path}")
        os.system(f"chown -R {self.username}:{self.group_name} {self.home_user_path}")
        self.show_repos()

    def delete_repository(self):
        self.show_contributors()
        # remove repo for owner
        try:
            os.unlink(f"{self.home_user_path}{self.repo_name}.git")
        except:
            print(f"an issue occured while unlinking {self.home_user_repo_path}")
        #remove repo for contributors
        if len(self.contributors.get("others")) > 0:
            for p in self.contributors.get("others"):
                try:
                    os.unlink(f"/home/{p}/{self.repo_name}.git")
                except :
                    print(f"an issue occured while unlinking {self.repo_name} for {p}")
        # remove repo main files
        try:
            os.system(f"rm -rf {self.repo_main_path}")
        except :
            print(f"an issue occured while removing {self.repo_main_path}")

    def add_contributor(self, member):
        self.show_contributors()
        self.contributors["others"].append(member)
        pickle.dump(self.contributors, open(self.repo_contributors_db, "wb"))

        try:
            os.system(f"ln -s {self.repo_bare_files_path} /home/{member}/")
            os.system(f"chown -R {member}:{self.group_name} /home/{member}")

        except:
            print(f"an issue occured in {member} files for repository {self.repo_name}")

    def remove_contributor(self, member):
        self.show_contributors()
        self.contributors["others"].remove(member)
        pickle.dump(self.contributors, open(self.repo_contributors_db, "wb"))
        try:
            os.unlink(f"/home/{member}/{self.repo_name}.git")
        except:
            print(f"repo {self.repo_name} not found for user {member}")

    def is_contributor(self, member):
        self.show_contributors()
        if member in self.contributors.get("others"):
            return True
        else:
            return False

    def is_repo_owner(self):
        self.show_contributors()
        if self.username == self.contributors.get("owner"):
            return True
        else:
            return False

    def show_contributors(self):

        if os.path.exists(self.repo_contributors_db) is True:
            self.contributors = pickle.load(open(self.repo_contributors_db, "rb"))
            for contributor in self.contributors.get("others"):
                tmp_user = User(contributor, '')
                if tmp_user.user_existence() is False:
                    self.contributors['others'].remove(contributor)
    
