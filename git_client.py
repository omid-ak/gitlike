""" this is the git client """

_author = "omid"

import os
import socket
import pickle
import getpass
from time import sleep
from sys import argv

def menue():
    os.system("clear")
    print('choose :\n'
          '1)create user\n'
          '2)delete user\n'
          '3)create repo\n'
          '4)delete repo\n'
          '5)get repo link\n'
          '6)add contributor to repo\n'
          '7)remove contributor from repo\n'
          '8)exit\n'
          )



def serilizer(**kwargs):
    return pickle.dumps(kwargs)

def main():
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = argv[1]
    port = 7920
    connection.connect((ip, port))

    while True:
        menue()
        choice = input('choice: ')
        # create user
        if choice == '1':
            username = input("username: ")
            password = getpass.getpass(f"[git] password for {username}: ")

            connection.sendall(serilizer(choice=choice, username=username, password=password))
            sleep(5)
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

        elif choice == '2': # delete user
            username = input("username: ")
            password = getpass.getpass(f"[git] password for {username}: ")

            dl_ch = input(f"Also all repositories for {username} will be remove\n"
                          f"Are you sure you want to delete user {username} ? (y/n): ")

            connection.sendall(serilizer(choice=choice, username=username, password=password, delete_response=dl_ch))
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
        elif choice == '3': # create repo
            username = input("username: ")
            password = getpass.getpass(f"[git] password for {username}: ")
            repo_name = input("Enter repository name: ")

            connection.sendall(serilizer(choice=choice, username=username, password=password, repo_name=repo_name))
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
        elif choice == '4':
            username = input("username: ")
            password = getpass.getpass(f"[git] password for {username}: ")
            repo_name = input("Enter repository name: ")

            dl_ch = input(f"Are you sure you want delete repository {repo_name}? (y/n): ")

            connection.sendall(serilizer(choice=choice,
                                         username=username,
                                         password=password,
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
        elif choice == '5':
            username = input("username: ")
            password = getpass.getpass(f"[git] password for {username}: ")
            repo_name = input("Enter repository name: ")

            connection.sendall(serilizer(choice=choice, username=username, password=password, repo_name=repo_name))
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
        elif choice == '6':
            username = input("username: ")
            password = getpass.getpass(f"[git] password for {username}: ")
            repo_name = input("Enter repository name: ")
            member = input("username of contributor: ")

            connection.sendall(serilizer(choice=choice,
                                         username=username,
                                         password=password,
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
        elif choice == '7':
            username = input("username: ")
            password = getpass.getpass(f"[git] password for {username}: ")
            repo_name = input("Enter repository name: ")
            member = input("username of contributor: ")

            connection.sendall(serilizer(choice=choice,
                                         username=username,
                                         password=password,
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
        elif choice == '8':
            print("Bye!")
            break
            exit(0)
        else:
            print('Unknown command !')
            break
            exit(0)



if __name__ == '__main__':
    main()