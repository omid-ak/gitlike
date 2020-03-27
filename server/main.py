"""
v1.0

This Is Main part of git server of `GITLIKE` Project Written By  Omid Akhgary
If You Want To Contact With Me:
Email: omid7798@gmail.com
License: GPL3

"""

_author = "omid"

from baseconf import Config
from users import User
from repositories import Repository
from _logging import Logger, Log_Type
from enum import Enum
import socket
from threading import Thread
import pickle
import os
import logging

# Using from configs
config = Config()
# Using from logger
logger = Logger()

# Determine Client Text Colors.
class Text_Color(Enum):

    SUCCESS = 'green'
    WARNING = 'yellow'
    ERROR   = 'red'


# Determine Logging variant Stages.
class Stages(Enum):
    PRE_ENROLLMENT  = "pre_enrollment"
    ENROLLMENT      = "enrollment"
    POST_ENROLLMENT = "post_enrollment"

# Enrollment Menu Variant Stages
Enrollment_Stages = {
                        "1": "signin",
                        "2": "signup"
                    }

# Main Menu(Post Enrollment Menu) Variant Stages.
Post_Enrollment_stages = {
                            "1": "delete account",
                            "2": "create repo",
                            "3": "delete repo",
                            "4": "get repo link",
                            "5": "add contributor to repo",
                            "6": "remove contributor from repo",
                            "7": "show my repos",
                            "8": "show repo contributors",
                         }

# Main Thread Handler.
def handler(main_socket, client, addr):
    c_ip = addr[0]
    c_port = addr[1]

    logger.main_logger(log_type=Log_Type.CONNECTION_RECEIVED, ip=c_ip, port=c_port, stage=Stages.PRE_ENROLLMENT.value)

    while True:
        try:
            send_com_name = {"company_name": f"{config.company_name} GitLike"}

            logger.main_logger(
                                log_type=Log_Type.SENT_DATA,
                                ip=c_ip,
                                port=c_port,
                                data=send_com_name,
                                stage=Stages.PRE_ENROLLMENT.value
                                )

            client.sendall(pickle.dumps(send_com_name))

            enroll_recv_data = client.recv(8192)

            try:
                rec_data_1 = pickle.loads(enroll_recv_data)

                logger.main_logger(
                                    log_type=Log_Type.RECEIVED_DATA,
                                    ip=c_ip,
                                    port=c_port,
                                    data=rec_data_1,
                                    stage=Stages.ENROLLMENT.value
                                    )

                enrollment_return = enrollment(
                                                choice=rec_data_1.get('choice'),
                                                username=rec_data_1.get('username'),
                                                password=rec_data_1.get('password'),
                                               )
                client.sendall(pickle.dumps(enrollment_return))

                logger.main_logger(
                                    log_type=Log_Type.RUNTIME_ACTIONS,
                                    ip=c_ip,
                                    port=c_port,
                                    stage=Stages.ENROLLMENT.value,
                                    action=Enrollment_Stages.get(rec_data_1.get('choice')),
                                    username=rec_data_1.get('username'),
                                    log_msg=enrollment_return.get("msg")
                                   )

                logger.main_logger(
                                    log_type=Log_Type.SENT_DATA,
                                    ip=c_ip, port=c_port,
                                    data=enrollment_return,
                                    stage=Stages.ENROLLMENT.value
                                    )

                if enrollment_return['continue'] is True:

                    while True:
                        choose_return = None
                        response = None
                        menu_rec_data = client.recv(8192)
                        try:
                            rec_data_2 = pickle.loads(menu_rec_data)

                            logger.main_logger(
                                                log_type=Log_Type.RECEIVED_DATA,
                                                ip=c_ip,
                                                port=c_port,
                                                data=rec_data_2,
                                                stage=Stages.POST_ENROLLMENT.value
                                                )

                            if rec_data_2['choice'] == '9':

                                logger.main_logger(
                                    log_type=Log_Type.RUNTIME_ACTIONS,
                                    ip=c_ip,
                                    port=c_port,
                                    stage=Stages.POST_ENROLLMENT.value,
                                    action=Post_Enrollment_stages.get(rec_data_2.get('choice')),
                                    username=rec_data_2.get('username'),
                                    log_msg="App Terminated"
                                )

                                client.close()

                            else:
                                choose_return = choose(
                                                        choice=rec_data_2.get('choice'),
                                                        username=rec_data_2.get('username'),
                                                        password=rec_data_2.get('password'),
                                                        repo_name=rec_data_2.get('repo_name', None),
                                                        member=rec_data_2.get('member', None),
                                                        delete_response=rec_data_2.get('delete_response', None)
                                                       )

                                logger.main_logger(
                                                    log_type=Log_Type.RUNTIME_ACTIONS,
                                                    ip=c_ip,
                                                    port=c_port,
                                                    stage=Stages.POST_ENROLLMENT.value,
                                                    action=Post_Enrollment_stages.get(rec_data_2.get('choice')),
                                                    username=rec_data_2.get('username'),
                                                    log_msg=choose_return.get('msg')
                                                    )

                                response = {
                                            'msg': choose_return['msg'],
                                            'color': choose_return['color']
                                            }

                                logger.main_logger(
                                                    log_type=Log_Type.SENT_DATA,
                                                    ip=c_ip, port=c_port,
                                                    data=response,
                                                    stage=Stages.POST_ENROLLMENT.value
                                                    )

                                client.sendall(pickle.dumps(response))

                        except:

                            logger.main_logger(
                                                log_type=Log_Type.RECEIVED_DATA,
                                                ip=c_ip,
                                                port=c_port,
                                                stage=Stages.POST_ENROLLMENT.value,
                                                data=menu_rec_data,
                                                level=logging.WARNING,
                                                log_msg=f"Unknown Input Data in stage {Stages.POST_ENROLLMENT.value}!"
                                               )
                            client.close()
                else:

                    logger.main_logger(
                                        log_type=Log_Type.RUNTIME_ACTIONS,
                                        ip=c_ip,
                                        port=c_port,
                                        level=logging.WARNING,
                                        stage=Stages.ENROLLMENT.value,
                                        action=Enrollment_Stages.get(rec_data_1.get('choice')),
                                        log_msg=enrollment_return.get('msg')
                                       )
                    client.close()

            except:

                logger.main_logger(
                                    log_type=Log_Type.RECEIVED_DATA,
                                    ip=c_ip,
                                    port=c_port,
                                    stage=Stages.ENROLLMENT.value,
                                    data=enroll_recv_data,
                                    level=logging.WARNING,
                                    log_msg=f"Unknown Input Data on stage {Stages.ENROLLMENT.value}!"
                                    )

                client.close()

        except (OSError, EOFError):
            logger.main_logger(
                                log_type=Log_Type.RUNTIME_ACTIONS,
                                ip=c_ip,
                                port=c_port,
                                stage=Stages.PRE_ENROLLMENT.value,
                                level=logging.WARNING,
                                log_msg="Unknown! May Be internal oserror of eoferror"
                               )
            pass

def enrollment(**kwargs):

    response_message    = None
    color               = None
    CONTINUE            = False
    log_level           = None

    user = User(kwargs['username'], kwargs['password'])
    if kwargs['choice'] == '1':
        if user.user_existence() and os.path.exists(f"/repositories/{user.username}"):
            if user.user_authentication():
                response_message    = f"Welcome {user.username}."
                color               = Text_Color.SUCCESS.value
                CONTINUE            = True
            else:
                response_message    = "Authentication Failed !"
                color               = Text_Color.ERROR.value
                CONTINUE            = False
        else:
            response_message    = f"user {user.username} not found"
            color               = Text_Color.ERROR.value
            CONTINUE            = False
        
    if kwargs['choice'] == '2':
        if user.username_validation() is True:
            if user.user_existence() and os.path.exists(f"/repositories/{user.username}"):
                response_message    = "user exists"
                color               = Text_Color.ERROR.value
                CONTINUE            = False
            else:
                user.create_user()
                user.change_shell(config.shell_name)
                user.add_to_group(config.group_name)
                response_message    = f"user {user.username} created successfully."
                color               = Text_Color.SUCCESS.value
        else:
            response_message    = f"username {user.username} is invalid only (words, digits, ., - , _) is valid"
            color               = Text_Color.ERROR.value
            CONTINUE            = False

    return {'msg': response_message,'continue': CONTINUE, 'color': color}


"""kwargs: {choice:#, username:#, password:#, member:#/emp, repo_name:#/emp}"""

def choose(**kwargs):

   
    response_message    = None
    color               = None
    log_leve            = None
    choice              = kwargs['choice']

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
                    response_message    = f"user {user.username} deleted successfully"
                    color               = Text_Color.SUCCESS.value
                else:
                    response_message    = "Aborted!"
                    color               = Text_Color.ERROR.value
            else:
                response_message    = "Authentication Failed !"
                color               = Text_Color.ERROR.value
        else:
            response_message    = f"user {user.username} not found"
            color               = Text_Color.ERROR.value

    # create repo
    elif choice == '2':
        username = kwargs['username']
        password = kwargs['password']
        repo_name = kwargs['repo_name']
        repository = Repository(repo_name, username, password, config.group_name)

        if repository.repo_name_validation() is True:
            if repository.repo_existence() is True:
                response_message    = {
                                        "resp_msg"  : "repository already exists\nclone or remote with ssh: ",
                                        "link"      : repository.repo_link
                                       }
                color               = Text_Color.WARNING.value
            else:
                repository.create_repository()
                response_message = {
                    "resp_msg"  : "repository created successfully.\nclone or remote with ssh: ",
                    "link"      : repository.repo_link
                }
                color            = Text_Color.SUCCESS.value
        else:
            response_message = f"username {repository.repo_name} is invalid only (words, digits, - , _) is valid"
            color            = Text_Color.ERROR.value

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
                    response_message = f"repository {repository.repo_name} deleted successfully"
                    color            = Text_Color.SUCCESS.value
                else:
                    response_message = "Aborted!"
                    color            = Text_Color.ERROR.value
            else:
                response_message = f"permission denied!\nyou have not privilege to remove repository {repository.repo_name}."
                color            = Text_Color.ERROR.value
        else:
            response_message = f"repository {repository.repo_name} not found for user {repository.username}!"
            color            = Text_Color.ERROR.value
    # get repo link
    elif choice == '4':
        username = kwargs['username']
        password = kwargs['password']
        repo_name = kwargs['repo_name']
        repository = Repository(repo_name, username, password, config.group_name)
        if repository.repo_existence():
            response_message = {"resp_msg": "clone or remote with ssh: ", "link": repository.repo_link}
            color            = None
        else:
            response_message = f"repository {repository.repo_name} not found for user {repository.username}!"
            color            = Text_Color.ERROR.value
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
                        response_message    = f"{member} removed from repository {repository.repo_name}"
                        color               = Text_Color.SUCCESS.value
                    else:
                        response_message    = f"permission denied!\nyou have not privilege to remove member {member_user.username}."
                        color               = Text_Color.ERROR.value
                else:
                    response_message    = f"user {member} is not contributing in repository {repository.repo_name}."
                    color               = Text_Color.ERROR.value
            else:
                response_message    = f"user {member_user.username} not found"
                color               = Text_Color.ERROR.value
        else:
            response_message = f"repository {repository.repo_name} not found for user {repository.username}!"
            color            = Text_Color.ERROR.value
    # show repos
    elif choice == '7':
        username = kwargs['username']
        password = kwargs['password']
        user = User(username, password)
        user.show_repos()

        if len(user.all_repos) > 0:
            repos               = ",".join(user.all_repos)
            response_message    = repos
            color               = Text_Color.SUCCESS.value
        else:
            response_message    = f"there are no repositories for user {user.username}."
            color                = Text_Color.WARNING.value

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
                contrbs      += f"{r},"
            response_message = contrbs
            color            = Text_Color.SUCCESS.value
        else:
            response_message    = f"there are no contributors for repository {repository.repo_name}."
            color               = Text_Color.WARNING.value

    else:
        response_message    = 'Unknown command !'
        color               = Text_Color.ERROR.value

    return {"msg": response_message, "color": color, "log_leve": log_leve}


def main():
    logger.main_logger(log_type=Log_Type.START)
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
            logger.main_logger(Log_Type=Log_Type.START, log_msg="Dependencies Installed Successfully.")
        elif answer is "n" or answer is "N":
            print("Operation aborted")
            logger.main_logger(Log_Type=Log_Type.START, log_msg="Dependencies Installation Operation Aborted.")
        else:
            print("Unknown!")
            exit(0)
    else:
        logger.main_logger(log_type=Log_Type.START, log_msg="Dependencies Resolved.")
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
