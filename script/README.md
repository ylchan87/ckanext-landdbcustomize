# About

contains example scripts that can edit the ckan database programatically via python


Ref: https://github.com/ckan/ckanapi

# Setup
## create python env
Install python via anaconda
Then create new env
`conda env create -f conda_env.yaml`

## Prepare access key
Login to ckan, go to your user profile, copy the API key and save to `apikey.txt`in this folder

## run one of the script
`python test_ckanapi.py`