source /usr/lib/ckan/venv/bin/activate #ckan python env
/ckan-entrypoint.sh
ckan -c $CKAN_VENV/src/ckan/ckan/config/sitecfg_test.ini search-index rebuild #needed if change to Solr schema / dataset import ?
ckan -c $CKAN_VENV/src/ckan/ckan/config/sitecfg_test.ini run --host 0.0.0.0
