#!/usr/bin/env bash

SCRIPT_PATH=$(dirname $(readlink -f $0 ) )

##
# Bash script to provision VM, used to set up BCA environment.
#
# Be aware this script is only the first time you issue the
#    vagrant up
# command, or following a
#    vagrant destroy
#    vagrant up
# combination.  See the README for further detais.
##

# Update and upgrade the box
sudo apt-get update
sudo apt-get upgrade

# Install subversion
sudo apt-get install subversion

# Install python-dev
sudo apt-get install -y python-dev

# Install pip and flask
sudo apt-get install -y python-pip
sudo pip install flask

# Needed for libewf
sudo apt-get install zlib1g-dev

# Install Postgress as back end database
sudo apt-get install -y postgresql

# PGAdmin 3 for database management
sudo apt-get install -y pgadmin3

# Postgress dev package
sudo apt-get install -y postgresql-server-dev-9.3

# psycopg2 and flask SQL Alchemy
sudo pip install -U psycopg2
sudo pip install Flask-SQLAlchemy

#SSS:
sudo pip install flask-wtf

# libtalloc
sudo apt-get install -y libtalloc2
sudo apt-get install -y libtalloc-dev

# Check postgress setup
check_install postgresql postgresql

# .pgpass contains the password for user vagrant. This needs to be
# in the home directory.
sudo cp /vagrant/.pgpass /home/vagrant/.pgpass

# Start postgress and setup up postgress user
sudo service postgresql start

# Create the database bca_db with owner vagrant
# First create user "vagrant":
sudo -u postgres psql -c"CREATE user vagrant WITH PASSWORD 'vagrant'"

# Now create the database
sudo -u postgres createdb -O vagrant bca_db

sudo service postgresql restart

## Instal java jdk:  (Installs in  /usr/lib/jvm/java-6-openjdk)
sudo apt-get install -y openjdk-7-jdk
sudo apt-get install -y openjdk-7-jre-headless
sudo apt-get install -y openjdk-7-jre-lib

### Install ant: (installs in /usr/bin/ant)

sudo apt-get install -y ant
sudo apt-get install -y ant-doc
sudo apt-get install -y ant-optional

## Install ivy

sudo apt-get install -y ivy
sudo apt-get install -y ivy-doc

# Update shared libraries
sudo ldconfig

cd /tmp

#  Install pylucene. It also installs JCC
sudo wget http://www.trieuvan.com/apache/lucene/pylucene/pylucene-4.9.0-0-src.tar.gz

tar xzf pylucene-4.9.0-0-src.tar.gz  

cd pylucene-4.9.0-0

pushd jcc

python setup.py build
python setup.py install

popd # puts us back on pylucene directory

# Here we have to edit the Makefile to uncomment the config info for Linux.
# First we look for the requred string in the makefile and copy the 5 lines
# strting from the 4th line after the pattern match, into a temp file (temp),
# after removing the leading hash (to uncomment the lines).
# Then we append these lines from temp file to Makefile after the given pattern
# is found.

grep -A 8 "Ubuntu 11.10 64-bit" Makefile | sed -n '4,8p' | sed 's/^#//' > temp
sed -i -e '/Ubuntu 11.10 64-bit/r temp' Makefile

make
sudo make install

# Install libewf 
cd /tmp
sudo wget https://53efc0a7187d0baa489ee347026b8278fe4020f6.googledrive.com/host/0B3fBvzttpiiSMTdoaVExWWNsRjg/libewf-20140608.tar.gz
tar -xzvf libewf-20140608.tar.gz
cd libewf-20140608
bootstrap
./configure --enable-v1-api
make
sudo make install
sudo ldconfig

# Install sleuthkit
cd /tmp
sudo wget http://sourceforge.net/projects/sleuthkit/files/latest/download?source=files -O sleuthkit.tar.gz
tar -xzvf sleuthkit.tar.gz
wget https://4a014e8976bcea5c2cd7bfa3cac120c3dd10a2f1.googledrive.com/host/0B3fBvzttpiiScUxsUm54cG02RDA/tsk4.1.3_external_type.patch
sed  -i '/TSK_IMG_TYPE_EWF_EWF = 0x0040,  \/\/\/< EWF version/a \
\
        TSK_IMG_TYPE_EXTERNAL = 0x1000,  \/\/\/< external defined format which at least implements TSK_IMG_INFO, used by pytsk' /tmp/sleuthkit-4.1.3/tsk/img/tsk_img.h
cd sleuthkit-4.1.3
./configure
make
sudo make install
sudo ldconfig

# Python tsck bindings
sudo apt-get install -y git
cd /tmp
git clone https://github.com/py4n6/pytsk
cd pytsk
python setup.py build
sudo python setup.py install

# install antiword (doc2text) and pdf2text
sudo apt-get install -y antiword
sudo apt-get install -y poppler-utils


# link to the shared image folder
#sudo mkdir /home/bcadmin
#sudo ln -s /vagrant/disk-images /home/bcadmin/disk_images

#start the server
#cd /vagrant
#python runserver.py &
