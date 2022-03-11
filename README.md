# deskconnd

Secure, cross-platform IPC on the network.

## How to use

### Clone repo

```shell
git clone https://github.com/deskconn/deskconnd.git
cd deskconnd
```

### Install requirements

```
./get_requirements.sh
```
or
```shell
sudo apt install virtualenv
virtualenv venv
source venv/bin/activate
pip3 install wheel -r requirements.txt
```

### Initialization

```shell
./scripts/daemon_dev.sh
```

### Disable Service Discovery

```shell
python3 cli.py discovery disable
```

### Enable Service Discovery

```shell
python3 cli.py discovery enable
```

### Start pairing

```shell
python3 cli.py pair
```
