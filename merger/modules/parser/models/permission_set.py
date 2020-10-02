''' Profiles Module '''
from colorama import Fore

from modules.parser.models import (ChildMetadataType, MetadataType,
                                   get_child_objects)


class ApplicationVisibility(ChildMetadataType):
    ''' ApplicationVisibilitie Class Implementation '''
    TAG_NAME = 'applicationVisibilities'
    ID_ATTRIBUTE = 'application'


class ClassAccess(ChildMetadataType):
    ''' ClassAccess Class Implementation '''
    TAG_NAME = 'classAccesses'
    ID_ATTRIBUTE = 'apexClass'


class CustomPermission(ChildMetadataType):
    ''' CustomPermission Class Implementation '''
    TAG_NAME = 'customPermissions'
    ID_ATTRIBUTE = 'name'


class ExternalDataSourceAccess(ChildMetadataType):
    ''' ExternalDataSourceAccess Class Implementation '''
    TAG_NAME = 'externalDataSourceAccesses'
    ID_ATTRIBUTE = 'externalDataSource'


class FieldPermission(ChildMetadataType):
    ''' FieldPermission Class Implementation '''
    TAG_NAME = 'fieldPermissions'
    ID_ATTRIBUTE = 'field'


class ObjectPermissions(ChildMetadataType):
    ''' ObjectPermissions Class Implementation '''
    TAG_NAME = 'objectPermissions'
    ID_ATTRIBUTE = 'object'


class LayoutAssignment(ChildMetadataType):
    ''' LayoutAssignment Class Implementation '''
    TAG_NAME = 'layoutAssignments'
    ID_ATTRIBUTE = 'layout'


class LoginIpRange(ChildMetadataType):
    ''' LoginIpRange Class Implementation '''
    TAG_NAME = 'loginIpRanges'

    def __repr__(self):
        return (f'{Fore.BLUE}<{Fore.CYAN}{self.__class__.__name__}'
                f'{Fore.BLUE}>{Fore.RESET}')


class PageAccess(ChildMetadataType):
    ''' PageAccess Class Implementation '''
    TAG_NAME = 'pageAccesses'
    ID_ATTRIBUTE = 'apexPage'


class RecordTypeVisibility(ChildMetadataType):
    ''' RecordTypeVisibility Class Implementation '''
    TAG_NAME = 'recordTypeVisibilities'
    ID_ATTRIBUTE = 'recordType'


class TabVisibility(ChildMetadataType):
    ''' TabVisibility Class Implementation '''
    TAG_NAME = 'tabVisibilities'
    ID_ATTRIBUTE = 'tab'


class TabSetting(ChildMetadataType):
    ''' TabSettings Class Implementation '''
    TAG_NAME = 'tabSettings'
    ID_ATTRIBUTE = 'tab'


class UserPermission(ChildMetadataType):
    ''' UserPermission Class Implementation '''
    TAG_NAME = 'userPermissions'
    ID_ATTRIBUTE = 'name'


class CustomSettingAccesses(ChildMetadataType):
    ''' CustomSettingAccesses Class Implementation '''
    TAG_NAME = 'customSettingAccesses'
    ID_ATTRIBUTE = 'name'


class FlowAccesses(ChildMetadataType):
    ''' FlowAccesses Class Implementation '''
    TAG_NAME = 'flowAccesses'
    ID_ATTRIBUTE = 'flow'


class CustomMetadataTypeAccesses(ChildMetadataType):
    ''' CustomMetadataTypeAccesses Class Implementation '''
    TAG_NAME = 'customMetadataTypeAccesses'
    ID_ATTRIBUTE = 'name'


class PermissionSet(MetadataType):
    ''' PermissionSet Class Implementation '''
    TAG_NAME = 'PermissionSet'
    PACKAGE_NAME = 'PermissionSet'
    CHILD_OBJECTS = get_child_objects(__name__)
    FOLDER_NAME = 'permissionsets'
    EXTENSION_NAME = 'permissionset'
    CHILD_SEPARATOR = '.'
    MINIMUM_VALUES = {'label'}