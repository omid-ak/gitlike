""" this is the git client """

_author = "omid"

import os
import socket
import pickle
import getpass
from sys import argv
from time import sleep
from pyfiglet import Figlet 

def signin():
    print('sign in:\n')
    username = input("username: ")
    password = getpass.getpass(f"[git] password for {username}: ")
    return {'username': username, 'password': password}

def signup():
    print('sign up:\n')
    username = input("username: ")
    password = getpass.getpass(f"[git] password for {username}: ")
    return {'username': username, 'password': password}

def menue(user, company_name):
    os.system("clear")
    print(greeting(company_name))
    print(f'choose :\t\t\t\tuser:{user}\n'
          
          '1-delete account\n'
          '2-create repository\n'
          '3-delete repository\n'
          '4-get repository link\n'
          '5-add contributor to repository\n'
          '6-remove contributor from repository\n'
          '7-show my repositories\n'
          '8-show repository contributors\n'
          '9-exit\n'
          )


def greeting(company_name):
    f = Figlet(font='standard')
    return f.renderText(company_name)

def serilizer(**kwargs):
    return pickle.dumps(kwargs)


def main():
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = argv[1]
    port = 7920
    connection.connect((ip, port))
    while True:
        company_name = pickle.loads(connection.recv(8192))["company_name"]
        print(f"this is company name: {company_name}")
        sign_response = None
        os.system("clear")
        print(greeting(company_name))
        print("Welcome:\n1)sign in\n2)sign up")
        s = input('choice: ')
        # sign in
        if s == '1':
            us = signin()
            connection.sendall(serilizer(choice=s, username=us['username'], password=us['password']))

            sign_response = connection.recv(8192)
            CONTINUE = pickle.loads(sign_response)['continue']
            print(pickle.loads(sign_response)['msg'])
            break

        # sign up
        elif s == '2':
            us = signup()
            connection.sendall(serilizer(choice=s, username=us['username'], password=us['password']))
            sign_response = connection.recv(8192)
            CONTINUE = pickle.loads(sign_response)['continue']
            print(pickle.loads(sign_response)['msg'])
            break

        else:
            print('Unknown command!')


    if CONTINUE:

        sleep(2)
        while True:
            menu_response = None
            menue(us['username'], company_name)
            choice = input('choice: ')

            # delete account
            if choice == '1':
                username_auth = input("username: ")
                password_auth = getpass.getpass(f"[git] password for {username_auth}: ")
                if username_auth == us['username'] and password_auth == us['password']:
                    dl_ch = input(f"Also all repositories for {username_auth} will be remove\n"
                                  f"Are you sure you want to delete user {username_auth} ? (y/n): ")

                    connection.sendall(serilizer(choice=choice,
                                                 username=username_auth,
                                                 password=password_auth,
                                                 delete_response=dl_ch
                                                 )
                                       )
                    menu_response = connection.recv(8192)
                    print(pickle.loads(menu_response)['msg'])
                    break
                    exit(0)
                else:
                    print('Authentication failed.\nusername or password not matched!')
                    break
                    exit(0)
            # create repo
            elif choice == '2':

                repo_name = input("Enter repository name: ")

                connection.sendall(serilizer(choice=choice,
                                             username=us['username'],
                                             password=us['password'],
                                             repo_name=repo_name
                                             )
                                   )
                menu_response = connection.recv(8192)
                print(pickle.loads(menu_response)['msg'])
                c = input("Do you have any other request? (y/n): ")
                if c == 'y':
                    continue
                elif c == 'n':
                    print('Bye!')
                    break
                    exit(0)
                else:
                    print("Unknown command!")
                    break
                    exit(0)

            # delete repo
            elif choice == '3':

                repo_name = input("Enter repository name: ")

                dl_ch = input(f"Are you sure you want delete repository {repo_name}? (y/n): ")

                connection.sendall(serilizer(choice=choice,
                                             username=us['username'],
                                             password=us['password'],
                                             repo_name=repo_name,
                                             delete_response=dl_ch
                                             )
                                   )
                menu_response = connection.recv(8192)
                print(pickle.loads(menu_response)['msg'])
                c = input("Do you have any other request? (y/n): ")
                if c == 'y':
                    continue
                elif c == 'n':
                    print('Bye!')
                    break
                    exit(0)
                else:
                    print("Unknown command!")
                    break
                    exit(0)


            # get repo link
            elif choice == '4':

                repo_name = input("Enter repository name: ")

                connection.sendall(serilizer(choice=choice,
                                             username=us['username'],
                                             password=us['password'],
                                             repo_name=repo_name
                                             )
                                   )
                menu_response = connection.recv(8192)
                print(pickle.loads(menu_response)['msg'])
                c = input("Do you have any other request? (y/n): ")
                if c == 'y':
                    continue
                elif c == 'n':
                    print('Bye!')
                    break
                    exit(0)
                else:
                    print("Unknown command!")
                    break
                    exit(0)

            # add member to repo
            elif choice == '5':

                repo_name = input("Enter repository name: ")
                member = input("username of contributor: ")

                connection.sendall(serilizer(choice=choice,
                                             username=us['username'],
                                             password=us['password'],
                                             repo_name=repo_name,
                                             member=member
                                             )
                                   )
                menu_response = connection.recv(8192)
                print(pickle.loads(menu_response)['msg'])
                c = input("Do you have any other request? (y/n): ")
                if c == 'y':
                    continue
                elif c == 'n':
                    print('Bye!')
                    break
                    exit(0)
                else:
                    print("Unknown command!")
                    break
                    exit(0)
            # remove member from repo
            elif choice == '6':
                repo_name = input("Enter repository name: ")
                member = input("username of contributor: ")

                connection.sendall(serilizer(choice=choice,
                                             username=us['username'],
                                             password=us['password'],
                                             repo_name=repo_name,
                                             member=member
                                             )
                                   )
                menu_response = connection.recv(8192)
                print(pickle.loads(menu_response)['msg'])
                c = input("Do you have any other request? (y/n): ")
                if c == 'y':
                    continue
                elif c == 'n':
                    print('Bye!')
                    break
                    exit(0)
                else:
                    print("Unknown command!")
                    break
                    exit(0)

            # show my repos
            elif choice == '7':
                connection.sendall(serilizer(choice=choice,
                                             username=us['username'],
                                             password=us['password']
                                             )
                                   )
                menu_response = connection.recv(8192)
                repos = pickle.loads(menu_response)['msg']
                if ',' in repos:
                    for repo in repos.split(','):
                        print(repo)
                else:
                    print(repos)

                c = input("Do you have any other request? (y/n): ")
                if c == 'y':
                    continue
                elif c == 'n':
                    print('Bye!')
                    break
                    exit(0)
                else:
                    print("Unknown command!")
                    break
                    exit(0)

            # show repo contributors
            elif choice == '8':

                repo_name = input("Enter repository name: ")

                connection.sendall(serilizer(choice=choice,
                                             username=us['username'],
                                             password=us['password'],
                                             repo_name=repo_name
                                             )
                                   )
                menu_response = connection.recv(8192)
                desr = pickle.loads(menu_response)
                contrbs = desr['msg']
                if ',' in contrbs:
                    for con in contrbs.split(','):
                        print(con)
                else:
                    print(contrbs)

                c = input("Do you have any other request? (y/n): ")
                if c == 'y':
                    continue
                elif c == 'n':
                    print('Bye!')
                    break
                    exit(0)
                else:
                    print("Unknown command!")
                    break
                    exit(0)
            # exit
            elif choice == '9':
                print("Bye!")
                break
                exit(0)
            else:
                print('Unknown command !')
                break
                exit(0)
    else:
        exit(0)


if __name__ == '__main__':
    main()