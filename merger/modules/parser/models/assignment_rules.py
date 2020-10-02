''' Assigment Rules Object Module '''
from modules.parser.models import (ChildMetadataType, CompoundMetadataType,
                                   MetadataType, get_child_objects)


class AssignmentRule(CompoundMetadataType):
    ''' AssigmentRule Child Metadata Implementation '''
    TAG_NAME = 'assignmentRule'
    PACKAGE_NAME = 'AssignmentRule'
    ID_ATTRIBUTE = 'fullName'

    def __hash__(self):
        return hash(str(self))

    class RuleEntry(ChildMetadataType):
        ''' Rule Entry - Assigment Rule implementation '''
        TAG_NAME = 'ruleEntry'
        ID_ATTRIBUTE = 'assignedTo'

        class CriteriaItems(ChildMetadataType):
            ''' CriteriaItems -  RuleEntry - AssigmentRule implementation '''
            TAG_NAME = 'criteriaItems'
            ID_ATTRIBUTE = 'field'

        CHILD_OBJECTS = {'criteriaItems': CriteriaItems}

    CHILD_OBJECTS = {'ruleEntry': RuleEntry}


class AssignmentRules(MetadataType):
    ''' AssignmentRules Metadata Implementation '''
    TAG_NAME = 'AssignmentRules'
    PACKAGE_NAME = 'AssignmentRules'
    CHILD_OBJECTS = get_child_objects(__name__)
    FOLDER_NAME = 'assignmentRules'
    EXTENSION_NAME = 'assignmentRules'
    CHILD_SEPARATOR = '.'
