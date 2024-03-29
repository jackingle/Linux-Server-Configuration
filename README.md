# Introduction

This project is in development for Udacity.  This server configuration
involves hosting and securing a previous project on a public server.
The server is hosted on Amazon Lightsail, secured from common external
attacks.  This is the result of a culmination of skills provided by
Udacity's Full Stack Web Developer Nanodegree Program.

## Server Details

IP Address:  18.223.189.177

URL:  18.223.189.177.xip.io

SSH Port: 2200

DNS:  18.223.189.177.xip.io

## Software Installed

The following commands added all of the necessary software to the server.
```console
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python-pip
sudo pip3 flask
sudo pip3 install sqlalchemy
sudo pip3 install oauth2client
sudo apt-get install PostgreSQL
sudo apt-get install python-virtualenv
sudo apt-get install apache2
sudo apt-get install libapache2-mod-wsgi-py3
sudo apt-get install git
```

## Configuration Changes Made

The SSH port was changed with `sudo nano /etc/ssh/sshd_config` where the 
port number was changed from 22 to 2200.  In order to commit the changes
`sudo service ssh restart`

### Uncomplicated Firewall Changes

These commands restricted security to specifications.
```console
sudo ufw default deny incoming
sudo ufw default deny outgoing
sudo ufw allow 2200/tcp 
sudo ufw allow 80/tcp 
sudo ufw allow 123/udp 
sudo ufw deny 22 
sudo ufw enable 
sudo ufw status 
```

### Grader User Created

grader was created by `sudo adduser grader`
The following commands next setup the grader, give sudo permission, and 
complete security steps.
`sudo nano /etc/sudoers.d/grader` provides a sudoer directory.
Within that file add `grader ALL=(ALL:ALL) ALL`


### RSA Key Creation

RSA SSH keys are created with `ssh-keygen` outside of the server environment.
Follow the next commands and copy your public key information to clipboard
then paste that public key to the authorized_keys file.
```console
su - grader
mkdir .ssh
touch .ssh/authorized_keys
nano .ssh/authorized_keys
service ssh restart
```

### Disable Root Login

Access the sshd config and uncomment and then change `PermitRootLogin` to `no`
```console
sudo nano /etc/ssh/sshd_config
```

### Change Timezone to UTC

```console
sudo timedatectl set-timezone UTC
```

### Clone Item Catalog

Lightsail has a default directory and user named ubuntu.  In that home 
directory clone the Item Catalog with 
`git clone https://github.com/jackingle/Item-Catalog`

### Configure Apache

First create a configuration file for Apache
`sudo nano /etc/apache2/sites-available/catalog.conf`
Paste the following in that file.

```shell
<VirtualHost *:80>
    ServerName 18.223.189.177.xip.io
    ServerAlias 18.223.189.177.xip.io
    ServerAdmin webmaster@localhost
    DocumentRoot /home/ubuntu/Item-Catalog/
    DirectoryIndex client_secrets.json
    WSGIScriptAlias / /home/ubuntu/Item-Catalog/script.wsgi
    <Directory /home/ubuntu/Item-Catalog>
    Options -Indexes +FollowSymLinks +MultiViews
        AllowOverride All
        Require all granted
    </Directory>
    Alias /static /home/ubuntu/Item-Catalog/static
    <Directory /home/ubuntu/Item-Catalog/static/>
    Options -Indexes +FollowSymLinks +MultiViews
        AllowOverride All
        Require all granted
    </Directory>
    <Directory /home/ubuntu/Item-Catalog/templates>
    Options -Indexes +FollowSymLinks +MultiViews
        AllowOverride All
        Require all granted
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/error.log
    LogLevel warn
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

Finally `sudo a2ensite catalog` in order to enable the site.

### Install and Configure PostgreSQL

Ensure no remote connections are available below.
`sudo nano /etc/postgresql/10/main/pg_hba.conf`

Login to PostgreSQL `sudo su - postgres`

Access PostgreSQL `psql`

Create a catalog user `CREATE USER catalog WITH PASSWORD 'password'`

Create the catalog database 
`ALTER USER catalog CREATEDB and CREATE DATABASE catalog WITH OWNER catalog`

Connect to the DB `\c catalog`

Control rights with the following
```
REVOKE ALL ON SCHEMA public FROM public
GRANT ALL ON SCHEMA public TO catalog
\q
```
Exit PostgreSQL and `cd /home/ubuntu/Item-Catalog`

Finally run the following to populate the database.
```console
python3 database_setup.py
python3 populate.py
```

### Last Step

Finally restart the apache server to ensure all changes take effect.
```console
sudo service apache2 restart
```

## Third Party Resources

AWS Lightsail provides the server instance.  The server was created as OS Only
with Ubuntu 18.04LTS.  The cheapest payment plan was chosen.  For one method 
of authentication, I used Lightsail's private SSH key along with Putty.  

Git along with Github is used for version control.

Apache provides the web server and configurations.
