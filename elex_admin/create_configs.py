import os

from racedates import RACEDATES
INI_TEMPLATE = """[uwsgi]
virtualenv = /home/ubuntu/.virtualenvs/elex-admin
chdir = /home/ubuntu/elex-admin/
wsgi-file = elex_admin/app.py
callable = app
touch-reload = /home/ubuntu/elex-admin/elex_admin/app.py
http-socket = 127.0.0.1:%s
logto = /var/log/elex-admin.uwsgi.log
uid = ubuntu
gid = ubuntu
die-on-term
catch-exceptions
workers = 1
harakiri = 120
max-requests = 50
master"""

nginx_conf = ""

if __name__ == "__main__":
    for i,r in enumerate(RACEDATES):
        port = i+8005
        if not os.path.isfile('elex_admin/%s.ini' % r):
            text = INI_TEMPLATE % port
            with open('elex_admin/%s.ini' % r, 'w') as writefile:
                writefile.write(text)
        nginx_conf += """    location ^~ /elections/2016/admin/%s/ {
        allow 10.0.0.0/8; 
        allow 170.149.100.0/24;
        allow 78.25.224.224/27;
        allow 202.147.18.187/32;
        allow 206.205.234.166/32;
        allow 50.232.13.178/32;
        allow 170.149.100.70/32;
        allow 23.21.126.6/32;
        allow 107.20.172.193/32;
        deny all;
        proxy_pass http://127.0.0.1:%s;
    }
""" % (r, port)

with open('elex_admin/races.conf', 'w') as writefile:
    writefile.write(nginx_conf)