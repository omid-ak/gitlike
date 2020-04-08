"""
v1.0.1
GitLike Project
Copyright (C) 2020 GitLike. All Rights Reserved.
Licence: GPL3
omid7798@gmail.com
"""

"""
Main Module To Run
* Be Aware that This Module Should Be Run As Root Privileges.!
"""

__author__ = "omid <omid7798@gmail.com>"

from baseconf import Config, Os_Type, Linux_Distro_Type
from users import User, User_Types
from repositories import Repository
from _logging import Logger, Log_Type
from enum import Enum
import socket
from threading import Thread
import pickle
import os
import logging


# check for root
if os.geteuid() != 0:
    print('Permission denied run only with root user')
    exit(0)

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
    PRE_ENROLLMENT          = "pre_enrollment"
    ENROLLMENT              = "enrollment"
    USER_POST_ENROLLMENT    = "post_enrollment"
    ADMIN_POST_ENROLLMENT   = "admin_post_enrollment"
# Enrollment Menu Variant Stages
Enrollment_Stages = {
                        "1": "sign_in",
                        "2": "sign_up",
                        "3": "exit"
                    }

# Main Menu(Post Enrollment Menu) Variant Stages.
User_Post_Enrollment_Stages = {
                            "1": "show my repos",
                            "2": "create repo",
                            "3": "delete repo",
                            "4": "get repo link",
                            "5": "show repo contributors",
                            "6": "add contributor to repo",
                            "7": "remove contributor from repo",
                            "8": "delete account",
                            "9": "exit"
                            }

Admin_Post_Enrollment_stages = {
                            "1": "show all repos",
                            "2": "show repo contributors",
                            "3": "exit"
                            }

def serializer(**kwargs):
    return pickle.dumps(kwargs)


def deserializer(obj):
    return pickle.loads(obj)


# Main Thread Handler.
"""
stages : pre enrollment, enrollment , post enrollment
pre enrollment:
this Function control main process of Server
first of all controlling data that is valid or not if is not valid log it as unknown data else
enrollment stage:
check for sign in or sign up in this format:
received data format;

 {
    'choice'    : '1'/'2'/'3' --> Enrollment Stages
    'username'  : #
    'password'  : #
 }
sent data format:
{
    'msg'       :#
    'continues' :#Trues/False    
    'color'     :# --> message color.
    'user_type' :# --> User_Types  
}

then check for qualification if user qualified:
post enrollment stage:
received data format:
{
    choice:#, --> 1/../9 --> Post Enrollment Stages
    username:#,
    password:#,
    member:#/emp,
    repo_name:#/emp,
    delete_response:#/emp
}

sent data:

{
    "msg"       : #
    "color"     : # --> message color
}

"""
def handler(main_socket, client, addr):

    global c_ip, c_port
    c_ip    = addr[0]
    c_port  = addr[1]

    logger.main_logger(log_type=Log_Type.CONNECTION_RECEIVED, ip=c_ip, port=c_port, stage=Stages.PRE_ENROLLMENT.value)

    while True:
        # controlling Unknown data
        try:
            send_com_name = {"company_name": f"{config.company_name} GitLike"}

            client.sendall(serializer(**send_com_name))

            logger.main_logger(
                                log_type=Log_Type.SENT_DATA,
                                ip=c_ip,
                                port=c_port,
                                data=send_com_name,
                                stage=Stages.PRE_ENROLLMENT.value
                                )
            """ get sign or sign up"""
            enroll_recv_data = client.recv(4096)

            try:
                rec_data_1 = deserializer(enroll_recv_data)

                logger.main_logger(
                                    log_type=Log_Type.RECEIVED_DATA,
                                    ip=c_ip,
                                    port=c_port,
                                    data=rec_data_1,
                                    stage=Stages.ENROLLMENT.value
                                    )

                if rec_data_1["choice"] == '3':
                    logger.main_logger(
                        log_type=Log_Type.RUNTIME_ACTIONS,
                        ip=c_ip,
                        port=c_port,
                        stage=Stages.ENROLLMENT.value,
                        action=Enrollment_Stages.get(rec_data_1.get('choice')),
                        log_msg="App Terminated"
                    )

                    client.close()
                    break

                enrollment_return = enrollment(
                                                choice=rec_data_1.get('choice'),
                                                username=rec_data_1.get('username'),
                                                password=rec_data_1.get('password'),
                                            )



                client.sendall(serializer(**enrollment_return))

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
                                    ip=c_ip,
                                    port=c_port,
                                    data=enrollment_return,
                                    stage=Stages.ENROLLMENT.value
                                    )

                if enrollment_return['continue'] is True:

                    global choose_return, response

                    while True:
                        menu_rec_data = client.recv(4096)
                        # users part
                        try:
                            # get post enrollment data
                            rec_data_2 = deserializer(menu_rec_data)
                            if enrollment_return["user_type"] is User_Types.GIT_USER.value:

                                logger.main_logger(
                                    log_type=Log_Type.RECEIVED_DATA,
                                    ip=c_ip,
                                    port=c_port,
                                    data=rec_data_2,
                                    stage=Stages.USER_POST_ENROLLMENT.value
                                )
                                # exit in stage enrollment
                                if rec_data_2['choice'] == '9':

                                    logger.main_logger(
                                        log_type=Log_Type.RUNTIME_ACTIONS,
                                        ip=c_ip,
                                        port=c_port,
                                        stage=Stages.USER_POST_ENROLLMENT.value,
                                        action=User_Post_Enrollment_Stages.get(rec_data_2.get('choice')),
                                        username=rec_data_2.get('username'),
                                        log_msg="App Terminated"
                                    )

                                    client.close()
                                    break

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
                                                    stage=Stages.USER_POST_ENROLLMENT.value,
                                                    action=User_Post_Enrollment_Stages.get(rec_data_2.get('choice')),
                                                    username=rec_data_2.get('username'),
                                                    log_msg=choose_return.get('msg')
                                                    )

                                response = {
                                            'msg'   : choose_return['msg'],
                                            'color' : choose_return['color']
                                            }

                                logger.main_logger(
                                                    log_type=Log_Type.SENT_DATA,
                                                    ip=c_ip,
                                                    port=c_port,
                                                    data=response,
                                                    stage=Stages.USER_POST_ENROLLMENT.value
                                                    )

                                client.send(serializer(**response))
                                if rec_data_2['choice'] == '8':
                                    client.close()
                                    break
                            # Admin part
                            elif enrollment_return["user_type"] is User_Types.ADMIN.value:

                                logger.main_logger(
                                    log_type=Log_Type.RECEIVED_DATA,
                                    ip=c_ip,
                                    port=c_port,
                                    data=rec_data_2,
                                    stage=Stages.ADMIN_POST_ENROLLMENT.value
                                )
                                # exit in stage enrollment
                                if rec_data_2['choice'] == '3':

                                    logger.main_logger(
                                        log_type=Log_Type.RUNTIME_ACTIONS,
                                        ip=c_ip,
                                        port=c_port,
                                        stage=Stages.ADMIN_POST_ENROLLMENT.value,
                                        action=Admin_Post_Enrollment_stages.get(rec_data_2.get('choice')),
                                        username=rec_data_2.get('username'),
                                        log_msg="App Terminated"
                                    )

                                    client.close()
                                    break

                                admin_choose_return = admin_choose(
                                    choice=rec_data_2.get('choice'),
                                    repo_name=rec_data_2.get('repo_name', None),
                                )

                                logger.main_logger(
                                                    log_type=Log_Type.RUNTIME_ACTIONS,
                                                    ip=c_ip,
                                                    port=c_port,
                                                    stage=Stages.ADMIN_POST_ENROLLMENT.value,
                                                    action=Admin_Post_Enrollment_stages.get(rec_data_2.get('choice')),
                                                    username=rec_data_2.get('username'),
                                                    log_msg=admin_choose_return.get('msg')
                                                    )

                                response = {
                                            'msg'   : admin_choose_return['msg'],
                                            'color' : admin_choose_return['color']
                                            }

                                logger.main_logger(
                                                    log_type=Log_Type.SENT_DATA,
                                                    ip=c_ip,
                                                    port=c_port,
                                                    data=response,
                                                    stage=Stages.ADMIN_POST_ENROLLMENT.value
                                                    )

                                client.send(serializer(**response))

                        except Exception:
                            if enrollment_return['user_type'] is User_Types.GIT_USER.value:
                                stage = Stages.USER_POST_ENROLLMENT.value
                            elif enrollment_return['user_type'] is User_Types.ADMIN.value:
                                stage = Stages.ADMIN_POST_ENROLLMENT.value
                            logger.main_logger(
                                                log_type=Log_Type.RECEIVED_DATA,
                                                ip=c_ip,
                                                port=c_port,
                                                stage=stage,
                                                data=menu_rec_data,
                                                level=logging.WARNING,
                                                log_msg=f"Unknown Input Data in stage {stage}!"
                                            )
                            client.close()
                            break
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
                    break

            except Exception:

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
                break
        except (OSError, EOFError):
            # log Unknown data
            logger.main_logger(
                                log_type=Log_Type.RUNTIME_ACTIONS,
                                ip=c_ip,
                                port=c_port,
                                stage=Stages.PRE_ENROLLMENT.value,
                                level=logging.WARNING,
                                log_msg=f"Unknown Input Data On Stage {Stages.PRE_ENROLLMENT.value}"
                            )
            client.close()
            break
    client.close()

def enrollment(**kwargs):

    """
    {
    'choice': '1' / '2' --> sign in / up
    'username':  #
    'password':  #
    }

    """

    global response_message, color, CONTINUE, user_type

    CONTINUE            = False
    user_type           = None
    #sign in
    user = User(kwargs['username'], kwargs['password'])
    if kwargs['choice'] == '1':
        group_memebers = config.group.get_group_members()
        if user.user_existence():
            if user.user_authentication() :
                if user.is_admin():
                    response_message    = f"Welcome {user.username}."
                    color               = Text_Color.SUCCESS.value
                    CONTINUE            = True
                    user_type           = User_Types.ADMIN.value
                elif user.username in group_memebers:
                    response_message    = f"Welcome {user.username}."
                    color               = Text_Color.SUCCESS.value
                    CONTINUE            = True
                    user_type           = User_Types.GIT_USER.value
                else:
                    response_message    = f"Invalid User Access Denied!."
                    color               = Text_Color.ERROR.value
                    CONTINUE            = False

            else:
                response_message    = "Authentication Failed !"
                color               = Text_Color.ERROR.value
                CONTINUE            = False
        else:
            response_message    = f"user {user.username} not found"
            color               = Text_Color.ERROR.value
            CONTINUE            = False

    # sign up
    elif kwargs['choice'] == '2':
        if user.username_validation() is True:
            if user.password_match():
                if user.user_existence():
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
                response_message    = "Sorry, passwords do not match."
                color               = Text_Color.ERROR.value
                CONTINUE            = False
        else:
            response_message    = f"username {user.username} is invalid only (words, digits, ., - , _) is valid"
            color               = Text_Color.ERROR.value
            CONTINUE            = False

    return {'msg': response_message, 'continue': CONTINUE, 'color': color, 'user_type': user_type}


def admin_choose(**kwargs):

    """
    kwargs: {
            'choice':# --> 1/.../3
            'repo_name'
            }
    """
    global response_message, color, choice

    choice = kwargs.get('choice')

    # show all repos
    if choice == '1':
        all_repos = Repository.show_all_repos()
        if len(all_repos) > 0:
            response_message    = all_repos
            color               = Text_Color.SUCCESS.value

        else:
            response_message    = "no repository fouond"
            color               = Text_Color.WARNING.value

    # show repo memebers
    elif choice == '2':
        repository = Repository(kwargs.get('repo_name'))
        if len(repository.show_contributors()) > 0:
            response_message = repository.show_contributors()
            color            = Text_Color.SUCCESS.value

        else:
            response_message    = f"there are no contributors for repository {repository.repo_name}."
            color               = Text_Color.WARNING.value

    else:
        response_message    = 'Unknown command !'
        color               = Text_Color.ERROR.value

    return {'msg': response_message, 'color': color}


def choose(**kwargs):

    """
    kwargs: {
            choice:#, --> 1/../9
            username:#,
            password:#,
            member:#/emp,
            repo_name:#/emp,
            delete_response:#/emp
            }
    """
    global response_message, color, choice

    choice              = kwargs['choice']

    # show repos
    if choice == '1':
        username = kwargs['username']
        password = kwargs['password']
        user = User(username, password)
        user.show_repos()

        if len(user.all_repos) > 0:
            response_message    = user.all_repos
            color               = Text_Color.SUCCESS.value
        else:
            response_message    = f"there are no repositories for user {user.username}."
            color                = Text_Color.WARNING.value


    # create repo
    elif choice == '2':
        username = kwargs['username']
        password = kwargs['password']
        repo_name = kwargs['repo_name']
        repository = Repository(repo_name, username=username, password=password, group_name=config.group_name)

        if repository.repo_name_validation():
            if repository.repo_existence():
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
            response_message = {
                "resp_msg": f"username {repository.repo_name} is invalid only (words, digits, - , _) is valid"
            }
            color            = Text_Color.ERROR.value

    # delete repo
    elif choice == '3':
        username = kwargs['username']
        password = kwargs['password']
        repo_name = kwargs['repo_name']
        repository = Repository(repo_name, username=username, password=password, group_name=config.group_name)

        if repository.repo_existence():
            repository.show_contributors()
            if repository.is_repo_owner():
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
        repository = Repository(repo_name, username=username, password=password, group_name=config.group_name)
        if repository.repo_existence():
            response_message = {"resp_msg": "clone or remote with ssh: ", "link": repository.repo_link}
            color            = None
        else:
            response_message = {
                "resp_msg": f"repository {repository.repo_name} not found for user {repository.username}!"
            }
            color            = Text_Color.ERROR.value

    # show contributors
    elif choice == '5':
        username = kwargs['username']
        password = kwargs['password']
        repo_name = kwargs['repo_name']
        repository = Repository(repo_name, username=username, password=password, group_name=config.group_name)
        repository.show_contributors()

        if len(repository.contributors) > 0:

            response_message = repository.contributors
            color            = Text_Color.SUCCESS.value
        else:
            response_message    = f"there are no contributors for repository {repository.repo_name}."
            color               = Text_Color.WARNING.value


    # add member to repo
    elif choice == '6':
        username = kwargs['username']
        password = kwargs['password']
        repo_name = kwargs['repo_name']
        repository = Repository(repo_name, username=username, password=password, group_name=config.group_name)
        member = kwargs['member']
        if repository.repo_existence():
            member_user = User(member, '')
            if member_user.user_existence():
                if repository.is_repo_owner():
                    repository.add_contributor(member)
                    response_message    = f"{member} added to repository {repository.repo_name}"
                    color               = Text_Color.SUCCESS.value
                else:
                    response_message    = "Permission Denied!\nyou have not privilege to add member to this repository"
                    color               = Text_Color.ERROR.value
            else:
                response_message        = f"user {member_user.username} not found"
                color                   = Text_Color.ERROR.value
        else:
            response_message    = f"repository {repository.repo_name} not found for user {repository.username}!"
            color               = Text_Color.ERROR.value
    # remove member from repo
    elif choice == '7':
        username = kwargs['username']
        password = kwargs['password']
        repo_name = kwargs['repo_name']
        member = kwargs['member']
        repository = Repository(repo_name, username=username, password=password, group_name=config.group_name)
        if repository.repo_existence():
            member_user = User(member, '')
            if member_user.user_existence():
                if repository.is_contributor(member):
                    repository.show_contributors()
                    if repository.is_repo_owner():
                        dl_ch = kwargs['delete_response']
                        if dl_ch is "y":
                            repository.remove_contributor(member)
                            response_message    = f"{member} removed from repository {repository.repo_name}"
                            color               = Text_Color.SUCCESS.value
                        else:
                            response_message = "Aborted!"
                            color = Text_Color.ERROR.value
                    else:
                        response_message    = f"permission denied!\nyou have not privilege to remove  any member."
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


    # delete account
    elif choice == '8':

        username = kwargs['username']
        password = kwargs['password']
        user = User(username, password)
        if user.user_existence():
            if user.user_authentication():
                dl_ch = kwargs['delete_response']
                if dl_ch == 'y':
                    user.delete_user()
                    response_message = f"user {user.username} deleted successfully"
                    color = Text_Color.SUCCESS.value
                else:
                    response_message = "Aborted!"
                    color = Text_Color.ERROR.value
            else:
                response_message = "Authentication Failed !"
                color = Text_Color.ERROR.value
        else:
            response_message = f"user {user.username} not found"
            color = Text_Color.ERROR.value

    else:
        response_message    = 'Unknown command !'
        color               = Text_Color.ERROR.value

    return {"msg": response_message, "color": color}


def main():
    logger.main_logger(log_type=Log_Type.START)
    # Base config
    print('initializing...')
    if config.os_type.name is Os_Type.UNKNOWN.name:
        print("Unknown Operation System .!")
        logger.main_logger(Log_Type=Log_Type.START, log_msg="Unknown Operating System.", level=logging.ERROR)
        exit(1)
    if config.os_type.name is Os_Type.LINUX.name:
        if config.distro_type.name is Linux_Distro_Type.UNKNOWN.name:
            print("Unknown Linux Distribution.!")
            logger.main_logger(Log_Type=Log_Type.START, log_msg="Unknown Linux Distribution.", level=logging.ERROR)
            exit(1)

    print(f"{config.os_type.value} Operating System")

    config.company_name = input("Entenr Your Company Name: ")
    print('checking for dependencies...')

    # install dependencies
    if config.dependencies_installation_status is False:
        answer = input("You need to install some dependencies do you want to continues? [y/n]: ")
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
    main_socket.bind(('0.0.0.0', config.server_port))

    main_socket.listen()
    print("Waiting For connection...")

    try:
        while True:
            client, addr = main_socket.accept()
            thread = Thread(target=handler, args=(main_socket, client, addr))
            thread.setDaemon(True)
            thread.start()
    except OSError:
        print('closed')
        pass


if __name__ == '__main__':
    main()
