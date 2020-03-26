
_author = "omid"

from baseconf import Config
from users import User
from repositories import Repository

import grp
import socket
from threading import Thread
import pickle
import os

config = Config()

def handler(main_socket, client, addr):
    c_ip = addr[0]
    c_port = addr[1]

    while True:
        try:
            client.sendall(pickle.dumps({"company_name": config.company_name}))
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
        if user.username_validation() is True:
            if user.user_existence() and os.path.exists(f"/repositories/{user.username}"):
                response_message = "user exists"
                CONTINUE = False
            else:
                user.create_user()
                user.change_shell(config.shell_name)
                user.add_to_group(config.group_name)
                response_message = f"user {user.username} created successfully."
        else:
            response_message = f"username {user.username} is invalid only (words, digits, ., - , _) is valid"
            CONTINUE = False

    return {'msg': response_message,'continue': CONTINUE}


"""kwargs: {choice:#, username:#, password:#, member:#/emp, repo_name:#/emp}"""

def choose(**kwargs):

   
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
        repository = Repository(repo_name, username, password, config.group_name)

        if repository.repo_name_validation() is True:
            if repository.repo_existence() is True:
                response_message = f"repository already exists\nclone or remote with ssh: {repository.repo_link}"
            else:
                repository.create_repository()
                response_message = f"repository created successfully.\nclone or remote with ssh: {repository.repo_link}"
        else:
            response_message = f"username {repository.repo_name} is invalid only (words, digits, - , _) is valid"

    # delete repo
    elif choice == '3':
        username = kwargs['username']
        password = kwargs['password']
        repo_name = kwargs['repo_name']
        repository = Repository(repo_name, username, password, config.group_name)

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
        repository = Repository(repo_name, username, password, config.group_name)
        if repository.repo_existence():
            response_message = f"clone or remote with ssh: {repository.repo_link}"
        else:
            response_message = f"repository {repository.repo_name} not found for user {repository.username}!"

    # add member to repo
    elif choice == '5':
        username = kwargs['username']
        password = kwargs['password']
        repo_name = kwargs['repo_name']
        repository = Repository(repo_name, username, password, config.group_name)
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
        repository = Repository(repo_name, username, password, config.group_name)
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
            repos = ",".join(user.all_repos)
            response_message = repos
        else:
            response_message = f"there are no repositories for user {user.username}."
    # show contributors
    elif choice == '8':
        username = kwargs['username']
        password = kwargs['password']
        repo_name = kwargs['repo_name']
        repository = Repository(repo_name, username, password, config.group_name)
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
    # Base config
    print('initializing...')
    config.company_name = input("Entenr Your Company Name: ")
    print('checking for dependencies...')

    # install dependencies
    if config.dependencies_installation_status is False:
        answer = input("You need to install some dependencies so you want to continues? [y/n]: ")
        if answer is "y" or answer is "Y":
            config.install_dependencies()
        elif answer is "n" or answer is "N":
            print("Operation aborted")
        else:
            print("Unknown!")
            exit(0)
    else:
        print("Dependencies Resolved.")
    
    # connection
    
    main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = '0.0.0.0'
    port = 7920
    main_socket.bind((ip, port))

    main_socket.listen()
    print("Wating For connection...")

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
