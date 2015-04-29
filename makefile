# deploy

GIT=git
CTL=supervisorctl -s unix:///tmp/supervisor.sock

start:
	for i in {6000..6009}; do ${CTL} start 'authsys:authsys-web-'$${i}; done

stop:
	for i in {6000..6009}; do ${CTL} stop 'authsys:authsys-web-'$${i}; done

restart:
	for i in {6000..6009}; do ${CTL} restart 'authsys:authsys-web-'$${i}; done

env:
	${GIT} pull

update:
	make env
	make restart 

