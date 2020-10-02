''' General models module '''
import enum


class OutputType(enum.Enum):
    ''' Describe the output types avaliable for reporting '''
    CSV = 'csv'
    XML = 'xml'
    SCREEN = 'screen'

    @staticmethod
    def get_name_list():
        ''' Return all the names of the values '''
        return [item.value for item in OutputType]


class MetadataType:
    ''' Metadata Type Implementation for wrapping the describe log info '''
    def __init__(self, xml_name, dir_name, suffix, has_metadata,
                 in_folder, child_objects):
        self.xml_name = xml_name
        self.dir_name = dir_name
        self.suffix = suffix
        self.has_metadata = bool(has_metadata)
        self.in_folder = bool(in_folder)
        self.child_objects = child_objects.split(',')

    def __repr__(self):
        return f'<{self.xml_name}>'


class MetadataTypeFromJSON:
    ''' Metadata Type Implementation for wrapping the describe log info '''

    def __init__(self, xmlName, dirName, suffix, hasMetadata, inFolder, childObjects):
        self.xml_name       = xmlName
        self.dir_name       = dirName
        self.suffix         = suffix
        self.has_metadata   = hasMetadata
        self.in_folder      = inFolder
        self.child_objects  = childObjects

    def __repr__(self):
        return f'<{self.xml_name}>'


class ChangeType(enum.Enum):
    ''' Type of changes, git like '''
    CREATION = 'A'
    MODIFICATION = 'M'
    DELETION = 'D'
    RENAME = 'R'
