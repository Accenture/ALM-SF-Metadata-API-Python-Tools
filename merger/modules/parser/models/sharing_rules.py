''' Sharing Rules module '''

from modules.parser.models import (ChildMetadataType, MetadataType,
                                   CompoundMetadataType, get_child_objects)


class SharingCriteriaRules(CompoundMetadataType):
    ''' SharingCriteriaRules Implementation '''
    TAG_NAME = 'sharingCriteriaRules'
    PACKAGE_NAME = 'SharingCriteriaRule'
    ID_ATTRIBUTE = 'fullName'

    class AccountSettings(ChildMetadataType):
        ''' AccountSettings - ChildMetadataType
            child object implementation '''
        TAG_NAME = 'accountSettings'

    class SharedTo(ChildMetadataType):
        ''' SharedTo - ChildMetadataType
            child object implementation '''
        TAG_NAME = 'sharedTo'

    class CriteriaItems(ChildMetadataType):
        ''' CriteriaItems - ChildMetadataType
            child object implementation '''
        TAG_NAME = 'criteriaItems'

    CHILD_OBJECTS = {'accountSettings': AccountSettings,
                     'sharedTo': SharedTo,
                     'criteriaItems': CriteriaItems}


class SharingOwnerRules(CompoundMetadataType):
    ''' SharingOwnerRules Implementation '''
    TAG_NAME = 'sharingOwnerRules'
    PACKAGE_NAME = 'SharingOwnerRule'
    ID_ATTRIBUTE = 'fullName'

    class AccountSettings(ChildMetadataType):
        ''' SharingOwnerRules - SharingOwnerRules
            child object implementation '''
        TAG_NAME = 'accountSettings'

    class SharedTo(ChildMetadataType):
        ''' SharingOwnerRules - SharingOwnerRules
            child object implementation '''
        TAG_NAME = 'sharedTo'

    class SharedFrom(ChildMetadataType):
        ''' SharingOwnerRules - SharingOwnerRules
            child object implementation '''
        TAG_NAME = 'sharedFrom'

    class CriteriaItems(ChildMetadataType):
        ''' SharingOwnerRules - SharingOwnerRules
            child object implementation '''
        TAG_NAME = 'criteriaItems'

    CHILD_OBJECTS = {'accountSettings': AccountSettings,
                     'sharedTo': SharedTo,
                     'sharedFrom': SharedFrom}


class SharingRules(MetadataType):
    ''' Custom Object Class Implementation '''
    TAG_NAME = 'SharingRules'
    PACKAGE_NAME = 'SharingRules'
    CHILD_OBJECTS = get_child_objects(__name__)
    FOLDER_NAME = 'sharingRules'
    EXTENSION_NAME = 'sharingRules'
    CHILD_SEPARATOR = '.'
