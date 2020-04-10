"""
-*- coding: utf-8 -*-
v1.0.1
gitlike project
copyright (c) 2020 GitLike, Omid Akhgary. all rights reserved.
licence: GPL3
email: omid7798@gmail.com
"""

__author__ = "omid <7798@gmail.com>"

import sys
import os
import socket
import pickle
import getpass
from sys import argv
from time import sleep
from pyfiglet import Figlet 
from termcolor import colored
from enum import Enum

class User_Types(Enum):
    ADMIN       = "admin"
    GIT_USER    = "git_user"



def signin():
    print('sign in:\n')
    username = input("username: ")
    password = getpass.getpass(f"[git] password for {username}: ")
    return {'username': username, 'password': password}


def signup():
    print('sign up:\n')
    passwords = list()
    username = input("username: ")
    passwords.append(getpass.getpass(f"[git] password for {username}: "))
    passwords.append(getpass.getpass(f"Retype password: "))
    return {'username': username, 'password': passwords}

def admin_menu(user, company_name):
    username_colorful = colored(user, 'cyan')
    os.system("clear")
    print(greeting(company_name))
    print("Wellcome To The GitLike Admin Page.")
    print(f'choose :\t\t\t\tuser_admin:{username_colorful}\n'

            '1-show all repositories\n'
            '2-show repository memebers\n'
            '3-show all users\n'
            '4-show user repositories\n'
            '5-exit\n'
        )

def menu(user, company_name):
    username_colorful = colored(user, 'cyan')
    os.system("clear")
    print(greeting(company_name))
    print("Wellcome To The GitLike Users Page")
    print(f'choose :\t\t\t\tuser:{username_colorful}\n'
          
          '1-show my repositories\n'
          '2-create repository\n'
          '3-delete repository\n'
          '4-get repository link\n'
          '5-show repository contributors\n'
          '6-add contributor to repository\n'
          '7-remove contributor from repository\n'
          '8-delete account\n'
          '9-exit\n'
          )


def greeting(company_name):
    f = Figlet(font='standard')
    return colored(f.renderText(company_name), "green")


def serializer(**kwargs):
    return pickle.dumps(kwargs)


def deserializer(obj):
    return pickle.loads(obj)


def main():
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = argv[1]
    port = 7920
    connection.connect((ip, port))
    while True:
        global sign_response
        company_name = deserializer(connection.recv(4096))["company_name"]
        sign_response = None
        os.system("clear")
        print(greeting(company_name))
        print("Welcome:\n1)sign in\n2)sign up\n3)exit")
        s = input('choice: ')
        # sign in
        if s == '1':
            us = signin()
            connection.sendall(serializer(choice=s, username=us['username'], password=us['password']))
            print("please wait ...")
            sign_response   = deserializer(connection.recv(4096))
            CONTINUE        = sign_response['continue']
            print(colored(sign_response['msg'], sign_response['color']))
            break

        # sign up
        elif s == '2':
            us = signup()
            connection.sendall(serializer(choice=s, username=us['username'], password=us['password']))
            print("please wait ...")
            sign_response   = deserializer(connection.recv(4096))
            CONTINUE        = sign_response['continue']
            print(colored(sign_response['msg'], sign_response['color']))
            break
        # exit
        elif s == '3':

            connection.sendall(serializer(choice=s))
            CONTINUE = False
            print("Bye!")
            break
            sys.exit(0)

        else:
            print(colored('Unknown command!', 'red'))
            break
            sys.exit(0)

    if CONTINUE:

        sleep(2)
        # admin part
        if sign_response['user_type'] == User_Types.ADMIN.value:

            global admin_menu_response, choice_admin
            while True:
                admin_menu_response = None
                admin_menu(us['username'], company_name)
                choice_admin = input('choice: ')
                # show all repos
                if choice_admin == '1':
                    connection.sendall(serializer(choice=choice_admin, username=us['username']))
                    print("pleaase wait...")
                    admin_menu_response = deserializer(connection.recv(4096))
                    repos_resp = admin_menu_response['msg']

                    if isinstance(repos_resp, list):
                        for repo in repos_resp:
                            print(colored(repo, admin_menu_response['color']))
                    else:
                        print(colored(repos_resp, admin_menu_response['color']))

                    c = input("Do you have any other request? (y/n): ")
                    if c == 'y':
                        continue
                    elif c == 'n':
                        print('Bye!')
                        break
                        sys.exit(0)
                    else:
                        print(colored("Unknown command!", 'red'))
                        break
                        sys.exit(0)

                # show repo memebers
                elif choice_admin == '2':
                    repo_name = input("Enter repository name: ")

                    connection.sendall(serializer(choice=choice_admin,
                                                username=us['username'],
                                                repo_name=repo_name
                                                )
                                    )

                    print("please wait ...")

                    admin_menu_response = deserializer(connection.recv(4096))
                    contrbs = admin_menu_response['msg']
                    if isinstance(contrbs, dict):
                        print(colored(contrbs.get("owner"), "magenta"))
                        if contrbs.get('others'):
                            for con in contrbs.get("others"):
                                print(colored(con, admin_menu_response['color']))
                    else:
                        print(colored(contrbs, admin_menu_response['color']))

                    c = input("Do you have any other request? (y/n): ")
                    if c == 'y':
                        continue
                    elif c == 'n':
                        print('Bye!')
                        break
                        sys.exit(0)
                    else:
                        print(colored("Unknown command!", 'red'))
                        break
                        sys.exit(0)

                #show all users
                elif choice_admin == '3':
                    connection.sendall(serializer(choice=choice_admin, username=us['username']))
                    print("pleaase wait...")
                    admin_menu_response = deserializer(connection.recv(4096))
                    users_resp = admin_menu_response['msg']

                    if isinstance(users_resp, list):
                        for user in users_resp:
                            print(colored(user, admin_menu_response['color']))
                    else:
                        print(colored(users_resp, admin_menu_response['color']))

                    c = input("Do you have any other request? (y/n): ")
                    if c == 'y':
                        continue
                    elif c == 'n':
                        print('Bye!')
                        break
                        sys.exit(0)
                    else:
                        print(colored("Unknown command!", 'red'))
                        break
                        sys.exit(0)

                # show user repos
                elif choice_admin == '4':
                    git_username = input("Enter git user username: ")

                    connection.sendall(serializer(choice=choice_admin,
                                                username=us['username'],
                                                git_username=git_username
                                                )
                                    )

                    print("please wait ...")

                    admin_menu_response = deserializer(connection.recv(4096))
                    repos_resp = admin_menu_response['msg']
                    if isinstance(repos_resp, list):
                        for repo in repos_resp:
                            print(colored(repo, admin_menu_response['color']))
                    else:
                        print(colored(repos_resp, admin_menu_response['color']))

                    c = input("Do you have any other request? (y/n): ")
                    if c == 'y':
                        continue
                    elif c == 'n':
                        print('Bye!')
                        break
                        sys.exit(0)
                    else:
                        print(colored("Unknown command!", 'red'))
                        break
                        sys.exit(0)

                # exit
                elif choice_admin == '5':
                    connection.sendall(serializer(choice=choice_admin,
                                                    username=us["username"],
                                                )
                                    )
                    print("Bye!")
                    break
                    sys.exit(0)
                else:
                    print(colored("Unknown command!", 'red'))
                    break
                    sys.exit(0)
        
        # users part
        elif sign_response['user_type'] == User_Types.GIT_USER.value:

            global menu_response, choice
            while True:
                menu_response = None
                menu(us['username'], company_name)
                choice = input('choice: ')
                
                # show my repos
                if choice == '1':
                    connection.sendall(serializer(choice=choice,
                                                username=us['username'],
                                                password=us['password']
                                                )
                                    )

                    print("please wait ...")

                    menu_response = deserializer(connection.recv(4096))
                    repos_resp = menu_response['msg']
                    if isinstance(repos_resp, list):
                        for repo in repos_resp:
                            print(colored(repo, menu_response['color']))
                    else:
                        print(colored(repos_resp, menu_response['color']))

                    c = input("Do you have any other request? (y/n): ")
                    if c == 'y':
                        continue
                    elif c == 'n':
                        print('Bye!')
                        break
                        sys.exit(0)
                    else:
                        print(colored("Unknown command!", 'red'))
                        break
                        sys.exit(0)


                # create repo
                elif choice == '2':

                    repo_name = input("Enter repository name: ")

                    connection.sendall(serializer(choice=choice,
                                                username=us['username'],
                                                password=us['password'],
                                                repo_name=repo_name
                                                )
                                    )

                    print("please wait ...")

                    menu_response   = deserializer(connection.recv(4096))
                    resp_msg        = menu_response['msg'].get('resp_msg', None)
                    link            = menu_response['msg'].get('link', None)
                    if resp_msg is not None and link is not None:
                        print(colored(resp_msg, menu_response['color']))
                        print(colored(link, 'blue'))
                    else:
                        print(colored(resp_msg, menu_response['color']))

                    c = input("Do you have any other request? (y/n): ")
                    if c == 'y':
                        continue
                    elif c == 'n':
                        print('Bye!')
                        break
                        sys.exit(0)
                    else:
                        print(colored("Unknown command!", 'red'))
                        break
                        sys.exit(0)

                # delete repo
                elif choice == '3':

                    repo_name = input("Enter repository name: ")

                    dl_ch = input(colored(f"Are you sure you want delete repository {repo_name}? (y/n): ", 'yellow'))

                    connection.sendall(serializer(choice=choice,
                                                username=us['username'],
                                                password=us['password'],
                                                repo_name=repo_name,
                                                delete_response=dl_ch
                                                )
                                    )

                    print("please wait ...")

                    menu_response = deserializer(connection.recv(4096))

                    print(colored(menu_response['msg'], menu_response['color']))
                    c = input("Do you have any other request? (y/n): ")
                    if c == 'y':
                        continue
                    elif c == 'n':
                        print('Bye!')
                        break
                        sys.exit(0)
                    else:
                        print(colored("Unknown command!", 'red'))
                        break
                        sys.exit(0)


                # get repo link
                elif choice == '4':

                    repo_name = input("Enter repository name: ")

                    connection.sendall(serializer(choice=choice,
                                                username=us['username'],
                                                password=us['password'],
                                                repo_name=repo_name
                                                )
                                    )

                    print("please wait ...")

                    menu_response = deserializer(connection.recv(4096))
                    resp_msg = menu_response['msg'].get('resp_msg', None)
                    link = menu_response['msg'].get('link', None)
                    if resp_msg is not None and link is not None:
                        print(colored(resp_msg, menu_response['color']))
                        print(colored(link, 'blue'))
                    else:
                        print(colored(resp_msg, menu_response['color']))
                    c = input("Do you have any other request? (y/n): ")
                    if c == 'y':
                        continue
                    elif c == 'n':
                        print('Bye!')
                        break
                        sys.exit(0)
                    else:
                        print(colored("Unknown command!", 'red'))
                        break
                        sys.exit(0)

                # show repo contributors
                elif choice == '5':

                    repo_name = input("Enter repository name: ")

                    connection.sendall(serializer(choice=choice,
                                                username=us['username'],
                                                password=us['password'],
                                                repo_name=repo_name
                                                )
                                    )

                    print("please wait ...")

                    menu_response = deserializer(connection.recv(4096))
                    contrbs = menu_response['msg']
                    if isinstance(contrbs, dict):
                        print(colored(contrbs.get("owner"), "magenta"))
                        if contrbs.get("others"):
                            for con in contrbs.get("others"):
                                print(colored(con, menu_response['color']))
                    else:
                        print(colored(contrbs, menu_response['color']))

                    c = input("Do you have any other request? (y/n): ")
                    if c == 'y':
                        continue
                    elif c == 'n':
                        print('Bye!')
                        break
                        sys.exit(0)
                    else:
                        print(colored("Unknown command!", 'red'))
                        break
                        sys.exit(0)




                # add member to repo
                elif choice == '6':

                    repo_name   = input("Enter repository name: ")
                    member      = input("username of contributor: ")

                    connection.sendall(serializer(choice=choice,
                                                username=us['username'],
                                                password=us['password'],
                                                repo_name=repo_name,
                                                member=member
                                                )
                                    )

                    print("please wait ...")

                    menu_response = deserializer(connection.recv(4096))
                    print(colored(menu_response['msg'], menu_response['color']))
                    c = input("Do you have any other request? (y/n): ")
                    if c == 'y':
                        continue
                    elif c == 'n':
                        print('Bye!')
                        break
                        sys.exit(0)
                    else:
                        print(colored("Unknown command!", 'red'))
                        break
                        sys.exit(0)

                # remove member from repo
                elif choice == '7':
                    repo_name   = input("Enter repository name: ")
                    member      = input("username of contributor: ")
                    dl_ch       = input(colored(f"Are yout sure you want delete user {member} from repository {repo_name}? (y/n): ", "yellow"))
                    connection.sendall(serializer(choice=choice,
                                                username=us['username'],
                                                password=us['password'],
                                                repo_name=repo_name,
                                                member=member,
                                                delete_response=dl_ch
                                                )
                                    )

                    print("please wait ...")

                    menu_response = deserializer(connection.recv(4096))
                    print(colored(menu_response['msg'], menu_response['color']))
                    c = input("Do you have any other request? (y/n): ")
                    if c == 'y':
                        continue
                    elif c == 'n':
                        print('Bye!')
                        break
                        sys.exit(0)
                    else:
                        print(colored("Unknown command!", 'red'))
                        break
                        sys.exit(0)



                # delete account
                elif choice == '8':
                    username_auth = input("username: ")
                    password_auth = getpass.getpass(f"[git] password for {username_auth}: ")
                    if username_auth == us['username'] and password_auth == us['password']:
                        dl_ch = input(colored(f"Also all repositories for {username_auth} will be remove\n"
                                    f"Are you sure you want to delete user {username_auth} ? (y/n): ", 'yellow'))

                        connection.sendall(serializer(choice=choice,
                                                    username=username_auth,
                                                    password=password_auth,
                                                    delete_response=dl_ch
                                                    )
                                        )
                        print("please wait ...")
                        menu_response = deserializer(connection.recv(4096))
                        print(colored(menu_response['msg'], menu_response['color']))
                        break
                        sys.exit(0)
                    else:
                        print(colored('Authentication failed.\nusername or password not matched!', 'red'))
                        break
                        sys.exit(0)
                # exit
                elif choice == '9':
                    connection.sendall(serializer(choice=choice,
                                                username=us["username"],
                                                )
                                    )
                    print("Bye!")
                    break
                    sys.exit(0)
                else:
                    print(colored("Unknown command!", 'red'))
                    break
                    sys.exit(0)
        else:
            sys.exit(0)


if __name__ == '__main__':
    main()
