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
        self.all_repos = list()
        self.show_repos()
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
        if os.path.exists(f"/repositories/{self.username}") == False:
            os.mkdir(f"/repositories/{self.username}")
        if os.path.exists(f"/repositories/{self.username}/contributors/") == False:
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
            pass
        try:
            shutil.rmtree(f"/repositories/{self.username}/")
        except:
            print(f"directory for user {self.username} not found")
            pass

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
        self.contributors = list()
        self.show_contributors()


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
        with open(f"/repositories/{self.username}/contributors/{self.repo_name}.txt", "a") as fw:
            fw.writelines(f"*{self.username}\n")
        os.chdir(self.repo_path)
        os.system("git init --bare --share=group")
        os.system(f"chgrp -R {self.grp_name} .")
        os.system(f"ln -s {self.repo_path} /home/{self.username}")
        os.chown(f"/home/{self.username}/", pwd.getpwnam(self.username).pw_uid, grp.getgrnam(self.grp_name).gr_gid)
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

        if os.path.exists(f"/repositories/{self.username}/contributors/{self.repo_name}.txt") == True:
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

    while True:
        try:
            enroll_recv_data = client.recv(8192)
            try:
                rec_data_1 = pickle.loads(enroll_recv_data)
                enrollment_return = enrollment(choice=rec_data_1.get('choice'),
                                               username=rec_data_1.get('username'),
                                               password=rec_data_1.get('password'),
                                               )
                client.sendall(pickle.dumps(enrollment_return))

                if enrollment_return['continue']:

                    while True:
                        choose_return = None
                        response = None
                        menu_rec_data = client.recv(8192)
                        try:
                            rec_data_2 = pickle.loads(menu_rec_data)
                            if rec_data_2['choice'] == '9':
                                client.close()
                            else:
                                choose_return = choose(choice=rec_data_2.get('choice'),
                                                       username=rec_data_2.get('username'),
                                                       password=rec_data_2.get('password'),
                                                       repo_name=rec_data_2.get('repo_name', None),
                                                       member=rec_data_2.get('member', None),
                                                       delete_response=rec_data_2.get('delete_response', None)
                                                       )
                                print(choose_return)
                                response = {
                                            'msg': choose_return
                                            }
                                client.sendall(pickle.dumps(response))
                        except:
                            client.close()
                else:
                    break
                    client.close()
            except:
                client.close()
        except (OSError, EOFError):
            pass

def enrollment(**kwargs):

    # create shell
    shell = Shell("/bin/git-shell")
    if shell.shell_existence() == False:
        shell.create_shell()

    # create group
    group = Group('git_users')
    if group.group_existence() == False:
        group.create_group()

    response_message = None
    CONTINUE = False
    user = User(kwargs['username'], kwargs['password'])
    if kwargs['choice'] == '1':
        if user.user_existence() and os.path.exists(f"/repositories/{user.username}"):
            if user.user_authentication():
                response_message = f"Welcome {user.username}."
                CONTINUE = True
            else:
                response_message = "Authentication Failed !"
                CONTINUE = False
        else:
            response_message = f"user {user.username} not found"
            CONTINUE = False
    if kwargs['choice'] == '2':
        if user.user_existence() and os.path.exists(f"/repositories/{user.username}"):
            response_message = "user exists"
            CONTINUE = False
        else:
            user.create_user()
            user.change_shell(shell.sh_name)
            user.add_to_group(group.grp_name)
            response_message = f"user {user.username} created successfully."
    return {'msg': response_message,'continue': CONTINUE}


"""kwargs: {choice:#, username:#, password:#, member:#/emp, repo_name:#/emp}"""

def choose(**kwargs):
    # create shell
    shell = Shell("/bin/git-shell")
    if shell.shell_existence() == False:
        shell.create_shell()

    # create group
    group = Group('git_users')
    if group.group_existence() == False:
        group.create_group()

    response_message = None

    choice = kwargs['choice']

    # delete account
    if choice == '1':
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
    elif choice == '2':
        username = kwargs['username']
        password = kwargs['password']
        repo_name = kwargs['repo_name']
        repository = Repository(repo_name, username, password, group.grp_name)
        if repository.repo_existence():
            response_message = f"repository already exists\nclone or remote with ssh: {repository.repo_link}"
        else:
            repository.create_repository()
            response_message = f"repository created successfully.\nclone or remote with ssh: {repository.repo_link}"



    # delete repo
    elif choice == '3':
        username = kwargs['username']
        password = kwargs['password']
        repo_name = kwargs['repo_name']
        repository = Repository(repo_name, username, password, group.grp_name)

        if repository.repo_existence():
            repository.show_contributors()
            if f"*{repository.username}" in repository.contributors:
                dl_ch = kwargs['delete_response']
                if dl_ch == 'y':
                    repository.delete_repository()
                    response_message = f"repository {repository.repo_name} deleted"

                else:
                    response_message = "Aborted!"
            else:
                response_message = f"permission denied!\nyou have not privilege to remove repository {repository.repo_name}."
        else:
            response_message = f"repository {repository.repo_name} not found for user {repository.username}!"

    # get repo link
    elif choice == '4':
        username = kwargs['username']
        password = kwargs['password']
        repo_name = kwargs['repo_name']
        repository = Repository(repo_name, username, password, group.grp_name)
        if repository.repo_existence():
            response_message = f"clone or remote with ssh: {repository.repo_link}"
        else:
            response_message = f"repository {repository.repo_name} not found for user {repository.username}!"

    # add member to repo
    elif choice == '5':
        username = kwargs['username']
        password = kwargs['password']
        repo_name = kwargs['repo_name']
        repository = Repository(repo_name, username, password, group.grp_name)
        member = kwargs['member']
        if repository.repo_existence():
            member_user = User(member, '')
            if member_user.user_existence():
                repository.add_contributor(member)
                response_message = f"{member} added to repository {repository.repo_name}"

            else:
                response_message = f"user {member_user.username} not found"
        else:
            response_message = f"repository {repository.repo_name} not found for user {repository.username}!"

    # remove member from repo
    elif choice == '6':
        username = kwargs['username']
        password = kwargs['password']
        repo_name = kwargs['repo_name']
        member = kwargs['member']
        repository = Repository(repo_name, username, password, group.grp_name)
        if repository.repo_existence():
            member_user = User(member, '')
            if member_user.user_existence():
                if repository.is_contributor(member):
                    repository.show_contributors()
                    if f"*{username}" in repository.contributors:
                        repository.remove_contributor(member)
                        response_message = f"{member} removed from repository {repository.repo_name}"
                    else:
                        response_message = f"permission denied!\nyou have not privilege to remove member {member_user.username}."
                else:
                    response_message = f"user {member} is not contributing in repository {repository.repo_name}."
            else:
                response_message = f"user {member_user.username} not found"

        else:
            response_message = f"repository {repository.repo_name} not found for user {repository.username}!"

    # show repos
    elif choice == '7':
        username = kwargs['username']
        password = kwargs['password']
        user = User(username, password)
        user.show_repos()

        if len(user.all_repos) > 0:
            repos = str()
            for r in user.all_repos:
                repos += f"{r},"
                response_message = repos
        else:
            response_message = f"there are no repositories for user {user.username}."
    # show contributors
    elif choice == '8':
        username = kwargs['username']
        password = kwargs['password']
        repo_name = kwargs['repo_name']
        repository = Repository(repo_name, username, password, group.grp_name)
        repository.show_contributors()

        if len(repository.contributors) > 0:
            contrbs = str()
            for r in repository.contributors:
                contrbs += f"{r},"
            response_message = contrbs
        else:
            response_message = f"there are no contributors for repository {repository.repo_name}."
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
    print("installation or checking Done.")
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
