source /usr/lib/ckan/venv/bin/activate #ckan python env

ckan-pip3 install -e /usr/lib/ckan/venv/src/ckan/
ckan-pip3 install -e /usr/lib/ckan/venv/src/ckanext-landdbcustomize/
ckan-pip3 install flask_debugtoolbar