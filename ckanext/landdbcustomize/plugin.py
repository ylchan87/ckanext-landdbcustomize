#!/usr/bin/python
# -*- coding: utf-8 -*-

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.plugins import DefaultTranslation
import collections

# Custom vocab
update_vocab = True

regions_tags = [
            (u'全港'    , u'全港'  , u'Whole HK'),
            (u'港島'    , u'港岛'  , u'HK Island'),
            (u'九龍'    , u'九龙'  , u'Kowloon'),
            (u'新界'    , u'新界'  , u'NT'),
            (u'地點'    , u'地点'  , u'Point'),
            (u'中西區'  , u'中西区' , u'Central and Western District'),
            (u'東區'    , u'东区'  ,u'Eastern District'),
            (u'南區'    , u'南区'  ,u'Southern District'),
            (u'灣仔區'  , u'湾仔区' ,u'Wan Chai District'),
            (u'深水埗區', u'深水埗区'  ,u'Sham Shui Po District'),
            (u'九龍城區', u'九龙城区'  ,u'Kowloon City District'),
            (u'觀塘區'  , u'观塘区'  ,u'Kwun Tong District'),
            (u'黃大仙區', u'黄大仙区'  ,u'Wong Tai Sin District'),
            (u'油尖旺區', u'油尖旺区'  ,u'Yau Tsim Mong District'),
            (u'離島區'  , u'离岛区'  ,u'Islands District'),
            (u'葵青區'  , u'葵青区'  ,u'Kwai Tsing District'),
            (u'北區'    , u'北区'   ,u'North District'),
            (u'西貢區'  , u'西贡区'  ,u'Sai Kung District'),
            (u'沙田區'  , u'沙田区'  ,u'Sha Tin District'),
            (u'大埔區'  , u'大埔区'  ,u'Tai Po District'),
            (u'荃灣區'  , u'荃湾区'  ,u'Tsuen Wan District'),
            (u'屯門區'  , u'屯门区'  ,u'Tuen Mun District'),
            (u'元朗區'  , u'元朗区'  ,u'Yuen Long District'),
        ]

datasources_tags = [
        (u'運輸及房屋局'       , u'运输及房屋局'           , u'Transport and Housing Bureau'),
        (u'政府統計處'          , u'政府统计处'             , u'Census and Statistics Department'), 
        (u'房屋委員會'         , u'房屋委员会'            , u'Hong Kong Housing Authority'), 
        (u'立法會'              , u'立法会'                , u'LegCo'), 
        (u'地政總署'             , u'地政总署'              , u'Lands Department'), 
        (u'金融管理局'           , u'金融管理局'            , u'Hong Kong Monetary Authority'), 
        (u'一手住宅物業銷售監管局' , u'一手住宅物业销售监管局'  , u'Sales of First-hand Residential Properties Authority'), 
        (u'人口普查'            , u'人口普查'              , u'Population census'), 
        (u'香港政府一站通'       , u'香港政府一站通'         , u'GovHK'),  
        (u'差餉物業估價署'       , u'差饷物业估价署'         , u'Rating and Valuation Department'), 
        (u'私人機構'            , u'私人机构'              , u'Private Agency'), 
        (u'香港按揭證券有限公司'  , u'香港按揭证券有限公司'    , u'The Hong Kong Mortgage Corporation Limited'),
        ]

updatefreqs_tags = [
        (u'5年'    , u'5年'      ,u'5-Yearly'),
        (u'每年'    , u'每年'     ,u'Yearly'), 
        (u'每半年'  , u'每半年'    ,u'Half-Yearly'),  
        (u'每月'    , u'每月'     ,u'Monthly'),
        (u'每季'    , u'每季'     ,u'Quarterly'),
        (u'不定期'  , u'不定期'    ,u'Irregular'),
        (u'一次性'   , u'一次性'   ,u'One-shot'), 
        (u'不再更新' , u'不再更新'  ,u'No longer updated'), 
        ]

def create_vocab(vocabName, tags):
    user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
    context = {'user': user['name']}
    try:
        data = {'id': vocabName}
        toolkit.get_action('vocabulary_show')(context, data)
    except toolkit.ObjectNotFound:
        data = {'name': vocabName}
        vocab = toolkit.get_action('vocabulary_create')(context, data)
    
    data = {'id': vocabName}
    vocab = toolkit.get_action('vocabulary_update')(context, data)
    for tag in tags:
        try:
            data = {'name': tag, 'vocabulary_id': vocab['id']}
            toolkit.get_action('tag_create')(context, data)
        except toolkit.ValidationError:
            # print("Skipped creating tag ", tag)
            #tag already exist?
            pass

def get_vocab(vocabName):
    try:
        tag_list = toolkit.get_action('tag_list')
        vocab_tags = tag_list(data_dict={'vocabulary_id': vocabName})
        return vocab_tags
    except toolkit.ObjectNotFound:
        return None

def regions_autoadd(value):
    if type(value)!=list or len(value)==0: return value
    region = value[0]
    if region in [u'中西區',u'東區',u'南區',u'灣仔區']:
        value.insert(0, u"港島")
    if region in [u'深水埗區',u'九龍城區',u'觀塘區' ,u'黃大仙區',u'油尖旺區']:
        value.insert(0, u"九龍")
    if region in [u'離島區',u'葵青區',u'北區',u'西貢區',u'沙田區',
                  u'大埔區',u'荃灣區',u'屯門區',u'元朗區']:
        value.insert(0, u"新界")
    return value

def regions():
    #FIXME: how to turn off update_vocab after first run?
    if update_vocab: create_vocab('regions', [ t[0] for t in regions_tags])
    return get_vocab('regions')

def datasources():
    if update_vocab: create_vocab('datasources', [ t[0] for t in datasources_tags])
    return get_vocab('datasources')

def updatefreqs():
    if update_vocab: create_vocab('updatefreqs', [ t[0] for t in updatefreqs_tags])
    return get_vocab('updatefreqs')    

def extend_facets_dict(base_facets_dict):
    new_facets_dict = collections.OrderedDict()
    new_facets_dict['vocab_regions'] = toolkit._(u'Region')
    new_facets_dict['vocab_datasources'] = toolkit._(u'Data source')
    new_facets_dict['vocab_updatefreqs'] = toolkit._(u'Update frequency')
    for k,v in base_facets_dict.items():
        new_facets_dict[k]=v
    return new_facets_dict

class LanddbcustomizePlugin(plugins.SingletonPlugin,
                            toolkit.DefaultDatasetForm,
                            DefaultTranslation
                            ):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IFacets)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.ITranslation)

    if update_vocab:
        #translation of terms (these cannot use ITranslate) 
        try:
            user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
            context = {'user': user['name']}
            
            term_translation_update = toolkit.get_action('term_translation_update')
            for tagList in [regions_tags, datasources_tags, updatefreqs_tags]:
                for tag in tagList:
                    data={
                        'term'              : tag[0],
                        'term_translation'  : tag[1],
                        'lang_code'         : "zh_CN", 
                    }
                    term_translation_update(context, data)

                    data={
                        'term'              : tag[0],
                        'term_translation'  : tag[2],
                        'lang_code'         : "en", 
                    }
                    term_translation_update(context, data)
        except:
            print ("Vocab not updated")



    
    # create_vocab('regions', [ t[0] for t in regions_tags] )

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'landdbcustomize')

    # IFacet
    def dataset_facets(self, facets_dict, package_type):
        new_facets_dict = extend_facets_dict(facets_dict)
        return new_facets_dict
    
    def group_facets(self,facets_dict, group_type, package_type):
        # somehow have to edit the facets_dict inplace instead of making a new one
        # https://github.com/ckan/ckan/issues/2713
        n = len(facets_dict)
        items = []
        for i in range(n):
            items.append( facets_dict.popitem(last=False) )
        
        facets_dict['vocab_regions'] = toolkit._(u'Region')
        facets_dict['vocab_datasources'] = toolkit._(u'Data source')
        facets_dict['vocab_updatefreqs'] = toolkit._(u'Update frequency')
        
        for k,v in items:
            facets_dict[k] = v

        return facets_dict
    
    def organization_facets(self,facets_dict, organization_type, package_type):
        # somehow have to edit the facets_dict inplace instead of making a new one
        # https://github.com/ckan/ckan/issues/2713
        n = len(facets_dict)
        items = []
        for i in range(n):
            items.append( facets_dict.popitem(last=False) )
        
        facets_dict['vocab_regions'] = toolkit._(u'Region')
        facets_dict['vocab_datasources'] = toolkit._(u'Data source')
        facets_dict['vocab_updatefreqs'] = toolkit._(u'Update frequency')
        
        for k,v in items:
            facets_dict[k] = v

        return facets_dict
    
    # IPackageController
    def before_search(self, search_params):
        extras = search_params.get('extras')
        if not extras:
            # There are no extras in the search params, so do nothing.
            return search_params

        start_date = extras.get('ext_startdate')
        print("sd", start_date)

        end_date = extras.get('ext_enddate')
        print("ed", end_date)

        if not start_date and not end_date:
            # The user didn't select either a start and/or end date, so do nothing.
            return search_params
        if not start_date:
            start_date = '*'
        if not end_date:
            end_date = '*'

        # Add a date-range query with the selected start and/or end dates into the Solr facet queries.
        fq = search_params.get('fq', u'')
        fq = u'{fq} +extras_start_date:[* TO {ed}] +extras_end_date:[{sd} TO *]'.format(fq=fq, sd=start_date, ed=end_date)
        search_params['fq'] = fq

        return search_params

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
                toolkit.get_converter('convert_to_tags')('regions'),
                regions_autoadd,
                toolkit.get_converter('convert_to_tags')('regions'),
            ],
            'datasource': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_tags')('datasources')
            ],
            'updatefreq': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_tags')('updatefreqs')
            ],
            'start_date': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_validator('isodate'),
                toolkit.get_converter('convert_to_extras'),
            ],
            'end_date': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_validator('isodate'),
                toolkit.get_converter('convert_to_extras')
            ],
            'last_update_date': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_validator('isodate'),
                toolkit.get_converter('convert_to_extras')
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
            'start_date': [
                toolkit.get_converter('convert_from_extras'),
                # toolkit.get_validator('isodate'),
                toolkit.get_validator('ignore_missing')],
            'end_date': [
                toolkit.get_converter('convert_from_extras'),
                # toolkit.get_validator('isodate'),
                toolkit.get_validator('ignore_missing')],
            'last_update_date': [
                toolkit.get_converter('convert_from_extras'),
                # toolkit.get_validator('isodate'),
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