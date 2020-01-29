""" this is the git client """

_author = "omid"

import os
import socket
import pickle
import getpass
from sys import argv

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

def menue():
    os.system("clear")
    print('choose :\n'
          
          '1)delete account\n'
          '2)create repo\n'
          '3)delete repo\n'
          '4)get repo link\n'
          '5)add contributor to repo\n'
          '6)remove contributor from repo\n'
          '7)exit\n'
          )



def serilizer(**kwargs):
    return pickle.dumps(kwargs)

def main():
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = argv[1]
    port = 7920
    connection.connect((ip, port))
    while True:
        os.system("clear")
        print("Welcome:\n1)sign in\n2)sign up")
        s = input('choice: ')
        # sign in
        if s == '1':
            us = signin()
            connection.sendall(serilizer(choice=s, username=us['username'], password=us['password']))
            resp = connection.recv(1024)
            CONTINUE = pickle.loads(resp)['continue']
            print(pickle.loads(resp)['msg'])
            break

        # sign up
        elif s == '2':
            us = signup()
            connection.sendall(serilizer(choice=s, username=us['username'], password=us['password']))
            resp = connection.recv(1024)
            CONTINUE = pickle.loads(resp)['continue']
            print(pickle.loads(resp)['msg'])
            break

        else:
            print('Unknown command!')


    if CONTINUE:
        while True:
            menue()
            choice = input('choice: ')

            # delete account
            if choice == '1':
                username = input("username: ")
                password = getpass.getpass(f"[git] password for {username}: ")

                dl_ch = input(f"Also all repositories for {username} will be remove\n"
                              f"Are you sure you want to delete user {username} ? (y/n): ")

                connection.sendall(serilizer(choice=choice, username=username, password=password, delete_response=dl_ch))
                resp = connection.recv(1024)
                print(pickle.loads(resp)['msg'])
                break
                exit(0)
            elif choice == '2': # create repo

                repo_name = input("Enter repository name: ")

                connection.sendall(serilizer(choice=choice, username=us['username'], password=us['password'], repo_name=repo_name))
                resp = connection.recv(1024)
                print(pickle.loads(resp)['msg'])
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
                resp = connection.recv(1024)
                print(pickle.loads(resp)['msg'])
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

                connection.sendall(serilizer(choice=choice, username=us['username'], password=us['password'], repo_name=repo_name))
                resp = connection.recv(1024)
                print(pickle.loads(resp)['msg'])
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
                resp = connection.recv(1024)
                print(pickle.loads(resp)['msg'])
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
                resp = connection.recv(1024)
                print(pickle.loads(resp)['msg'])
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
            elif choice == '7':
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