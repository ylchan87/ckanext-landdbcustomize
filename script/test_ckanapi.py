from ckanapi import RemoteCKAN
ua = 'ckanapiexample/1.0 (+http://example.com/my/website)'

session = RemoteCKAN('https://db.cschk.org', apikey='???', user_agent=ua)

# search datasets 
packages = session.action.package_search(include_private=True, q='運作 organization=autobot')
print(packages['count'])
p = packages['results'][0]

#create dataset
idx = 3
data = {
    'name' : f"test{idx}_name",
    'title' : f"test{idx}_title",
    'title_en' : f"test{idx}_title_en",
    'owner_org' : "autobot"
}
p = session.action.package_create(**data)
pid = p["id"]

# add resource to above dataset
local_resource = {
    "package_id":pid,
    "description": "an img",
    "url":"https://asdf.org",
    "upload": open("/home/roy/Downloads/image.png", "rb")
}
session.action.resource_create(**local_resource)

# list policy categories
gps = session.action.group_list()


# change "uploader"
tmp = session.action.package_patch(id=pid, owner_org="students")