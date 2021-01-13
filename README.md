# User Mobility Profile

Progetto finale per il corso di Industrial Applications, Università di Pisa, a.a. 2020/2021.

![general_scheme](/general%20scheme.jpg)

## Specifications
For see more details, read also [Specifications File](The%20User%20Mobility%20Profile%20Project%20Specification.pdf)

## Prototype Report 
For see more details, read also [Prototype Report](The%20User%20Mobility%20Profile%20Prototype%20Report.pdf)

https://www.raspberrypi.org/software/
############################################################
Image Ubuntu MATE 18.04 LTS Bionic for Raspberry pi 3
############################################################

Install SO: 18.04 LTS (“Bionic”) (Starting in MongoDB Community 3.6.20)
https://releases.ubuntu-mate.org/archived/bionic/arm64/

wget -qO - https://www.mongodb.org/static/pgp/server-3.6.asc | sudo apt-key add -
echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/3.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list


sudo apt-get update
sudo apt-get install -y mongodb

echo "mongodb hold" | sudo dpkg --set-selections
echo "mongodb-server hold" | sudo dpkg --set-selections
echo "mongodb-shell hold" | sudo dpkg --set-selections
echo "mongodb-mongos hold" | sudo dpkg --set-selections
echo "mongodb-tools hold" | sudo dpkg --set-selections


ps --no-headers -o comm 1

sudo systemctl start mongodb
sudo systemctl daemon-reload
sudo systemctl status mongodb
sudo systemctl enable mongodb
sudo systemctl stop mongodb
sudo systemctl restart mongod

Connection
mongo --host 127.0.0.1:27017


Stop Mongo
sudo service mongod stop

nano ~/.bashrc

add: 
alias sudo='sudo '
alias python='/usr/bin/python3.7'
alias pip=pip3

pip install virtualenv
sudo mkdir python-virtual-environments && cd /usr/bin/python-virtual-environments
python3 -m venv env

source env/bin/activate

sudo nano /etc/dphys-swapfile
CONF_SWAPSIZE=100
add 
CONF_SWAPSIZE=1024



sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start

sudo raspi-config

Boot Options> Desktop/Cli > Console Autologin





sudo apt-get install python-pyaudio python3-pyaudio
sudo pip install picamera
sudo pip install cpython
sudo pip install scipy
sudo pip install face_recognition_models


dlib>=19.3.0


User: pi
Password: pi


MongoDB++





apt-get update
apt-get upgrade
apt-get dist-upgrade
reboot

apt-get install mongodb



##################################################################################
Uninstall section
##################################################################################

# Old Version Python 2.7
sudo apt-get remove python2.7
sudo apt-get remove --auto-remove python2.7
sudo apt-get purge python2.7
sudo apt-get purge --auto-remove python2.7


# Old Version Python 3.6

sudo apt-get remove python3.6
sudo apt-get remove --auto-remove python3.6
sudo apt-get purge python3.6
sudo apt-get purge --auto-remove python3.6

sudo apt-get update
sudo apt install software-properties-common


sudo apt-get install python3.7




## Credits

* [R. Bertini](https://github.com/RickyDenton)
* [A. Chianese](https://github.com/Spearton)
* [G. Gagliardi](https://github.com/guidogagl)
* [M. Gómez](https://github.com/MarshaGomez)
* [F. Lapenna](https://github.com/FedericoLapenna)
* [D. Maggi](https://github.com/dariamaggi)