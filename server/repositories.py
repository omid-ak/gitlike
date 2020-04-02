"""
v1.0
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
        self.repo_path = None
        self.home_user_repo_path = None
        self.repo_contributors_db = None
        self.get_repo_link_and_path_and_contributors_db()
        self.contributors = dict()
        self.show_contributors()

    def get_repo_link_and_path_and_contributors_db(self):
        self.repo_contributors_db = f"/repositories/{self.username}/contributors/{self.repo_name}.json"
        self.repo_path = f"/repositories/{self.username}/{self.repo_name}.git"
        self.home_user_repo_path = f"/home/{self.username}/{self.repo_name}.git"
        self.repo_link = f"ssh://{self.username}@{self.ip}:{self.git_port}{self.repo_path}"

    def repo_existence(self):
        if os.path.exists(self.repo_path) is True:
            return True
        else:
            return False

    def repo_name_validation(self):
        if re.match("^[a-zA-Z0-9_-]+$", self.repo_name):
            return True
        else:
            return False

    def create_repository(self):
        os.mkdir(f"{self.repo_path}")
        os.mkdir(f"{self.home_user_repo_path}")
        self.contributors = {"owner": self.username, "others": []}
        pickle.dump(self.contributors, open(self.repo_contributors_db, "wb"))
        os.chdir(self.repo_path)
        os.system("git init --bare --share=group")
        os.system(f"chgrp -R {self.group_name} .")
        os.system(f"ln -s {self.repo_path} {self.home_user_repo_path}")
        os.system(f"chown -R {self.username}:{self.group_name} {self.home_user_repo_path}")
        self.show_repos()

    def delete_repository(self):
        self.show_contributors()
        try:
            os.unlink(f"{self.home_user_repo_path}")
        except:
            print("an issue occured when unlinking {self.home_user_repo_path}")

        if len(self.contributors.get("others")) > 0:
            for p in self.contributors.get("others"):
                try:
                    os.unlink(f"/repositories/{p}/{self.repo_name}.git")
                except :
                    print(f"an issue occured when unlinking {self.repo_name} for {p}")
                    pass
                try:
                    os.unlink(f"/repositories/{p}/contributors/{self.repo_name}.json")
                except :
                    print(f"an issue occured when unlinking /repositories/{p}/contributors/{self.repo_name}.json for {p}")
                    pass
        try:
            os.system(f"rm -rf {self.repo_contributors_db}")
        except :
            print(f"contributors file for repo {self.repo_name} not found for user {self.username}")
            pass
        try:
            os.system(f"rm -rf {self.repo_path}")
        except :
            print(f"an issue occured when removing {self.repo_path}")
            pass

    def add_contributor(self, member):
        self.show_contributors()
        self.contributors["others"].append(member)
        pickle.dump(self.contributors, open(self.repo_contributors_db, "wb"))

        try:
            os.system(f"ln -s {self.repo_path} /repositories/{member}/{self.repo_name}.git")
            os.system(f"ln -s {self.repo_contributors_db} /repositories/{member}/contributors/{self.repo_name}.json")

            os.makedirs(self.home_user_repo_path)
            os.system(f"ln -s {self.repo_path} /home/{member}/{self.repo_name}.git")
            os.system(f"chown -R {member}:{self.group_name} /home/{member}/{self.repo_name}.git")
        except:
            print(f"an issue occured in {member} files for repository {self.repo_name}")
            pass

    def remove_contributor(self, member):
        self.show_contributors()
        self.contributors["others"].remove(member)
        pickle.dump(self.contributors, open(self.repo_contributors_db, "wb"))
        try:
            os.unlink(f"/repositories/{member}/{self.repo_name}.git")
        except:
            print(f"repo {self.repo_name} not found for user {member}")
            pass
        try:
            os.unlink(f"/repositories/{member}/contributors/{self.repo_name}.json")
        except:
            print(f"contributors file for repo {self.repo_name} not found for user {member}")
            pass

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
            tmp_contributors = pickle.load(open(self.repo_contributors_db, "rb"))
            for contributors in tmp_contributors.get("others"):
                tmp_user = User(contributors, '')
                if tmp_user.user_existence():
                    self.contributors['others'].append(contributors)
        else:
            pass