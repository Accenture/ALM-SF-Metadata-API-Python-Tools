''' Module for testing parsing '''
from modules.git.utils import get_file
from modules.parser.models.assignment_rules import AssignmentRules
from modules.parser.models.auto_response_rules import AutoResponseRules
from modules.parser.models.custom_labels import CustomLabels
from modules.parser.models.custom_object import Object
from modules.parser.models.escalation_rules import EscalationRules
from modules.parser.models.managed_topic import ManagedTopics
from modules.parser.models.matching_rules import MatchingRules
from modules.parser.models.permission_set import PermissionSet
from modules.parser.models.profiles import Profile
from modules.parser.models.sharing_rules import SharingRules
from modules.parser.models.workflow import Workflow

IMPLEMENTED_CHILD = {AutoResponseRules.PACKAGE_NAME: AutoResponseRules,
                     CustomLabels.PACKAGE_NAME: CustomLabels,
                     Object.PACKAGE_NAME: Object,
                     EscalationRules.PACKAGE_NAME: EscalationRules,
                     ManagedTopics.PACKAGE_NAME: ManagedTopics,
                     MatchingRules.PACKAGE_NAME: MatchingRules,
                     Profile.PACKAGE_NAME: Profile,
                     SharingRules.PACKAGE_NAME: SharingRules,
                     Workflow.PACKAGE_NAME: Workflow}


def parse_file(filename, xml_definition, reference):
    ''' Parse a file into a Object bassed on the definition '''
    print( filename )
    object_class = IMPLEMENTED_CHILD[xml_definition.xml_name]
    return object_class(filename, filestring=get_file(filename, reference))
