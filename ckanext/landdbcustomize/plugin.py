#!/usr/bin/python
# -*- coding: utf-8 -*-

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.plugins import DefaultTranslation
from ckan.common import request, config, c

import collections
from .translate_dict import custom_tags,regions_tags,datasources_tags,updatefreqs_tags,datacategories_tags

# Custom vocab
update_vocab = True


def create_vocab(vocabName, tags):
    user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
    context = {'user': user['name']}
    context = {'user': "admin"}  #FIXME: hardcode "admin"

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

def datacategories():
    if update_vocab: create_vocab('datacategories', [ t[0] for t in datacategories_tags])
    return get_vocab('datacategories')


def extend_facets_dict(base_facets_dict):
    new_facets_dict = collections.OrderedDict()
    new_facets_dict['vocab_regions'] = toolkit._(u'Region')
    new_facets_dict['vocab_datasources'] = toolkit._(u'Data source')
    new_facets_dict['vocab_updatefreqs'] = toolkit._(u'Update frequency')
    new_facets_dict['vocab_datacategories'] = toolkit._(u'Data category')
    for k,v in base_facets_dict.items():
        # print("facet dict",k,v )
        if k=='groups': 
            new_facets_dict[k] = toolkit._(u'Topics')
            continue
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
            for tagList in [regions_tags, datasources_tags, updatefreqs_tags, custom_tags, datacategories_tags]:
                for tag in tagList:
                    data={
                        'term'              : tag[0],
                        'term_translation'  : tag[0],
                        'lang_code'         : "zh_Hant_TW", 
                    }
                    term_translation_update(context, data)

                    data={
                        'term'              : tag[0],
                        'term_translation'  : tag[1],
                        'lang_code'         : "zh_Hans_CN", 
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
        #toolkit.add_resource('fanstatic', 'landdbcustomize')
        toolkit.add_resource('assets', 'landdbcustomize')


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
        facets_dict['vocab_datacategories'] = toolkit._(u'Data category')
        
        for k,v in items:
            # print("facet dict",k,v)
            if k=='groups': 
                facets_dict[k] = toolkit._(u'Topics')
                continue
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
        facets_dict['vocab_datacategories'] = toolkit._(u'Data category')
        
        for k,v in items:
            # print("facet dict",k,v)
            if k=='groups': 
                facets_dict[k] = toolkit._(u'Topics')
                continue
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
                'datacategories': datacategories,
               }

    # IDatasetForm

    def _modify_package_schema(self, schema):
        # custom tags
        schema.update({
            'title_en': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras'),
            ],
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
            'datacategory': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_tags')('datacategories')
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
            'title_en': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')],
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
            'datacategory': [
                toolkit.get_converter('convert_from_tags')('datacategories'),
                toolkit.get_validator('ignore_missing'),
            ],
            })

        return schema
    
    def before_view(self, dataset_dict):

        desired_lang_code = request.environ['CKAN_LANG']
        fallback_lang_code = config.get('ckan.locale_default', 'en')

        translated_title = dataset_dict.get("title_" + desired_lang_code, None)
        if translated_title:
            dataset_dict["title"] = translated_title

        return dataset_dict



    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []
