# Introduction

This project is in development for Udacity.  

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

## Configuration changes made

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

### Grader user created

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

### Disable root login

Access the sshd config and uncomment and then change `PermitRootLogin` to `no`
```console
sudo nano /etc/ssh/sshd_config
```

### Change Timezone to UTC

```console
sudo timedatectl set-timezone UTC
```

## Third Party Resources

AWS Lightsail provides the server instance.  The server was created as OS Only
with Ubuntu 18.04LTS.  The cheapest payment plan was chosen.  For one method 
of authentication, I used Lightsail's private SSH key along with Putty.  

Git along with Github is used for version control.


