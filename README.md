# Introduction

This project is in development for Udacity.  It consists of an Item Catalog
including a front end website with user authentication through OAuth2 and a
back end database.  Properly logged in users may edit information in the
database utilizing REST API.


## The Database

The database contains spells that you might find in a traditional
RPG(Role Playing Game).  Three tables within the database include Users, School,
and Spell.  Spells in RPGs are often split into Schools of Magic.  


## Installation

This project requires a virtual machine provided by Udacity and Python.

- Python 2 or 3(any version)
- Vagrant
- ViritualBox

The necessary virtual machine can be found [at this link](https://github.com/udacity/fullstack-nanodegree-vm/blob/master/vagrant/Vagrantfile).

Install Vagrant from [here](https://www.vagrantup.com/downloads.html).

Install ViritualBox from [here](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1).


### Start the virtual machine

You will need some form of Unix shell in order to execute commands to log in to
the virtual machine.  After you have installed the dependencies, use the
following commands.  
``` console
cd /vagrant/
vagrant up
vagrant ssh
```


### Import required modules

Depending on whether you would like to utilize python2 or python3, use pip or pip3 respectively.  It might be necessary in some cases to add sudo to the beginning of these install statements and append `--user`

``` console
pip3 install flask
pip3 install sqlalchemy
pip3 install oauth2client
pip3 install requests
```


### Run the database setup file

Initialize the database by running the code below.  This will generate the
database and populate it with a few spells.  I will add more categories soon.
``` console
python3 database_setup.py
python3 populate.py
```


### Run the server file

Place the files in the repository in the shared folder for the virtual machine.
The example
code below shows python3 being used but this program will work in python2 as
well.
``` console
python3 spelllist.py
```


### Access the website locally

The URL for the program is set to work only at http://localhost:8000


## Known issues

Create a new spell should only appear once on specSpell.html.
