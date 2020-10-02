''' Profiles Module '''

from modules.parser.models import (ChildMetadataType, CompoundMetadataType,
                                   MetadataType, get_child_objects)


class WorkflowFieldUpdate(CompoundMetadataType):
    ''' WorkflowFieldUpdate Class Implementation '''
    TAG_NAME = 'fieldUpdates'
    ID_ATTRIBUTE = 'fullName'
    PACKAGE_NAME = 'WorkflowFieldUpdate'


class WorkflowKnowledgePublish(CompoundMetadataType):
    ''' WorkflowKnowledgePublish Class Implementation '''
    TAG_NAME = 'knowledgePublishes'
    ID_ATTRIBUTE = 'label'
    PACKAGE_NAME = 'WorkflowKnowledgePublish'


class WorkflowTask(CompoundMetadataType):
    ''' WorkflowTask Class Implementation '''
    TAG_NAME = 'tasks'
    ID_ATTRIBUTE = 'fullName'
    PACKAGE_NAME = 'WorkflowTask'


class WorkflowAlert(CompoundMetadataType):
    ''' WorkflowAlert Class Implementation '''
    TAG_NAME = 'alerts'
    ID_ATTRIBUTE = 'fullName'
    PACKAGE_NAME = 'WorkflowAlert'

    class Recipient(ChildMetadataType):
        ''' Recipients - WorkflowFieldUpdate '''
        TAG_NAME = 'recipients'
        ID_ATTRIBUTE = 'type'

    CHILD_OBJECTS = {'recipients': Recipient}


# class WorkflowSend(CompoundMetadataType):
#     ''' WorkflowSend Class Implementation '''
#     TAG_NAME = ''
#     ID_ATTRIBUTE = ''
#     PACKAGE_NAME = 'WorkflowSend'


class WorkflowOutboundMessage(CompoundMetadataType):
    ''' WorkflowOutboundMessage Class Implementation '''
    TAG_NAME = 'outboundMessages'
    ID_ATTRIBUTE = 'fullName'
    PACKAGE_NAME = 'WorkflowOutboundMessage'


class WorkflowRule(CompoundMetadataType):
    ''' WorkflowRule Class Implementation '''
    TAG_NAME = 'rules'
    ID_ATTRIBUTE = 'fullName'
    PACKAGE_NAME = 'WorkflowRule'

    class Action(ChildMetadataType):
        ''' Recipients - WorkflowFieldUpdate '''
        TAG_NAME = 'actions'
        ID_ATTRIBUTE = 'name'

    class CriteriaItem(ChildMetadataType):
        ''' Recipients - WorkflowFieldUpdate '''
        TAG_NAME = 'criteriaItems'
        ID_ATTRIBUTE = 'field'

    class WorkflowTimeTriggers(ChildMetadataType):
        ''' Recipients - WorkflowFieldUpdate '''
        TAG_NAME = 'workflowTimeTriggers'

        class Action(ChildMetadataType):
            ''' Action - WorkflowTimeTriggers '''
            TAG_NAME = 'actions'
            ID_ATTRIBUTE = 'name'

        CHILD_OBJECTS = {'actions': Action}

    CHILD_OBJECTS = {'actions': Action,
                     'criteriaItems': CriteriaItem,
                     'workflowTimeTriggers': WorkflowTimeTriggers}


class Workflow(MetadataType):
    ''' PermissionSet Class Implementation '''
    TAG_NAME = 'Workflow'
    PACKAGE_NAME = 'Workflow'
    CHILD_OBJECTS = get_child_objects(__name__)
    FOLDER_NAME = 'workflows'
    EXTENSION_NAME = 'workflow'
    CHILD_SEPARATOR = '.'
