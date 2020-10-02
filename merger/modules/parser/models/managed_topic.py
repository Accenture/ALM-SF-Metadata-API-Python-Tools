''' ManagedTopics Module '''
from modules.parser.models import (CompoundMetadataType, MetadataType,
                                   get_child_objects)


class ManagedTopic(CompoundMetadataType):
    ''' Custom Label Child Metadata Implementation '''
    TAG_NAME = 'managedTopic'
    PACKAGE_NAME = 'ManagedTopic'
    ID_ATTRIBUTE = 'fullName'

    def __hash__(self):
        return hash(str(self))


class ManagedTopics(MetadataType):
    ''' Custom Labels Metadata Implementation '''
    TAG_NAME = 'ManagedTopics'
    PACKAGE_NAME = 'ManagedTopics'
    CHILD_OBJECTS = get_child_objects(__name__)
    FOLDER_NAME = ''  # TODO
    EXTENSION_NAME = ''  # TODO
    HAS_PREFIX = False
    CHILD_SEPARATOR = '.'
