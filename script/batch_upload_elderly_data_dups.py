import pandas as pd
import re
import hashlib
from ckanapi import RemoteCKAN

with open("apikey.txt", "r") as f:
    site = f.readline().strip()
    secret = f.readline()

ua = 'ckanapiexample/1.0 (+http://example.com/my/website)'
session = RemoteCKAN(site, apikey=secret, user_agent=ua)

def mdy_to_ymd(indate):
    """
    date format convert
    eg. 1/31/2000 becomes 2000-1-13
    """
    if not indate: return ""
    m,d,y = indate.split("/")
    return "-".join([y,m,d])

def isOneToOne(df, col1, col2):
    showWidthBkup = pd.get_option('display.max_colwidth')
    pd.set_option('display.max_colwidth', None)

    tmpdf = df[ [col1,col2] ]
    dupsAB = tmpdf.groupby(col1).filter(lambda g: g[col2].nunique() > 1).drop_duplicates().sort_values([col1,col2])
    print (f"{col1} with multi {col2} :")
    print (dupsAB)

    dupsBA = tmpdf.groupby(col2).filter(lambda g: g[col1].nunique() > 1).drop_duplicates().sort_values([col2,col1])
    print (f"{col2} with multi {col1} :")
    print (dupsBA)

    pd.set_option('display.max_colwidth', showWidthBkup)

    return len(dupsAB)==0 and len(dupsBA)==0

def gen_unique_url(dataset_row):
    outStr = row['title_en']
    outStr = outStr.lower().replace(" ", "_")
    outStr = re.sub(r'\W+', '', outStr)
    if len(outStr)>100:
        key = row['標題'] + row['title_en']
        hash = hashlib.md5(key.encode())
        outStr = outStr[:90] + "_" + hash.hexdigest()[:8]
    return outStr

tmp = session.action.group_list(all_fields=True)
groups_lut = { g['display_name'] : g['name'] for g in tmp}

#==========================================================
# Load data
# this csv is by exporting a airtable
df = pd.read_csv("./dups.csv")  # df means dataframe
df = df.fillna('')
df["標題"] = df["標題"].str.strip()
df["title_en"] = df["title_en"].str.strip()
pd.set_option('display.max_colwidth', -1)
assert isOneToOne(df, "標題", "title_en")

#dups = df[df.duplicated(subset=["title_en"], keep=False)]
#dups = dups.sort_values("title_en")
#dups.to_csv("./dups.csv", index=False)

#df = df.drop_duplicates(subset=["title_en"], keep=False)
bundles = df.groupby("title_en")

startIdx=2
idx = 0
for bundle_name,bundle in bundles:
    idx+=1
    if idx<=startIdx: continue
    

    row = bundle.iloc[0]
    print(f"Adding dataset {idx} {row['標題']}")

    dataset_content = {}
    dataset_content["name"] = gen_unique_url(row)
    dataset_content["title"]    = row['標題']
    dataset_content["title_en"] = row['title_en']
    dataset_content["groups"] = [{'name': groups_lut[g]} for g in row['政策範疇'].split(",")]
    dataset_content["notes"] = "\n".join( [ row['說明'] , row['註'] , row['註2']] ).strip()
    dataset_content["source"] = row['來源']
    dataset_content["tags"] = [{'name': n} for n in row['標籤'].split(",")]
    dataset_content["last_update_date"] = bundle['最後更新日期'].apply(mdy_to_ymd).max()
    dataset_content["datasource"] = row['資料來源']
    dataset_content["region"] = row['地區']
    dataset_content["updatefreq"] = row['更新頻率']
    dataset_content["start_date"] = bundle['數據開始日期'].apply(mdy_to_ymd).min()
    dataset_content["end_date"] = bundle['數據結束日期'].apply(mdy_to_ymd).max()

    dataset_content["license_id"] = 'notspecified'
    dataset_content["owner_org"] = "ecp" # i.e. 安老政策組
    dataset_content["private"] = True

    # keys = list(dataset_content.keys())
    # for key in keys:
    #     if dataset_content[key] == '': del dataset_content[key]

    dataset = session.action.package_create(**dataset_content)
    dataset["id"]

    # add resource to above dataset
    for idx2, row in bundle.iterrows():
        urls = row['來源'].split()
        name = ""
        if not name: name = row["註"]
        if not name: name = url.split("/")[-1]

        for url in urls:
            resource_content = {
                "package_id":dataset["id"],
                "name": name,
                "url":url,
            }
            session.action.resource_create(**resource_content)
    
