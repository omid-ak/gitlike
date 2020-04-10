"""
-*- coding: utf-8 -*-
v1.0.2
GiLike Project
Copyright (C) 2020 GitLike, Omid Akhgary. All Rights Reserved.
Licence: GPL3
Email: omid7798@gmail.com
"""

# Repository management of Server Side part of GitLike Project.

__author__ = "omid <omid7798@gmail.com>"

from .users import User
from .baseconf import Config, Os_Type
from shutil import rmtree
import os
import pwd
import grp
import re
import pickle


class Repository(User, Config):
    def __init__(self, **kwargs):
        User.__init__(self, username=kwargs.get('username', None), password=kwargs.get('password', None))
        Config.__init__(self)
        self.repo_name              = kwargs.get("repo_name", None)
        self.os_type                = kwargs.get("os_type", None)
        self.repo_link              = None
        self.repo_main_path         = None
        self.repo_bare_files_path   = None
        self.repo_contributors_db   = None
        self.get_repo_link_and_path_and_contributors_db()
        self.contributors = dict()
        self.show_contributors()

    def get_repo_link_and_path_and_contributors_db(self):
        self.repo_main_path = os.path.join("/repositories", self.repo_name)
        self.repo_contributors_db = os.path.join(self.repo_main_path, "contributors", f"{self.repo_name}.json")
        self.repo_bare_files_path = os.path.join(self.repo_main_path,f"{self.repo_name}.git")
        self.repo_link = f"ssh://{self.username}@{self.ip}:{self.git_port}{os.path.join(self.home_user_path, f'{self.repo_name}.git')}"

    def repo_existence(self):
        if os.path.exists(self.repo_main_path) is True:
            return True
        else:
            return False
    def user_repo_existence(self):
        if os.path.exists(os.path.join(self.home_user_path, f"{self.repo_name}.git")):
            return True
        else:
            return False

    def repo_name_validation(self):
        if re.match("^[a-zA-Z0-9_-]+$", self.repo_name):
            return True
        else:
            return False

    def create_repository(self):
        os.mkdir(os.path.join(self.repo_main_path))
        os.mkdir(os.path.join(self.repo_bare_files_path))
        os.mkdir(os.path.join(self.repo_main_path, "contributors"))
        
        self.contributors = {"owner": self.username, "others": []}
        pickle.dump(self.contributors, open(self.repo_contributors_db, "wb"))

        if self.os_type is Os_Type.LINUX or self.os_type is Os_Type.FREE_BSD:
            os.system(f"git init --bare --share=group {self.repo_bare_files_path}")
            os.system(f"chgrp -R {self.group_name} {self.repo_bare_files_path}")
            os.system(f"ln -s {self.repo_bare_files_path} {self.home_user_path}")
            os.system(f"chown -R {self.username}:{self.group_name} {self.home_user_path}")
        self.show_repos()

    def delete_repository(self):
        self.show_contributors()
        # remove repo for owner
        try:
            os.unlink(os.path.join(self.home_user_path, f"{self.repo_name}.git"))
        except:
            print(f"an issue occured while unlinking {self.home_user_repo_path}")
        #remove repo for contributors
        if len(self.contributors.get("others")) > 0:
            for p in self.contributors.get("others"):
                try:
                    os.unlink(os.path.join("/home", p, f"{self.repo_name}.git"))
                except :
                    print(f"an issue occured while unlinking {self.repo_name} for {p}")
        # remove repo main files
        if self.os_type is Os_Type.LINUX or self.os_type is Os_Type.FREE_BSD:
            try:
                rmtree(os.path.join(self.repo_main_path))
            except :
                print(f"an issue occured while removing {self.repo_main_path}")

    def add_contributor(self, member):
        self.show_contributors()
        self.contributors["others"].append(member)
        pickle.dump(self.contributors, open(self.repo_contributors_db, "wb"))

        if self.os_type is Os_Type.LINUX or self.os_type is Os_Type.FREE_BSD:
            try:
                os.system(f"ln -s {self.repo_bare_files_path} {os.path.join('/home', member)}")
                os.system(f"chown -R {member}:{self.group_name} {os.path.join('/home', member)}")

            except:
                print(f"an issue occured in {member} files for repository {self.repo_name}")

    def remove_contributor(self, member):
        self.show_contributors()
        self.contributors["others"].remove(member)
        pickle.dump(self.contributors, open(self.repo_contributors_db, "wb"))
        try:
            os.unlink(os.path.join("/home", member, f"{self.repo_name}.git"))
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
                tmp_user = User(username=contributor)
                if tmp_user.user_existence() is False:
                    self.contributors['others'].remove(contributor)

    @staticmethod
    def show_all_repos():
        all_repos = list()
        dirs = list()
        try:
            dirs = os.listdir(f"/repositories/")

        except:
            pass

        if len(dirs) > 0:
            for d in dirs:
                all_repos.append(d)

        return all_repos