echo
echo '============= Installing docker ============='
sudo apt-get update
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common

sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt-get update
sudo apt-get install docker-ce


echo
echo '============= Installing python modules ============='
sudo pip install -r requirements.txt

echo
echo '============= Installing mysql-server ============='
sudo apt-get update
sudo apt install mysql-server

echo
echo '============= Initialize db ============='
sudo mysql < ./initial.sql -p

echo
echo '============= Running phantomjs  ============='
sudo docker run -d -p 8910:8910 wernight/phantomjs phantomjs --webdriver=8910
