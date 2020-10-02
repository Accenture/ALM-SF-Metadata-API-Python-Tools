''' Custom Object Module '''
from colorama import Fore

from modules.parser.models import (ChildMetadataType, CompoundMetadataType,
                                   MetadataType, get_child_objects)


class ActionOverride(ChildMetadataType):
    ''' Action Override Classs Implementation '''
    TAG_NAME = 'actionOverrides'
    ID_ATTRIBUTE = 'actionName'


class BusinessProcess(CompoundMetadataType):
    ''' Business Process Classs Implementation '''
    TAG_NAME = 'businessProcesses'
    PACKAGE_NAME = 'BusinessProcess'
    ID_ATTRIBUTE = 'fullName'

    class Value(ChildMetadataType):
        ''' DisplayedField - FieldSet child object implementation '''
        TAG_NAME = 'values'
        ID_ATTRIBUTE = 'fullName'

    CHILD_OBJECTS = {'values': Value}


class CompactLayout(CompoundMetadataType):
    ''' Compact Layout Classs Implementation '''
    TAG_NAME = 'compactLayouts'
    PACKAGE_NAME = 'CompactLayout'
    ID_ATTRIBUTE = 'fullName'


class CustomField(CompoundMetadataType):
    ''' Custom Field Class Implementation '''
    TAG_NAME = 'fields'
    PACKAGE_NAME = 'CustomField'
    ID_ATTRIBUTE = 'fullName'

    class ValueSet(ChildMetadataType):
        ''' Value Set - Custom Field child object implementation '''
        TAG_NAME = 'valueSet'

        class ValueSetDefinition(ChildMetadataType):
            ''' Value Set Definition - Value Setd child
                object implementation '''
            TAG_NAME = 'valueSetDefinition'

            class Value(ChildMetadataType):
                ''' Value - Value Setd child object implementation '''
                TAG_NAME = 'value'
                ID_ATTRIBUTE = 'fullName'

            CHILD_OBJECTS = {'value': Value}

        class ValueSettings(ChildMetadataType):
            ''' Value Settings - Value Set child object implementation '''
            TAG_NAME = 'valueSettings'
            ID_ATTRIBUTE = 'valueName'

        CHILD_OBJECTS = {'valueSetDefinition': ValueSetDefinition,
                         'valueSettings': ValueSettings}

    class LookupFilter(ChildMetadataType):
        ''' LookUp Filter - Custom Field child object implementation '''
        TAG_NAME = 'lookupFilter'

        class FilterItems(ChildMetadataType):
            ''' FilterItems - Custom Field child object implementation '''
            TAG_NAME = 'filterItems'
            ID_ATTRIBUTE = 'field'

        CHILD_OBJECTS = {'filterItems': FilterItems}

    class SummaryFilterItems(ChildMetadataType):
        ''' Summary Filter Items - Custom Field child object implementation '''
        TAG_NAME = 'summaryFilterItems'

    CHILD_OBJECTS = {'valueSet': ValueSet,
                     'lookupFilter': LookupFilter,
                     'summaryFilterItems': SummaryFilterItems}


class FieldSet(CompoundMetadataType):
    ''' Field Set Class Implementation '''
    TAG_NAME = 'fieldSets'
    PACKAGE_NAME = 'FieldSet'
    ID_ATTRIBUTE = 'fullName'

    class DisplayedField(ChildMetadataType):
        ''' DisplayedField - FieldSet child object implementation '''
        TAG_NAME = 'displayedFields'
        ID_ATTRIBUTE = 'field'

    class AvailableFields(ChildMetadataType):
        ''' DisplayedField - FieldSet child object implementation '''
        TAG_NAME = 'availableFields'
        ID_ATTRIBUTE = 'field'

    CHILD_OBJECTS = {'displayedFields': DisplayedField,
                     'availableFields': AvailableFields}


class HistoryRetentionPolicy(ChildMetadataType):
    ''' History Retention Policy Class Implementation '''
    TAG_NAME = 'historyRetentionPolicy'
    ID_ATTRIBUTE = ''


class Index(CompoundMetadataType):
    ''' Index Class Implementation '''
    TAG_NAME = 'indexes'
    PACKAGE_NAME = 'Index'
    ID_ATTRIBUTE = 'fullName'

    class Field(ChildMetadataType):
        ''' Custom Field Class Implementation '''
        TAG_NAME = 'fields'
        ID_ATTRIBUTE = 'name'

    CHILD_OBJECTS = {'fields': Field}


class ListView(CompoundMetadataType):
    ''' List View Class Implementation '''
    TAG_NAME = 'listViews'
    PACKAGE_NAME = 'ListView'
    ID_ATTRIBUTE = 'fullName'

    class Filter(ChildMetadataType):
        ''' Filter - List View child object implementation '''
        TAG_NAME = 'filters'
        ID_ATTRIBUTE = 'field'

    class SharedTo(ChildMetadataType):
        ''' SharedTo - List View child object implementation '''
        TAG_NAME = 'sharedTo'

    CHILD_OBJECTS = {'filters': Filter,
                     'sharedTo': SharedTo}


class RecordType(CompoundMetadataType):
    ''' Record Type Class Implementation '''
    TAG_NAME = 'recordTypes'
    PACKAGE_NAME = 'RecordType'
    ID_ATTRIBUTE = 'fullName'

    class PicklistValues(ChildMetadataType):
        ''' Record Type Picklist Values implementation '''
        TAG_NAME = 'picklistValues'
        ID_ATTRIBUTE = 'picklist'

        class PicklistValue(ChildMetadataType):
            ''' Record Type Picklist Value implementation '''
            TAG_NAME = 'values'
            ID_ATTRIBUTE = 'fullName'

        CHILD_OBJECTS = {'values': PicklistValue}

    CHILD_OBJECTS = {'picklistValues': PicklistValues}


class SearchLayouts(ChildMetadataType):
    ''' Search Layouts Class Implementation '''
    TAG_NAME = 'searchLayouts'
    ID_ATTRIBUTE = None

    def __init__(self, xml, name_prefix=''):
        super().__init__(xml, name_prefix)
        self._apiname = 'SearchLayouts'

    def __repr__(self):
        return (f'{Fore.BLUE}<{Fore.CYAN}{self.__class__.__name__}'
                f'{Fore.BLUE}>{Fore.RESET}')


class SharingReason(CompoundMetadataType):
    ''' Sharing Reason Class Implementation '''
    TAG_NAME = 'sharingReasons'
    PACKAGE_NAME = 'SharingReason'
    ID_ATTRIBUTE = 'fullName'


class SharingRecalculation(ChildMetadataType):
    ''' Sharing Recalculation Class Implementation '''
    TAG_NAME = 'sharingRecalculations'
    ID_ATTRIBUTE = 'className'


class ValidationRule(CompoundMetadataType):
    ''' Validation Rule Class Implementation '''
    TAG_NAME = 'validationRules'
    PACKAGE_NAME = 'ValidationRule'
    ID_ATTRIBUTE = 'fullName'


class WebLink(CompoundMetadataType):
    ''' Web Link Class Implementation '''
    TAG_NAME = 'webLinks'
    PACKAGE_NAME = 'WebLink'
    ID_ATTRIBUTE = 'fullName'


# Extra Classes


class ArticleTypeChannelDisplay(ChildMetadataType):
    ''' ArticleTypeChannelDisplay Field Class Implementation '''
    TAG_NAME = 'articleTypeChannelDisplay'

    class ArticleTypeTemplate(ChildMetadataType):
        ''' ArticleTypeChannelDisplay - ArticleTypeTemplate
            Class Implementation '''
        TAG_NAME = 'articleTypeTemplates'
        ID_ATTRIBUTE = 'channel'

    CHILD_OBJECTS = {'articleTypeTemplates': ArticleTypeTemplate}


class NameField(ChildMetadataType):
    ''' Name Field Class Implementation '''
    TAG_NAME = 'nameField'
    ID_ATTRIBUTE = 'label'


# Main Class


class Object(MetadataType):
    ''' Custom Object Class Implementation '''
    TAG_NAME = 'CustomObject'
    PACKAGE_NAME = 'CustomObject'
    CHILD_OBJECTS = get_child_objects(__name__)
    MINIMUM_VALUES = set()
    FOLDER_NAME = 'objects'
    EXTENSION_NAME = 'object'
    CHILD_SEPARATOR = '.'

    def _add_minimum_values(self, news, builders):
        ''' Add minimum values to the news dictionary '''
        for key, value in getattr(self, CustomField.TAG_NAME, {}).items():
            if (hasattr(value, 'type') and getattr(value, 'type') == 'MasterDetail'):
                isAdded = False
                for keyValue, itemsValue in getattr(self, CustomField.TAG_NAME).items():
                    if keyValue == key:
                        isAdded = True
                if not isAdded:
                    if f'{CustomField.TAG_NAME}' not in news:
                        news[f'{CustomField.TAG_NAME}'] = set()
                    news[f'{CustomField.TAG_NAME}'].add(value)
                    self._added_values.add(value)
        super()._add_minimum_values(news, builders)

    def downcast(self):
        if (self._apiname.endswith('__c') and
                CustomSetting.CUSTOMSETTING_TAG in self.__dict__):
            self.__class__ = CustomSetting
        elif self._apiname.endswith('__c'):
            self.__class__ = CustomObject
        elif self._apiname.endswith('__x'):
            self.__class__ = ExternalObject
        elif self._apiname.endswith('__b'):
            self.__class__ = BigObject
        elif self._apiname.endswith('__mdt'):
            self.__class__ = CustomMetadataType
        elif self._apiname.endswith('__kav'):
            self.__class__ = ArticleType
        else:
            self.__class__ = StandardObject

    def get_display_name(self):
        return f'CustomObject-{self.__class__.__name__}'


class StandardObject(Object):
    MINIMUM_VALUES = set()

class CustomObject(Object):
    MINIMUM_VALUES = { NameField.TAG_NAME, 'searchLayouts', 'deploymentStatus', 'label', 'pluralLabel', 'sharingModel' }

class CustomSetting(Object):
    CUSTOMSETTING_TAG = 'customSettingsType'
    MINIMUM_VALUES = { 'label', CUSTOMSETTING_TAG }

class ExternalObject(Object):
    MINIMUM_VALUES = { 'deploymentStatus', 'label', 'pluralLabel', 'externalDataSource' }

class BigObject(Object):
    MINIMUM_VALUES = { 'deploymentStatus', 'label', 'pluralLabel' }

class CustomMetadataType(Object):
    MINIMUM_VALUES = { 'label', 'pluralLabel' }

class ArticleType(Object):
    MINIMUM_VALUES = { 'deploymentStatus', 'label', 'pluralLabel' }
