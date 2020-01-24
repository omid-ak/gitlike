#! ./venv/bin/python3

_author = 'omid'

import pam
import os
import pwd
import crypt
import grp
import platform
import getpass
import time
from enum import Enum
from sys import argv
import shutil

class Server_info(Enum):
    IP = argv[1]
    PORT = 22

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

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
        os.system(f"useradd -p {encPass} {self.username}")

    def delete_user(self):
        os.system(f"userdel {self.username}")
        shutil.rmtree(f"/home/{self.username}")
        shutil.rmtree(f"/repositories/{self.username}/")

    def change_shell(self, shell):
        os.system(f"usermod --shell {shell} {self.username}")
    
    def add_to_group(self, group_name):
        os.system(f"usermod -aG {group_name} {self.username}")

class Group:

    def __init__(self, grp_name):
        self.grp_name = grp_name
    def group_existence(self):
        if self.grp_name in [entry.gr_name for entry in grp.getgrall()]:
            return True
        else:
            return False
    def create_group(self):
        os.system(f"groupadd {self.grp_name}")

class Shell:
    def __init__(self, sh_name):
        self.sh_name = sh_name
    def shell_existence(self):
        if os.path.exists(self.sh_name):
            return True
        else:
            return False
    def create_shell(self):
        os.system(f"echo {self.sh_name} >> /etc/shells")

class Repository(User, Group):
    def __init__(self, repo_name, username, password, group_name):
        self.repo_name = repo_name
        User.__init__(self, username, password)
        Group.__init__(self, group_name)
        self.repo_link = None
        self.repo_path = None
        self.get_repo_link_and_path()

    def get_repo_link_and_path(self):
        self.repo_path = f"/repositories/{self.username}/{self.repo_name}.git"
        self.repo_link = f"ssh://{self.username}@{Server_info.IP.value}:{Server_info.PORT.value}{self.repo_path}"


    def repo_existence(self):
        if os.path.exists(self.repo_path):
            return True
        else:
            return False

    def create_repository(self):
        os.makedirs(self.repo_path)
        os.chdir(self.repo_path)
        os.system("git init --bare --share=group")
        os.system(f"chgrp -R {self.grp_name} .")
        os.system(f"ln -s {self.repo_path} /home/{self.username}")
        os.chown(f"/home/{self.username}/", pwd.getpwnam(self.username).pw_uid, grp.getgrnam(self.grp_name).gr_gid)

    def delete_repository(self):
        os.unlink(f"/home/{self.username}/{self.repo_name}.git")
        shutil.rmtree(self.repo_path)


def detect_distro_type():
    redhat = ['fedora', 'centos', 'suse']
    debian = ['ubuntu', 'debian']
    dist = platform.linux_distribution()[0]
    distro_type = None
    redhat_flag = False
    debian_flag = False
    for d in redhat:
        if d in dist.lower():
            redhat_flag = True
            break
        else:
            pass
    for d in debian:
        if d in dist.lower():
            debian_flag = True
            break
        else:
            pass
    if redhat_flag:
        distro_type = 'redhat'
    elif debian_flag:
        distro_type = 'debian'
    return distro_type


def main():
    os.system("clear")
    # check for root
    if os.geteuid() != 0:
        print('Permission denied run only with root user')
        exit(0)

    # install git
    if os.path.exists("/usr/bin/git") == False:
        if detect_distro_type() == 'redhat':
            os.system('yum update -y && yum install git -y')
        elif detect_distro_type() == 'debian':
            os.system('apt update -y && apt install git -y')
    # create shell
    shell = Shell("/bin/git-shell")
    if not shell.shell_existence():
        shell.create_shell()
    # create group
    group = Group('git_users')
    if not group.group_existence():
        group.create_group()
    def menue():
        os.system("clear")
        print('choose :\n1)create user\n2)delete user\n3)create repo\n4)delete repo\n5)get repo link\n6)exit\n')

    while True:
        menue()
        choice = input()
        if choice == '1': # create user
            username = input("username: ")
            password = getpass.getpass(f"[git] password for {username}: ")
            user = User(username, password)
            if user.user_existence():
                print("user exists")
                time.sleep(3)
                continue
            else:
                user.create_user()
                user.change_shell(shell.sh_name)
                user.add_to_group(group.grp_name)
                print(f"user {user.username} created successfully.")
                time.sleep(3)
                continue
        elif choice == '2': # delete user
            username = input("username: ")
            password = getpass.getpass(f"[git] password for {username}: ")
            user = User(username, password)
            if user.user_existence():
                if user.user_authentication():
                    dl_ch = input(f"Are you sure you want to delete user {user.username} ? (y/n): ")
                    if dl_ch == 'y':
                        user.delete_user()
                        print(f"user {user.username} deleted")
                        break
                        exit(0)
                    else:
                        print("Aborted!")
                        break
                        exit(0)
                else:
                    print("Authentication Failed !")
                    break
                    exit(0)
            else:
                print("user not found")
                time.sleep(3)
                continue
        elif choice == '3': # create repo
            username = input("username: ")
            password = getpass.getpass(f"[git] password for {username}: ")
            repo_name = input("Enter repository name: ")
            repository = Repository(repo_name, username, password, group.grp_name)
            if repository.user_existence():
                if repository.user_authentication():
                    if repository.repo_existence():
                        print(f"repository already exists\nclone or remote with ssh: {repository.repo_link}")
                        break
                        exit(0)
                    else:
                        repository.create_repository()
                        print(f"repository created successfully.\nclone or remote with ssh: {repository.repo_link}")
                        break
                        exit(0)
                else:
                    print("Authentication Failed !")
                    break
                    exit(0)
        elif choice == '4': # delete repo
            username = input("username: ")
            password = getpass.getpass(f"[git] password for {username}: ")
            repo_name = input("Enter repository name: ")
            repository = Repository(repo_name, username, password, group.grp_name)
            if repository.user_existence():
                if repository.user_authentication():
                    if repository.repo_existence():
                        dl_ch = input(f"Are you sure you want to delete repository {repository.repo_name} ? (y/n): ")
                        if dl_ch == 'y':
                            repository.delete_repository()
                            print(f"repository {repository.repo_name} deleted")
                            break
                            exit(0)
                        else:
                            print("Aborted!")
                            break
                            exit(0)
                    else:
                        print(f"repository {repository.repo_name} not found for user {repository.username}!")
                        break
                        exit(0)
                else:
                    print("Authentication Failed !")
                    break
                    exit(0)
        elif choice == '5': # get repo link
            username = input("username: ")
            password = getpass.getpass(f"[git] password for {username}: ")
            repo_name = input("Enter repository name: ")
            repository = Repository(repo_name, username, password, group.grp_name)
            if repository.user_existence():
                if repository.user_authentication():
                    if repository.repo_existence():
                        print(f"clone or remote with ssh: {repository.repo_link}")
                        break
                        exit(0)
                    else:
                        print(f"repository {repository.repo_name} not found for user {repository.username}!")
                        break
                        exit(0)
                else:
                    print("Authentication Failed !")
                    break
                    exit(0)
        elif choice == '6': # exit
            print("Bye!")
            break
            exit(0)
        else:
            print('Unknown command !')


if __name__ == '__main__':
    main()
