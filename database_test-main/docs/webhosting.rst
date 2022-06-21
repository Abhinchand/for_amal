==============================
Web Hosting
==============================


Virtual environment::

    pip install virtualenv
    virtualenv env
    source env/bin/activate

Install dependencies::

    pip install -r requirements.txt

PostgreSQL is a powerful, open-source object-relational database system

* Install PostgreSQL::

    sudo apt-get install python-dev
    sudo apt-get install postgresql-server-dev-9.1
    sudo apt-get install python-psycopg2 - Or sudo pip install psycopg2
    sudo apt-get install postgresql pgadmin3

* Change the default password::

    sudo su
    su postgres -c psql postgres
    ALTER USER postgres WITH PASSWORD 'YourPassWordHere';
    \q

* Create the database::

    sudo su
    su postgres -c psql postgres
    CREATE DATABASE dbname;
    CREATE USER djangouser WITH ENCRYPTED PASSWORD 'myPasswordHere';
    GRANT ALL PRIVILEGES ON DATABASE dbname TO djangouser;

* Django settings::

    DATABASES = {
    'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'dbname',
    'USER': 'postgres',
    'PASSWORD': 'postgres',
    'HOST': '',
    'PORT': '',
    }
    }


Nginx is a web server that can also be used as a reverse proxy, load balancer, mail proxy and HTTP cache. Nginx can be deployed to server dynamic HTTP content on the network using WSGI application servers (an example) and it can serve as a software load balancer. Nginx will face the outside world. It will serve media files (images, CSS, etc) directly from the file system. However, it can't talk directly to Django applications; it needs something (uWSGI) that will run the application, feed it requests from the web, and return responses. `Refer1 <https://serverfault.com/a/887845>`_.


* Install Nginx::

    sudo apt-get install nginx

* Nginx configuration file Location::

    /etc/nginx/conf.d/virtual.conf

* conf file contents::

    server {
    listen 80;
    server_name {your domain_name};
    error_log /srv/www/database/logs/error.log;
    access_log /srv/www/database/logs/access.log;
    charset utf-8;

    location /static/ {
    alias /srv/www/database/static/;
    }

    location /media/ {
    alias /srv/www/database/media/;
    }

    location / {
    add_header 'Cache-Control' 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0';
    expires off;
    #uwsgi_pass unix:/opt/uwsgi/sock/database.sock;
    proxy_connect_timeout 300s;
    proxy_read_timeout 300s;
    proxy_pass http://127.0.0.1:8000;
    include uwsgi_params;
    }

    #root /srv/www/database_test/database/templates/extra;
    #index site-down.html;

    }

* Nginx file location::

    /var/log/nginx/error.log

uWSGI is a popular web server that implements the WSGI (pronounced wiz-gee) standard. WSGI (Web Server Gateway Interface) is a software specification, uWSGI is a web server. It’s pretty common to pair Django and uWSGI since they both talk WSGI. The uWSGI server is a full featured HTTP server that is quite capable of running production web apps. However, it’s not as performant as nginx at serving static content, so it’s pretty common to see nginx sitting in front a uWSGI server. Here’s where some poor naming choices make things even more confusing. So we know WSGI is a software spec, uWSGI is a server, so what the hell is uwsgi? When it’s spelled using all lowercase letters, it refers to a binary protocol for connecting the uWSGI server to other applications. `Refer2 <https://www.ultravioletsoftware.com/single-post/2017/03/23/An-introduction-into-the-WSGI-ecosystem>`_.

* Install uWSGI::

    sudo apt-get install build-essential python
    sudo apt-get install python-dev
    pip install uwsgi

* uwsgi emperor configuration location::

    /etc/uwsgi/emperor.ini

* uwsgi emperor configuration contents::

    [uwsgi]
    emperor = /etc/uwsgi/vassals
    uid = uwsgi
    gid = uwsgi
    logto = /etc/uwsgi/log/uwsgilog

* uwsgi vassals configuration location::

    /etc/uwsgi/vassals/demo.ini

* uwsgi vassals configuration contents::

    [uwsgi]
    http = :8000
    workers = 1
    processes = 1
    socket = /opt/uwsgi/sock/database.sock
    chdir = /srv/www/database/
    pythonpath = /srv/www/database/database/
    home = /opt/python-virtual-env/
    logto = /srv/www/database/logs/uwsgi.log
    module = BPPRC.wsgi
    uid = uwsgi
    chmod-socket = 666
    chown-socket = uwsgi
    harakiri = 300


* uwsgi log file location::

    /etc/uwsgi/log/uwsgilog


* Install Needle::

    Needed for BestMatchFinder app

    Download EMBOSS-6.x.x.tar.gz
    Gunzip EMBOSS-6.x.x.tar.gz
    tar xvf EMBOSS-6.x.x.tar.gz
    cd EMBOSS-6.x.x
    ./configure
    make

It should be able to run in the terminal. Provide a full path in both production as well as local. This applies to all the binary external softwares.


* Clustal Omega::

     Needed for Clustalanalysis app

     Download http://clustal.org/omega/.
     Clustal installation instructions can be found http://clustal.org/omega/INSTALL.

* Manage the production and local settings::

    Use a `.env` files in the production and local with respective settings

    Example production `.env` file::

    SECRET_KEY='………'
    EMAIL_BACKEND='django_ses.SESBackend'

    #Amazon key
    AWS_ACCESS_KEY_ID='……..'
    AWS_SECRET_ACCESS_KEY='…’
    AWS_SES_REGION_NAME='us-east-1'
    AWS_SES_REGION_ENDPOINT='email-smtp.us-east-1.amazonaws.com'

    CRISPY_TEMPLATE_PACK='bootstrap4'
    CSRF_COOKIE_SECURE=True

    # google recaptcha
    RECAPTCHA_PUBLIC_KEY="6Lc-HfMUAAAAALHi0-vkno4ntkJvLW3rAF-d5UXT"

    # used betweeen server and reCAPTCHA
    RECAPTCHA_PRIVATE_KEY="6Lc-HfMUAAAAAI2H-DuGJKPETsB_ep3EQNKkdesC"

    NEEDLE_PATH='/opt/EMBOSS-6.6.0/emboss/'
    BLAST_PATH='/usr/local/bin/'
    CLUSTAL_PATH='/usr/local/bin/'
    DATABASE_TYPE='production'


    Example local `.env` file::

    SECRET_KEY=’’
    DEVELOPMENT=True

    AWS_ACCESS_KEY_ID=''
    AWS_SECRET_ACCESS_KEY=''

    CRISPY_TEMPLATE_PACK='bootstrap4'
    CSRF_COOKIE_SECURE=True

    # used betweeen server and reCAPTCHA
    RECAPTCHA_PRIVATE_KEY="6Lc-HfMUAAAAAI2H-DuGJKPETsB_ep3EQNKkdesC"

    NEEDLE_PATH='/usr/local/bin/'
    BLAST_PATH=''
    CLUSTAL_PATH='/sw/bin/'

    DATABASE_TYPE='sqlite3'
