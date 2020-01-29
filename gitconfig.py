#! ./venv/bin/python3

_author = "omid"

import pam
import os
import pwd
import crypt
import grp
import platform
from enum import Enum
import shutil
import socket
from threading import Thread
import pickle

class Server_info(Enum):
    IP = socket.gethostbyname(socket.gethostname())
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
        if os.path.exists(f"/repositories/{self.username}") == False:
            os.mkdir(f"/repositories/{self.username}")

    def delete_user(self):
        try:
            os.system(f"userdel {self.username}")
            shutil.rmtree(f"/home/{self.username}")
            shutil.rmtree(f"/repositories/{self.username}/")
        except:
            pass
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

    def add_contributor(self, member):
        os.system(f"ln -s {self.repo_path} /repositories/{member}/{self.repo_name}.git")

    def remove_contributor(self, member, repo_name):
        os.unlink(f"/repositories/{member}/{repo_name}.git")

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



def handler(main_socket, client, addr):
    c_ip = addr[0]
    c_port = addr[1]

    try:
        while True:

            rec_data = pickle.loads(client.recv(1024))

            choose_return = choose(choice=rec_data.get('choice'),
                                   username=rec_data.get('username'),
                                   password=rec_data.get('password'),
                                   repo_name=rec_data.get('repo_name', None),
                                   member=rec_data.get('member', None),
                                   delete_response=rec_data.get('delete_response', None)
                                   )
            response = {
                        'msg': choose_return
                        }
            client.sendall(pickle.dumps(response))
            if rec_data['choice'] == '8':
                client.close()

    except (OSError, EOFError):
        pass


"""kwargs: {choice:#, username:#, password:#, member:#/emp, repo_name:#/emp}"""

def choose(**kwargs):
    response_message = None

    # create shell
    shell = Shell("/bin/git-shell")
    if shell.shell_existence() == False:
        shell.create_shell()
    # create group
    group = Group('git_users')
    if group.group_existence() == False:
        group.create_group()

    choice = kwargs['choice']
    # create user
    if choice == '1':
        username = kwargs['username']
        password = kwargs['password']
        user = User(username, password)
        if user.user_existence():
            response_message = "user exists"

        else:
            user.create_user()
            user.change_shell(shell.sh_name)
            user.add_to_group(group.grp_name)
            response_message = f"user {user.username} created successfully."

    # delete user
    elif choice == '2':
        username = kwargs['username']
        password = kwargs['password']
        user = User(username, password)
        if user.user_existence():
            if user.user_authentication():
                dl_ch = kwargs['delete_response']
                if dl_ch == 'y':
                    user.delete_user()

                    response_message = f"user {user.username} deleted"

                else:
                    response_message = "Aborted!"

            else:
                response_message = "Authentication Failed !"

        else:
            response_message = f"user {user.username} not found"

    # create repo
    elif choice == '3':
        username = kwargs['username']
        password = kwargs['password']
        repo_name = kwargs['repo_name']
        repository = Repository(repo_name, username, password, group.grp_name)
        if repository.user_existence():
            if repository.user_authentication():
                if repository.repo_existence():
                    response_message = f"repository already exists\nclone or remote with ssh: {repository.repo_link}"
                else:
                    repository.create_repository()
                    response_message = f"repository created successfully.\nclone or remote with ssh: {repository.repo_link}"

            else:
                response_message = "Authentication Failed !"

    # delete repo
    elif choice == '4':
        username = kwargs['username']
        password = kwargs['password']
        repo_name = kwargs['repo_name']
        repository = Repository(repo_name, username, password, group.grp_name)
        if repository.user_existence():
            if repository.user_authentication():
                if repository.repo_existence():
                    dl_ch = kwargs['delete_response']
                    if dl_ch == 'y':
                        repository.delete_repository()
                        response_message = f"repository {repository.repo_name} deleted"

                    else:
                        response_message = "Aborted!"

                else:
                    response_message = f"repository {repository.repo_name} not found for user {repository.username}!"

            else:
                response_message = "Authentication Failed !"

    # get repo link
    elif choice == '5':

        username = kwargs['username']
        password = kwargs['password']
        repo_name = kwargs['repo_name']
        repository = Repository(repo_name, username, password, group.grp_name)
        if repository.user_existence():
            if repository.user_authentication():
                if repository.repo_existence():
                    response_message = f"clone or remote with ssh: {repository.repo_link}"
                else:
                    response_message = f"repository {repository.repo_name} not found for user {repository.username}!"
            else:
                response_message = "Authentication Failed !"

    # add member to repo
    elif choice == '6':
        username = kwargs['username']
        password = kwargs['password']
        repo_name = kwargs['repo_name']
        repository = Repository(repo_name, username, password, group.grp_name)
        member = kwargs['member']
        if repository.user_existence():
            if repository.user_authentication():
                if repository.repo_existence():
                    member_user = User(member, '')
                    if member_user.user_existence():
                        repository.add_contributor(member)
                        response_message = f"{member} added to repository {repository.repo_name}"

                    else:
                        response_message = f"user {member_user.username} not found"
                else:
                    response_message = f"repository {repository.repo_name} not found for user {repository.username}!"
            else:
                response_message = "Authentication Failed !"

    # remove member from repo
    elif choice == '7':
        username = kwargs['username']
        password = kwargs['password']
        repo_name = kwargs['repo_name']
        member = kwargs['member']
        repository = Repository(repo_name, username, password, group.grp_name)
        if repository.user_existence():
            if repository.user_authentication():
                if repository.repo_existence():
                    member_user = User(member, '')
                    if member_user.user_existence():
                        repository.remove_contributor(member, repo_name)
                        response_message = f"{member} removed from repository {repository.repo_name}"

                    else:
                        response_message = f"user {member_user.username} not found"

                else:
                    response_message = f"repository {repository.repo_name} not found for user {repository.username}!"

            else:
                response_message = "Authentication Failed !"

    else:
        response_message = 'Unknown command !'

    print(response_message)
    return response_message

def main():
    # check for root
    if os.geteuid() != 0:
        print('Permission denied run only with root user')
        exit(0)
    print('initializing...')
    print('checking for git installation...')

    # install git
    if os.path.exists("/usr/bin/git") == False:
        if detect_distro_type() == 'redhat':
            os.system('yum update -y && yum install git -y')
        elif detect_distro_type() == 'debian':
            os.system('apt update -y && apt install git -y')

    # init dir
    if os.path.exists("/repositories") == False:
        os.mkdir("/repositories")
    main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connection
    ip = '0.0.0.0'
    port = 7920
    main_socket.bind((ip, port))

    main_socket.listen()
    try:
        while True:
            client, addr = main_socket.accept()
            print(f"connection from {addr[0]}:{addr[1]}")
            thread = Thread(target=handler, args=(main_socket, client, addr))
            thread.setDaemon(True)
            thread.start()
    except OSError:
        print('closed')
        pass


if __name__ == '__main__':
    main()
