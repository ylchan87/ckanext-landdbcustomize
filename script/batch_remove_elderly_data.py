import pandas as pd
import re
import hashlib
from ckanapi import RemoteCKAN

with open("apikey.txt", "r") as f:
    site = f.readline().strip()
    secret = f.readline()

ua = 'ckanapiexample/1.0 (+http://example.com/my/website)'
session = RemoteCKAN(site, apikey=secret, user_agent=ua)

packages = session.action.package_search(include_private=True, q=f'organization=ecp', rows=1000)
print (len(packages["results"]))

## Uncomment to really delete the data
##for idx, p in enumerate(packages['results']):
##    dataset = session.action.dataset_purge(id=p['id'])
    