start:
	scripts/daemon_dev.sh

clean:
	rm -f ~/deskconn.db

deps:
	pip3 install -r requirements.txt
