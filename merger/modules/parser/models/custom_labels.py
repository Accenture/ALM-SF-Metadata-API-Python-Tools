''' Module for Custom Labels Implementations '''
from modules.parser.models import (CompoundMetadataType, MetadataType,
                                   get_child_objects)


class CustomLabel(CompoundMetadataType):
    ''' Custom Label Child Metadata Implementation '''
    TAG_NAME = 'labels'
    PACKAGE_NAME = 'CustomLabel'
    ID_ATTRIBUTE = 'fullName'

    def __hash__(self):
        return hash(str(self))


class CustomLabels(MetadataType):
    ''' Custom Labels Metadata Implementation '''
    TAG_NAME = 'CustomLabels'
    PACKAGE_NAME = 'CustomLabels'
    CHILD_OBJECTS = get_child_objects(__name__)
    FOLDER_NAME = 'labels'
    EXTENSION_NAME = 'labels'
    HAS_PREFIX = False
    CHILD_SEPARATOR = '.'
