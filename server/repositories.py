"""
v1.0

Repository management of Server Side part of GitLike Project.

"""

_author = "omid"

from users import User
from baseconf import Config, Group
import os
import pwd
import grp
import re
import shutil

class Repository(User, Group, Config):
    def __init__(self, repo_name, username, password, group_name):
        self.repo_name = repo_name
        User.__init__(self, username, password)
        Group.__init__(self, group_name)
        Config.__init__(self)
        self.repo_link = None
        self.repo_path = None
        self.get_repo_link_and_path()
        self.contributors = list()
        self.show_contributors()

    def get_repo_link_and_path(self):
        self.repo_path = f"/repositories/{self.username}/{self.repo_name}.git"
        self.repo_link = f"ssh://{self.username}@{self.IP}:{self.PORT}{self.repo_path}"

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
        os.makedirs(self.repo_path)
        with open(f"/repositories/{self.username}/contributors/{self.repo_name}.txt", "a") as fw:
            fw.writelines(f"*{self.username}\n")
        os.chdir(self.repo_path)
        os.system("git init --bare --share=group")
        os.system(f"chgrp -R {self.group_name} .")
        os.system(f"ln -s {self.repo_path} /home/{self.username}")
        os.chown(f"/home/{self.username}/", pwd.getpwnam(self.username).pw_uid, grp.getgrnam(self.group_name).gr_gid)
        self.show_repos()

    def delete_repository(self):
        self.show_contributors()
        try:
            os.unlink(f"/home/{self.username}/{self.repo_name}.git")
        except:
            pass
        contributors_except_owner = list(filter(lambda x: '*' not in x, self.contributors))
        if len(contributors_except_owner) > 0:
            for p in contributors_except_owner:
                try:
                    os.unlink(f"/repositories/{p}/{self.repo_name}.git")
                except :
                    print(f"repo {self.repo_name} not found for user {p}")
                    pass
                try:
                    os.unlink(f"/repositories/{p}/contributors/{self.repo_name}.txt/")
                except :
                    print(f"contributors file for repo {self.repo_name} not found for user {p}")
                    pass
        try:
            os.remove(f"/repositories/{self.username}/contributors/{self.repo_name}.txt/")
        except :
            print(f"contributors file for repo {self.repo_name} not found for user {self.username}")
            pass
        try:
            shutil.rmtree(self.repo_path)
        except :
            print(f"repo {self.repo_name} not found for user {self.username}")
            pass

    def add_contributor(self, member):
        with open(f"/repositories/{self.username}/contributors/{self.repo_name}.txt", "a") as fw:
            fw.writelines(member+'\n')
        try:
            os.system(f"ln -s {self.repo_path} /repositories/{member}/{self.repo_name}.git")
            os.system(f"ln -s /repositories/{self.username}/contributors/{self.repo_name}.txt /repositories/{member}/contributors/{self.repo_name}.txt")
        except:
            print(f"directory for user {member} not found!")
            pass
        self.show_contributors()

    def remove_contributor(self, member):
        self.show_contributors()
        tmp = self.contributors

        open(f"/repositories/{self.username}/contributors/{self.repo_name}.txt", "w").close()

        tmp.remove(member)

        for con in tmp:
            print(con)
            with open(f"/repositories/{self.username}/contributors/{self.repo_name}.txt", "a") as fw:
                fw.writelines(con+'\n')
                fw.close()
        try:
            os.unlink(f"/repositories/{member}/contributors/{self.repo_name}.txt/")
        except:
            print(f"contributors file for repo {self.repo_name} not found for user {member}")
            pass
        try:
            os.unlink(f"/repositories/{member}/{self.repo_name}.git")
        except:
            print(f"repo {self.repo_name} not found for user {member}")
            pass
        self.show_contributors()

    def is_contributor(self, member):
        self.show_contributors()
        if member in self.contributors:
            return True
        else:
            return False

    def show_contributors(self):

        if os.path.exists(f"/repositories/{self.username}/contributors/{self.repo_name}.txt") is True:
            repo_owner = None
            entries = list()

            self.contributors.clear()
            with open(f"/repositories/{self.username}/contributors/{self.repo_name}.txt", 'r') as fr:
                entries = fr.readlines()
                fr.close()
            repo_owner = list(filter(lambda x: '*' in x, entries))[0].strip('\n').strip('*')

            for lines in entries:
                user = User(lines.strip('\n').strip('*'), '')
                if user.user_existence():
                    if user.username == repo_owner:
                        self.contributors.append(f"*{user.username}")
                    else:
                        self.contributors.append(user.username)
        else:
            pass