''' EscalationRules Module '''
from modules.parser.models import (ChildMetadataType, CompoundMetadataType,
                                   MetadataType, get_child_objects)


class EscalationRule(CompoundMetadataType):
    ''' Custom Label Child Metadata Implementation '''
    TAG_NAME = 'escalationRule'
    PACKAGE_NAME = 'EscalationRule'
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

        class EscalationAction(ChildMetadataType):
            ''' CriteriaItems -  RuleEntry implementation '''
            TAG_NAME = 'escalationAction'

        CHILD_OBJECTS = {'criteriaItems': CriteriaItems,
                         'escalationAction': EscalationAction}

    CHILD_OBJECTS = {'ruleEntry': RuleEntry}


class EscalationRules(MetadataType):
    ''' Custom Labels Metadata Implementation '''
    TAG_NAME = 'EscalationRules'
    PACKAGE_NAME = 'EscalationRules'
    CHILD_OBJECTS = get_child_objects(__name__)
    FOLDER_NAME = 'escalationRules'
    EXTENSION_NAME = 'escalationRules'
    CHILD_SEPARATOR = '.'
