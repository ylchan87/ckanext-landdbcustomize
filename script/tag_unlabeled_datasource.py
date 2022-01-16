from ckanapi import RemoteCKAN
from pprint import pprint
from datetime import datetime

secret = open("apikey.txt", "r").readline().strip()

ua = 'ckanapiexample/1.0 (+http://example.com/my/website)'
session = RemoteCKAN('https://data.hkppdb.org', apikey=secret, user_agent=ua)

packages = []
batch_size = 1000

print(f"{datetime.now()} Look for untagged dataset")
# get all dataset
while True:
    reply = session.action.package_search(include_private=True, rows=1000, start=len(packages))
    packages += reply['results']
    if len(reply['results'])<batch_size: break

for p in packages:
    if 'tags' not in p or len(p['tags'])==0:
        print(f"Dataset {p['title']} has no tag, add tag 未標籤")

        package_tags = [{'name': '未標籤'}]
        pid = p["id"]
        session.action.package_patch(id=pid, tags=package_tags)
    
    else:
        package_tags = p['tags']

        has_unlabeled_tag = False
        for idx,t in enumerate(package_tags):
            if t['name'] == '未標籤': 
                has_unlabeled_tag =True
                break
        
        if has_unlabeled_tag and len(package_tags) >1:
            print(f"Dataset {p['title']} has >1 tags, remove tag 未標籤")
            tmp = package_tags.pop(idx)
            assert tmp['name'] == '未標籤' 

            pid = p["id"]
            session.action.package_patch(id=pid, tags=package_tags)
        
print(f"{datetime.now()} Done")