from ckanapi import RemoteCKAN
from pprint import pprint

secret = open("apikey.txt", "r").readline()

ua = 'ckanapiexample/1.0 (+http://example.com/my/website)'
session = RemoteCKAN('https://data.hkppdb.org', apikey=secret, user_agent=ua)

datasource_tags= session.action.tag_list(vocabulary_id="datasources")
# search datasets 

for tag in datasource_tags:
    
    #if tag=="人口普查": break

    packages = session.action.package_search(include_private=True, q=f'vocab_datasources={tag}', rows=1000)
    print(tag, packages['count'])

    for p in packages['results']:
    
        tags_to_have = p.get("datasource", [])
        if tag not in tags_to_have: 
            print(f"add missing datasource tag {tag} {p['title']}")
            tags_to_have.append(tag)
        
            pid = p["id"]
            session.action.package_patch(id=pid, datasource=tags_to_have)