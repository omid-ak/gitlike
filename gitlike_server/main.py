"""
-*- coding: utf-8 -*-
v1.0.2
GitLike Project
Copyright (C) 2020 GitLike, Omid Akhgary. All Rights Reserved.
Licence: GPL3
omid7798@gmail.com
"""

"""
Main Module To Run
* Be Aware that This Module Should Be Run As Root Privileges.!
"""

__author__ = "omid <omid7798@gmail.com>"

from .baseconf import Config
from .users import User, User_Types
from .repositories import Repository
from ._logging import Logger, Log_Type
from enum import Enum
import pickle
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
                            "3": "show all users",
                            "4": "show user repos",
                            "5": "exit"
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
then check if user is git_user:
received data format:
{
    choice:#, --> 1/../9 --> User Post Enrollment Stages
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

elif user is admin:

{
    choice:#, --> 1/../5 --> Admin Post Enrollment Stages
    username:#, --> admin user
    git_user:#,
    repo_name:#/emp,
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
                            if enrollment_return["user_type"] == User_Types.GIT_USER.value:

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
                            elif enrollment_return["user_type"] == User_Types.ADMIN.value:

                                logger.main_logger(
                                    log_type=Log_Type.RECEIVED_DATA,
                                    ip=c_ip,
                                    port=c_port,
                                    data=rec_data_2,
                                    stage=Stages.ADMIN_POST_ENROLLMENT.value
                                )
                                # exit in stage enrollment
                                if rec_data_2['choice'] == '5':

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
                                    username=rec_data_2.get('username'),
                                    git_username=rec_data_2.get('git_username', None),
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
    user = User(username=kwargs['username'], password=kwargs['password'], shell_name=config.shell_name, group_name=config.group_name, os_type=config.os_type)
    if kwargs['choice'] == '1':
        git_users = config.group.get_group_members()
        if user.user_existence():
            if user.user_authentication() :
                if user.is_admin():
                    response_message    = f"Welcome {user.username}."
                    color               = Text_Color.SUCCESS.value
                    CONTINUE            = True
                    user_type           = User_Types.ADMIN.value
                elif user.username in git_users:
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
            'choice'    :# --> 1/.../5
            'username'  :#
            'repo_name' :#/emp
            'git_user'  :#/emp
            }
    """
    global response_message, color, choice

    choice = kwargs.get('choice')

    # show all repos
    if choice == '1':
        all_repos = Repository.show_all_repos()
        if all_repos:
            response_message    = all_repos
            color               = Text_Color.SUCCESS.value

        else:
            response_message    = "no repository found"
            color               = Text_Color.WARNING.value

    # show repo memebers
    elif choice == '2':
        repository = Repository(repo_name=kwargs.get('repo_name'), os_type=config.os_type)
        if repository.repo_existence():
            if repository.contributors:
                response_message = repository.contributors
                color            = Text_Color.SUCCESS.value

            else:
                response_message    = f"there are no contributors for repository {repository.repo_name}."
                color               = Text_Color.WARNING.value

        else:
            response_message        = f"repository {repository.repo_name} not found"
            color                   = Text_Color.ERROR.value

    # show all users
    elif choice == '3':
        git_users = config.group.get_group_members()
        if git_users:
            response_message    = git_users
            color               = Text_Color.SUCCESS.value

        else:
            response_message    = "no user found"
            color               = Text_Color.WARNING.value

    # show user repos
    elif choice == '4':
        git_user = User(username=kwargs.get('git_username'), os_type=config.os_type)
        git_user_repos = git_user.all_repos

        if git_user_repos:
            response_message    = git_user_repos
            color               = Text_Color.SUCCESS.value
        else:
            response_message    = f"there are no repositories for user {git_user.username}."
            color                = Text_Color.WARNING.value           

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
        user = User(username=username, password=password, os_type=config.os_type)
        user.show_repos()

        if user.all_repos:
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
        repository = Repository(repo_name=repo_name, username=username, password=password, os_type=config.os_type)

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
        repository = Repository(repo_name=repo_name, username=username, password=password, os_type=config.os_type)

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
        repository = Repository(repo_name=repo_name, username=username, password=password, os_type=config.os_type)
        if repository.user_repo_existence():
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
        repository = Repository(repo_name=repo_name, username=username, password=password, os_type=config.os_type)
        repository.show_contributors()

        if repository.user_repo_existence():
            if repository.contributors:
                response_message = repository.contributors
                color            = Text_Color.SUCCESS.value

            else:
                response_message    = f"there are no contributors for repository {repository.repo_name}."
                color               = Text_Color.WARNING.value

        else:
            response_message    = f"repository {repository.repo_name} not found for user {repository.username}"
            color               = Text_Color.ERROR.value

    # add member to repo
    elif choice == '6':
        username = kwargs['username']
        password = kwargs['password']
        repo_name = kwargs['repo_name']
        repository = Repository(repo_name=repo_name, username=username, password=password, os_type=config.os_type)
        member = kwargs['member']
        if repository.user_repo_existence():
            member_user = User(username=member, os_type=config.os_type)
            if member_user.user_existence():
                if repository.is_repo_owner():
                    if repository.is_contributor(member) is False:
                        repository.add_contributor(member)
                        response_message    = f"{member} added to repository {repository.repo_name}"
                        color               = Text_Color.SUCCESS.value
                    else:
                        response_message    = f"{member} already subscribed in repository {repository.repo_name}"
                        color               = Text_Color.WARNING.value
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
        repository = Repository(repo_name=repo_name, username=username, password=password, os_type=config.os_type)
        if repository.user_repo_existence():
            member_user = User(username=member, os_type=config.os_type)
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
        user = User(username=username, password=password, os_type=config.os_type)
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

