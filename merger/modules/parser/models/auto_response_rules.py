''' Auto Response Module '''
from modules.parser.models import (ChildMetadataType, CompoundMetadataType,
                                   MetadataType, get_child_objects)


class AutoResponseRule(CompoundMetadataType):
    ''' AutoResponseRule Child Metadata Implementation '''
    TAG_NAME = 'autoResponseRule'
    PACKAGE_NAME = 'AutoResponseRule'
    ID_ATTRIBUTE = 'fullName'

    def __hash__(self):
        return hash(str(self))

    class RuleEntry(ChildMetadataType):
        ''' RuleEntry - AutoResponseRule implementation '''
        TAG_NAME = 'ruleEntry'

        class CriteriaItems(ChildMetadataType):
            ''' CriteriaItems -  RuleEntry implementation '''
            TAG_NAME = 'criteriaItems'
            ID_ATTRIBUTE = 'field'

        CHILD_OBJECTS = {'criteriaItems': CriteriaItems}

    CHILD_OBJECTS = {'ruleEntry': RuleEntry}


class AutoResponseRules(MetadataType):
    ''' AutoResponseRules Metadata Implementation '''
    TAG_NAME = 'AutoResponseRules'
    PACKAGE_NAME = 'AutoResponseRules'
    CHILD_OBJECTS = get_child_objects(__name__)
    FOLDER_NAME = 'autoResponseRules'
    EXTENSION_NAME = 'autoResponseRules'
    CHILD_SEPARATOR = '.'
