#!/usr/bin/python
# -*- coding: utf-8 -*-

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import collections

# Custom vocab
def create_vocab(vocabName, tags):
    user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
    context = {'user': user['name']}
    try:
        data = {'id': vocabName}
        toolkit.get_action('vocabulary_show')(context, data)
    except toolkit.ObjectNotFound:
        data = {'name': vocabName}
        vocab = toolkit.get_action('vocabulary_create')(context, data)
        for tag in tags:
            data = {'name': tag, 'vocabulary_id': vocab['id']}
            toolkit.get_action('tag_create')(context, data)

def get_vocab(vocabName):
    try:
        tag_list = toolkit.get_action('tag_list')
        vocab_tags = tag_list(data_dict={'vocabulary_id': vocabName})
        return vocab_tags
    except toolkit.ObjectNotFound:
        return None

def regions():
    vocabName = 'regions'
    tags = [
            u'全港',
            u'港島',
            u'九龍',
            u'新界',
            u'地點',
            u'十八區',
        ]
    create_vocab(vocabName, tags)
    return get_vocab(vocabName)

def datasources():
    vocabName = 'datasources'
    tags = [
        u'運輸及房屋局',
        u'政府統計署', 
        u'房屋委員會', 
        u'立法會', 
        u'地政總署', 
        u'金融管理局', 
        u'一手住宅物業銷售監管局',
        u'政府統計處', 
        u'人口普查', 
        u'香港政府一站通',  
        u'差餉物業估價署', 
        u'私人機構', 
        u'香港按揭證券有限公司',
        ]
    create_vocab(vocabName, tags)
    return get_vocab(vocabName)

def updatefreqs():
    vocabName = 'updatefreqs'
    tags = [
        u'5年',
        u'每年', 
        u'每半年',  
        u'每月',
        u'每季',
        u'不定期',
        u'一次性', 
        u'不再更新', 
        ]
    create_vocab(vocabName, tags)
    return get_vocab(vocabName)
    
    
    

class LanddbcustomizePlugin(plugins.SingletonPlugin,toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IFacets)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'landdbcustomize')

    # IFacet
    def dataset_facets(self, facets_dict, package_type):
        new_facets_dict = collections.OrderedDict()
        new_facets_dict['vocab_regions'] = toolkit._(u'地區')
        new_facets_dict['vocab_datasources'] = toolkit._(u'資料來源')
        new_facets_dict['vocab_updatefreqs'] = toolkit._(u'頻率')
        for k,v in facets_dict.items():
            new_facets_dict[k]=v
        return new_facets_dict
    
    def group_facets(self,facets_dict, group_type, package_type):
        return facets_dict
    
    def organization_facets(self,facets_dict, group_type, package_type):
        return facets_dict
    
    # ITemplateHelpers
    # inform the template of our custom vocab
    def get_helpers(self):
        return {
                'regions': regions,
                'datasources': datasources,
                'updatefreqs': updatefreqs,
               }

    # IDatasetForm

    def _modify_package_schema(self, schema):
        # custom tags
        schema.update({
            'region': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_tags')('regions')
            ],
            'datasource': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_tags')('datasources')
            ],
            'updatefreq': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_tags')('updatefreqs')
            ],
        })

        return schema

    def create_package_schema(self):
        # let's grab the default schema in our plugin
        schema = super(LanddbcustomizePlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        # let's grab the default schema in our plugin
        schema = super(LanddbcustomizePlugin, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema
    
    def show_package_schema(self):
        schema = super(LanddbcustomizePlugin, self).show_package_schema()
        
        
        #this line prevent custom tag show in the "tags" field
        schema['tags']['__extras'].append(toolkit.get_converter('free_tags_only'))
        #add custom tags
        schema.update({
            'region': [
                toolkit.get_converter('convert_from_tags')('regions'),
                toolkit.get_validator('ignore_missing')],
            'datasource': [
                toolkit.get_converter('convert_from_tags')('datasources'),
                toolkit.get_validator('ignore_missing')],
            'updatefreq': [
                toolkit.get_converter('convert_from_tags')('updatefreqs'),
                toolkit.get_validator('ignore_missing')],
            })

        return schema
    



    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []