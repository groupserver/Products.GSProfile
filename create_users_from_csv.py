# coding=utf-8
'''Create Users from CSV file.
'''
from zope.component import createObject
from zope.interface import implements, providedBy
from zope.app.apidoc.interface import getFieldsInOrder
from zope.schema import *
from zope.schema.vocabulary import SimpleTerm
from zope.schema.interfaces import ITokenizedTerm, IVocabulary,\
  IVocabularyTokenized, ITitledTokenizedTerm
from zope.interface.common.mapping import IEnumerableMapping 
from Products.Five import BrowserView
from Products.XWFCore.odict import ODict
from Products.XWFCore.CSV import CSVFile
import interfaces, utils

import logging
log = logging.getLogger('GSCreateUsersFromCSV')

class CreateUsersForm(BrowserView):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.groupsInfo = createObject('groupserver.GroupsInfo', context)
        self.profileList = ProfileList(context)
        self.acl_users = context.site_root().acl_users
        
    @property
    def columns(self):
        retval = []
        
        profileAttributes = {}
        for pa in self.profileList:
            profileAttributes[pa.token] = pa.title
        
        for i in range(0, len(self.profileList)):
            j = i + 65
            columnId = 'column%c' % chr(j)
            columnTitle = u'Column %c'% chr(j)
            column = {
              'columnId':    columnId, 
              'columnTitle': columnTitle, 
              'profileList': self.profileList}
            retval.append(column)
        assert len(retval) > 0
        return retval
        
    def process_form(self):
        form = self.context.REQUEST.form
        result = {}
        result['form'] = form

        if form.has_key('submitted'):
            result['message'] = u''
            result['error'] = False
            
            r = self.process_columns(form)
            result['message'] = '%s\n%s' % (result['message'], r['message'])
            result['error'] = result['error'] or r['error']
            columns = r['columns']

            if not result['error']:
                r = self.process_csv_file(form, columns)
                result['message'] = '%s\n%s' % (result['message'], r['message'])
                result['error'] = result['error'] or r['error']
                csvResults = r['csvResults']
            if not result['error']:
                r = self.process_csv(csvResults, columns)
                result['message'] = '%s\n%s' % (result['message'], r['message'])
                result['error'] = result['error'] or r['error']

            assert result.has_key('error')
            assert type(result['error']) == bool
            assert result.has_key('message')
            assert type(result['message']) == unicode

        assert type(result) == dict
        assert result.has_key('form')
        assert type(result['form']) == dict
        return result
        
    def process_columns(self, form):
        assert type(form) == dict
        assert 'csvfile' in form
        
        message = u''
        error = False
        
        columns = {}
        for key in form:
            if 'column' in key and form[key] != 'nothing':
                foo, col = key.split('column')
                i = ord(col) - 65
                columns[i] = form[key]
                
        requiredColumns = [p for p in self.profileList if p.value.required]
        notSpecified = []

        providedColumns = columns.values()
        for requiredColumn in requiredColumns:
            if requiredColumn.token not in providedColumns:
                print requiredColumn.token 
                notSpecified.append(requiredColumn)
        if notSpecified:
            error = True
            colPlural = len(notSpecified) > 1 and 'columns have' \
              or 'column has'
            colM = '\n'.join(['<li>%s</li>'% c.title for c in notSpecified])
            m = u'<p>The required %s not been specified:</p>\n<ul>%s</ul>' %\
              (colPlural, colM)
            message = u'%s\n%s' % (message, m)
            
        result = {'error':    error,
                  'message':  message,
                  'columns':  columns,
                  'form':   form}
        assert result.has_key('error')
        assert type(result['error']) == bool
        assert result.has_key('message')
        assert type(result['message']) == unicode
        assert result.has_key('columns')
        assert type(result['columns']) == dict
        assert len(result['columns']) >= 2
        assert result.has_key('form')
        assert type(result['form']) == dict
        return result

    def process_csv_file(self, form, columns):
        message = u''
        error = False
        if 'csvfile' not in form:
            m = u'<p>There was no CSV file specified. Please specify a '\
              u'CSV file</p>'
            message = u'%s\n%s' % (message, m)
            error = True
            csvfile = None
            csvResults = None
        else:
            csvfile = form.get('csvfile')
            try:
                csvResults = CSVFile(csvfile, [str]*len(columns))
            except AssertionError, x:
                m = u'<p>The number of columns you have defined (%s) '\
                  u'does not match the number of columns in the CSV file '\
                  u'you provided.</p>' % len(columns)
                error = True
                message = u'%s\n%s' % (message, m)
                csvResults = None
        result = {'error':      error,
                  'message':    message,
                  'csvResults': csvResults,
                  'form':       form}
        assert result.has_key('error')
        assert type(result['error']) == bool
        assert result.has_key('message')
        assert type(result['message']) == unicode
        assert result.has_key('csvResults')
        # assert isinstance(result['csvResults'], CSVFile)
        assert result.has_key('form')
        assert type(result['form']) == dict
        return result

    def process_csv(self, csvResults, columns):
        assert isinstance(csvResults, CSVFile)
        assert type(columns) == dict        

        message = u'<ul>\n'
        error = False
        
        # Map the data into the correctly named columns.
        for row in csvResults.mainData:
            fieldmap = {}
            for column in columns:
                fieldmap[columns[column]] = row[column]
            r = self.process_row(fieldmap)
            error = error or r['error']
            message  = u'%s\n<li>%s</li>' % (message, r['message'])
        message  = u'%s\n</ul>' % (message)
        result = {'error':      error,
                  'message':    message}
        assert result.has_key('error')
        assert type(result['error']) == bool
        assert result.has_key('message')
        assert type(result['message']) == unicode
        return result

    def process_row(self, fields):
        assert type(fields) == dict
        
        existingUser = self.acl_users.get_userByEmail(fields['email'])
        if existingUser:
            fn = existingUser.getProperty('fn')
            uid = existingUser.getId()
            m = u'Should add user %s (%s) to the group %s (%s)' % \
              (fn, uid, self.groupInfo.get_name(), self.groupInfo.get_id())
        else:
            m = u'Should create user for the address %s' % (fields['email'])
        result = {'error':      False,
                  'message':    m}
        assert result.has_key('error')
        assert type(result['error']) == bool
        assert result.has_key('message')
        assert type(result['message']) == unicode
        return result
        
class ProfileList(object):
    implements(IVocabulary, IVocabularyTokenized)
    __used_for__ = IEnumerableMapping

    def __init__(self, context):
        self.context = context
        self.__properties = ODict()

        site_root = context.site_root()

        assert hasattr(site_root, 'GlobalConfiguration')
        config = site_root.GlobalConfiguration
        
        profileSchemaName = config.getProperty('profileInterface',
                                              'IGSCoreProfile')
        profileSchemaName = '%sAdminJoinCSV' % profileSchemaName
        assert hasattr(interfaces, profileSchemaName), \
            'Interface "%s" not found.' % profileSchemaName
        self.__schema = getattr(interfaces, profileSchemaName)
        
    def __iter__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        retval = [SimpleTerm(self.properties[p], p, self.properties[p].title)
                  for p in self.properties.keys()]
        for term in retval:
              assert term
              assert ITitledTokenizedTerm in providedBy(term)
              assert term.value.title == term.title
        return iter(retval)

    def __len__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        return len(self.properties)

    def __contains__(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        retval = False
        retval = value in self.properties
        assert type(retval) == bool
        return retval

    def getQuery(self):
        """See zope.schema.interfaces.IBaseVocabulary"""
        return None

    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        return self.getTermByToken(value)
        
    def getTermByToken(self, token):
        """See zope.schema.interfaces.IVocabularyTokenized"""
        for p in self.properties:
            if p == token:
                retval = SimpleTerm(self.properties[p], p, self.properties[p].title)
                assert retval
                assert ITitledTokenizedTerm in providedBy(retval)
                assert retval.token == retval.value
                return retval
        raise LookupError, token

    @property
    def properties(self):
        assert self.context
        if len(self.__properties) == 0:
            ifs = getFieldsInOrder(self.__schema)
            for interface in ifs:
                self.__properties[interface[0]] = interface[1]
        retval = self.__properties
        assert isinstance(retval, ODict)
        assert retval
        return retval

