''' MatchingRules Module '''
from modules.parser.models import (ChildMetadataType, CompoundMetadataType,
                                   MetadataType, get_child_objects)


class MatchingRule(CompoundMetadataType):
    ''' Custom Label Child Metadata Implementation '''
    TAG_NAME = 'matchingRules'
    PACKAGE_NAME = 'MatchingRule'
    ID_ATTRIBUTE = 'fullName'

    def __hash__(self):
        return hash(str(self))

    class MatchingRuleItem(ChildMetadataType):
        ''' Rule Entry - Assigment Rule implementation '''
        TAG_NAME = 'matchingRuleItems'
        ID_ATTRIBUTE = 'fieldName'

    CHILD_OBJECTS = {'matchingRuleItems': MatchingRuleItem}


class MatchingRules(MetadataType):
    ''' Custom Labels Metadata Implementation '''
    TAG_NAME = 'MatchingRules'
    PACKAGE_NAME = 'MatchingRules'
    CHILD_OBJECTS = get_child_objects(__name__)
    FOLDER_NAME = 'matchingRules'
    EXTENSION_NAME = 'matchingRule'
    CHILD_SEPARATOR = '.'
