sudo apt update && apt upgrade -y
sudo apt install virtualenv gcc python3-dev -y

virtualenv venv
source venv/bin/activate

pip3 install wheel -r requirements.txt

