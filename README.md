# git-server-config

**configuring a git vcs on a server and use from client**

Instructions:

Server:<br>

***Notice that run main.py in server only with root user!***<br>

`sudo su`<br>
`python3 -m venv venv`<br>
`source venv/bin/activate`<br>
`pip install -r server/server_requirements.txt`<br>
`python server/main.py`

Client:<br>

`python3 -m venv venv`<br>
`source venv/bin/activate`<br>
`pip install -r client/client_requirements.txt`<br>
`python client/GitLike.py <your_server_ip_address>`
