PROJECT_DIR=`pwd`
VIRTUAL_ENV_ROOT=$(HOME)/virtual_env
VIRTUAL_ENV_NAME=lisbeth
CRONTAB_FILE=config/crontab/crontab

link_manage_py:
	ln -s $(PROJECT_DIR)/manage.py $(VIRTUAL_ENV_ROOT)/$(VIRTUAL_ENV_NAME)/bin/manage.py
make_dirs:
	mkdir -p $(PROJECT_DIR)/logs/celery/
	mkdir -p $(PROJECT_DIR)/pids/celery/
	mkdir -p $(PROJECT_DIR)/static/
	mkdir -p $(PROJECT_DIR)/state
	mkdir -p $(PROJECT_DIR)/data/cache/beth/
	touch $(PROJECT_DIR)/state/logrotate-state
swap:
	sudo /bin/dd if=/dev/zero of=/var/swap bs=1M count=$(expr $(grep MemTotal /proc/meminfo | awk '{print $2}') / 1024)
	sudo /sbin/mkswap /var/swap
	sudo chmod 600 /var/swap
	sudo /sbin/swapon /var/swap
pull:
	git pull
update_cron:
	crontab $(CRONTAB_FILE)
	sudo service cron restart
update_systemd:
	sudo cp config/systemd/* /etc/systemd/system/
	sudo systemctl daemon-reload
restart:
	sudo systemctl restart gunicorn
	sudo systemctl restart celery
stop:
	sudo systemctl stop gunicorn
	sudo systemctl stop celery
static:
	./manage.py collectstatic --noinput
migrate:
	./manage.py migrate
pip:
	pip install -r requirements.txt
fresh_code: pull pip make_dirs migrate static
deploy: fresh_code update_cron update_systemd restart
venv:
	sudo add-apt-repository universe
	sudo apt-get update
	sudo apt-get install -y python3
	sudo apt-get install -y python3-pip
	sudo apt-get install -y python-dev build-essential git virtualenvwrapper
	sudo apt-get install -y libpq-dev
	sudo apt install libcurl4-openssl-dev libssl-dev
	echo "export WORKON_HOME=~/virtual_env" >> $(HOME)/.bash_aliases
	echo "source /usr/share/virtualenvwrapper/virtualenvwrapper.sh" >> $(HOME)/.bash_aliases
	echo "export VISUAL=vim" >> $(HOME)/.bash_aliases
	echo "export EDITOR=vim" >> $(HOME)/.bash_aliases
	source $(HOME)/.bash_aliases && mkvirtualenv lisbeth --python `which python3.8`
bootstrap: venv make_dirs link_manage_py fresh_code