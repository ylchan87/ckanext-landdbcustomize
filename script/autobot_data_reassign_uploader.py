from ckanapi import RemoteCKAN
from pprint import pprint

with open("apikey.txt", "r") as f:
    site = f.readline().strip()
    secret = f.readline()

ua = 'ckanapiexample/1.0 (+http://example.com/my/website)'
session = RemoteCKAN(site, apikey=secret, user_agent=ua)

packages = session.action.package_search(include_private=True, q=f'organization=autobot', rows=1000)

for idx, p in enumerate(packages['results']):
    # group = 政策範疇, owner = 上載者
    groups = [g['name'] for g in p["groups"]]
    if len(groups)==0:
        continue 
    if len(groups)>1: 
        print(groups, p["title"])

    group = groups[0]

    if group=="universal_retirement_protection":
        new_owner = "uppg"
    elif group=="elderly":
        new_owner = "ecp"
    elif group=="urbanrenewal":
        new_owner = "urconcern"
    elif group=="housing":
        new_owner = "hpg"
    elif group=="thelink":
        new_owner = "linkwatch"
    else:
        print("unknown group")
        
    print (f"reassign uploader to {new_owner} {p['title']}")
    pid = p["id"]
    session.action.package_patch(id=pid, owner_org=new_owner)

    #if idx>3: break
