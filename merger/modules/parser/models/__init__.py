''' Main Module Containing the abstract classes '''
import collections
import inspect
import re
import sys

from colorama import Fore
from lxml import etree

from modules.utils import (WARNING_LINE, print_apiname, print_differences,
                           print_warning, write_file)
from modules.utils.exceptions import (MissingRequiredAttribute,
                                      NotEnoughParams, TooManyParams)
from modules.utils.models import ChangeType, OutputType

NS_MAP = {'ns': 'http://soap.sforce.com/2006/04/metadata'}
NS_MAP2 = {None: 'http://soap.sforce.com/2006/04/metadata'}


class MetadataType:
    ''' Abstract Metadata Type '''
    TAG_NAME = ''
    PACKAGE_NAME = ''
    CHILD_OBJECTS = {}
    FOLDER_NAME = ''
    EXTENSION_NAME = ''
    HAS_PREFIX = True
    CHILD_SEPARATOR = ''
    MINIMUM_VALUES = {}

    ATTRIBUTES_LOCATION = '_attributes'

    def __init__(self, apiname, filestring=None, filepath=None,
                 _differences=None, _composed=True, **kwargs):
        # print(apiname)
        if '/' in apiname:  # TODO try to do this in a better way
            self._apiname = apiname[apiname.rfind('/') + 1:apiname.rfind('.')]
        else:
            self._apiname = apiname

        self._prefix = (f'{self._apiname}{self.CHILD_SEPARATOR}'
                        if self.HAS_PREFIX else '')
        self._added_values = set()
        self._only_composed = _composed
        self._differences = _differences

        if not filestring and not filepath:
            self._apiname = apiname
            self.__dict__.update(kwargs)
        else:
            if filestring and filepath:
                raise TooManyParams()
            if filestring:
                self._xml = etree.fromstring(filestring)
            elif filepath:
                self._xml = etree.parse(filepath)
            else:
                raise NotEnoughParams()

            self.__extract_metadata()
        self.downcast()

        if self.get_display_name().startswith( 'CustomObject-' ):
            if hasattr( self, '_xml' ):
                print( self._apiname )
                print( self.MINIMUM_VALUES )
                for child in self._xml.getchildren():
                    if not isinstance( child, etree._Comment ):
                        if not child.getchildren():
                            child_tag = no_ns(child.tag)
                            self.MINIMUM_VALUES.add( child_tag )
                print( self.MINIMUM_VALUES )

    def __extract_metadata(self):
        ''' Extracts metadata for the current xml '''
        for child in self._xml.getchildren():
            if not isinstance( child, etree._Comment ):
                child_tag = no_ns(child.tag)

                # execute if is a handled child_object
                if child_tag in self.CHILD_OBJECTS:
                    if not hasattr(self, child_tag):
                        setattr(self, child_tag, {})

                    extracted = self.CHILD_OBJECTS[child_tag](child, self._prefix)
                    getattr(self, child_tag)[extracted.name] = extracted

                # execute if is an attribute (no child elements only text)
                elif not child.getchildren():
                    setattr(self, child_tag, Attribute(child))

                # execute if unhandled child object
                else:
                    print(f'{WARNING_LINE} Unsupported Metadata '
                          f'Type {child_tag}')

    def __repr__(self):
        return f'<{self.TAG_NAME}, {self._apiname}>'

    def compare(self, new, builders):
        ''' Returns the differences and builds a destructive change '''
        print_apiname(self._apiname, self.get_display_name())
        differences = self.__extract_differences(self.__dict__, new.__dict__)

        builders.add_child_differences(self.PACKAGE_NAME, self._apiname,
                                       differences)
        news = dict()

        for child_xml_name, values in differences.items():
            erased = values['D']
            modified = values['M']
            added = values['A']

            new_modified = modified.union(added)

            print_differences(child_xml_name, added, modified, erased)

            if new_modified:
                value = get_first_value(new_modified)
                if isinstance(value, Attribute):
                    for modified in new_modified:
                        news[modified.tag_name] = modified
                else:
                    news[child_xml_name] = new_modified

            if erased:
                value = get_first_value(erased)

                if issubclass(value.__class__, CompoundMetadataType):
                    builders.add_destructive_changes(erased)
                else:
                    print_warning(f'Cannot assure removing non-managed child'
                                  f'objects will change anything in Salesforce'
                                  f' maybe manual steps are required')
        if not news:
            print_warning(f'Only destructive changes detected')
            return False

        if self.MINIMUM_VALUES:
            for child_xml_name in news:
                #if (child_xml_name not in self.CHILD_OBJECTS or not issubclass(self.CHILD_OBJECTS[child_xml_name],CompoundMetadataType)):
                if child_xml_name in self.MINIMUM_VALUES:
                    self._add_minimum_values(news, builders)
                    self._only_composed = False
                    break

        return self.__class__(self._apiname, _differences=differences,
                              _composed=self._only_composed, **news)

    def _add_minimum_values(self, news, builders):
        ''' Add minimum values to the news dictionary '''
        missing_attributes = []
        for minimum_value_name in self.MINIMUM_VALUES:
            if minimum_value_name in news:
                pass
            elif hasattr(self, minimum_value_name):
                minimum_value = getattr(self, minimum_value_name)
                if isinstance(minimum_value, Attribute):
                    news[f'zzz_{minimum_value_name}'] = minimum_value
                    self._added_values.add(minimum_value)
                else:
                    news[f'zzz_{minimum_value_name}'] = minimum_value.values()
                    self._added_values.add(minimum_value.values())
            else:
                missing_attributes.append(minimum_value_name)
        if missing_attributes:
            print_warning(f'Missing required attributes '
                          f'{missing_attributes}')
            builders.add_error(f'Missing {len(missing_attributes)} required '
                               f'attributes for {self._apiname} '
                               f'({self.PACKAGE_NAME})')
        if self._added_values:
            print_warning(f'Added required attributes {self._added_values}')

    def __extract_differences(self, self_dic, new_dic):
        ''' Extract the differences between two dictionaries '''
        # Extract differences from attributes with child values
        differences = self.__get_attribute_changes(self_dic, new_dic)

        differences.update(
            {child_object.TAG_NAME: (
                MetadataType.__compare_childs(self_dic, new_dic, tag_name))
             for tag_name, child_object in self.CHILD_OBJECTS.items()})

        return differences

    def __get_attribute_changes(self, self_dic, new_dic):
        ''' Extract changes in attributes '''
        keys_1 = set(self_dic.keys())
        keys_2 = set(new_dic.keys())
        intersect = keys_1.intersection(keys_2)

        added = set()
        modified = set()
        erased = {self_dic[name] for name in keys_1 - intersect
                  if isinstance(self_dic[name], Attribute)}

        for new_s_key in keys_2:
            if isinstance(new_dic[new_s_key], Attribute):
                if new_s_key not in keys_1:
                    added.add(new_dic[new_s_key])
                elif self_dic[new_s_key] != new_dic[new_s_key]:
                    modified.add(new_dic[new_s_key])

        return {self.ATTRIBUTES_LOCATION: {'D': erased, 'M': modified,
                                           'A': added}}

    def to_file(self, delta_folder):
        ''' Writes in a file the object '''
        folder_path = f'{delta_folder}/{self.FOLDER_NAME}'
        file_name = f'{self._apiname}.{self.EXTENSION_NAME}'
        string = etree.tostring(self.serialize(), pretty_print=True,
                                encoding='utf-8',
                                xml_declaration=True).decode('utf-8')
        write_file(folder_path, file_name, string)

    def serialize(self):
        ''' Serializes the object into an xml '''
        element = etree.Element(self.TAG_NAME, nsmap=NS_MAP2)
        added_minimum_values = False
        for tag_name, child_object in self.__dict__.items():
            if tag_name.startswith('_'):
                continue
            if tag_name.startswith('zzz_') and not added_minimum_values:
                added_minimum_values = True
                #element.append(etree.Comment(' === Automatically Added === '))
            if isinstance(child_object,
                          collections.Iterable):  # pylint: disable=E1101
                for child in child_object:
                    element.append(child.get_xml())
            else:
                element.append(child_object.get_xml())

        return element

    def to_builders(self, builders):
        ''' Adds changes to Package XML '''
        if self._only_composed:
            for tag_name, child_object in self.CHILD_OBJECTS.items():
                if issubclass(child_object, CompoundMetadataType):
                    childs = {child for child in getattr(self, tag_name, [])}
                    if childs:
                        builders.add_constructive_changes(childs)
        else:
            builders.add_change(self.FOLDER_NAME, self._apiname,
                                ChangeType.MODIFICATION, no_tree=True)

    @staticmethod
    def __compare_childs(origin, new, tag):
        ''' Compare child elements '''
        origin = origin[tag] if tag in origin else {}
        new = new[tag] if tag in new else {}

        keys_1 = set(origin.keys())
        keys_2 = set(new.keys())

        intersect = keys_1.intersection(keys_2)

        added = {new[name] for name in keys_2 - intersect}
        erased = {origin[name] for name in keys_1 - intersect}

        modified = {new[name] for name in intersect
                    if origin[name] != new[name]}
        return {'D': erased, 'M': modified, 'A': added}

    def downcast(self):
        pass

    def get_display_name(self):
        return self.PACKAGE_NAME


class Attribute:
    ''' Attribute class implementation '''
    def __init__(self, xml):
        self._xml = xml
        self.tag_name = no_ns(xml.tag)
        self.value = xml.text.strip() if xml.text else ''
        self.name = self.tag_name
        self._apiname = self.tag_name

    def __repr__(self):
        return (f'{Fore.BLUE}<{self.tag_name}, {Fore.CYAN}'
                f'{self.value}{Fore.BLUE}>{Fore.RESET}')

    def __hash__(self):
        return hash(self.tag_name)

    def __eq__(self, other):
        return (self.tag_name == other.tag_name
                and self.value == other.value)

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name

    def __le__(self, other):
        return self.name <= other.name

    def __ge__(self, other):
        return self.name >= other.name

    def get_xml(self):
        ''' Return the xml of the attribute '''
        return self._xml


class ChildMetadataType:
    ''' Abstract Metadata Type for Child Objects '''
    TAG_NAME = ''
    PACKAGE_NAME = ''
    ID_ATTRIBUTE = ''
    CHILD_OBJECTS = []

    def __init__(self, xml, name_prefix=''):
        self._xml = xml
        self.__extract_metadata()

        if self.ID_ATTRIBUTE:
            self._apiname = getattr(self, self.ID_ATTRIBUTE, None)
            if not self._apiname:
                print( self.ID_ATTRIBUTE )
                print( dir( self ) )
                raise MissingRequiredAttribute(self.__class__.__name__,
                                               self.ID_ATTRIBUTE)
            self.name = f'{name_prefix}{self._apiname}'
        else:
            self.name = ''

    def __extract_metadata(self):
        ''' Extracts metadata for the current xml '''
        for child in self._xml.getchildren():
            if not isinstance( child, etree._Comment ):
                child_tag = no_ns(child.tag)

                # execute if is a handled child_object
                if child_tag in self.CHILD_OBJECTS:
                    if not hasattr(self, child_tag):
                        setattr(self, child_tag, {})

                    extracted = self.CHILD_OBJECTS[child_tag](child, '')
                    getattr(self, child_tag)[extracted.name] = extracted

                # execute if is an attribute (no child elements only text)
                elif not child.getchildren():
                    if hasattr(self, child_tag):  # list of values with no children
                        already_saved = getattr(self, child_tag)
                        if isinstance(already_saved, set):
                            already_saved.add(child.text)
                        else:
                            # TODO im sure there is a better way to do this
                            new_set = set()
                            new_set.add(already_saved)
                            already_saved = new_set
                        setattr(self, child_tag, already_saved)
                    else:
                        text_value = child.text.strip() if child.text else ''
                        setattr(self, child_tag, text_value)

                # execute if unhandled child object
                else:
                    print(f'{WARNING_LINE} Unsupported Metadata Type {child_tag}')

    def __repr__(self):
        value = ''
        if hasattr( self, '_apiname' ):
            value = (f'{Fore.BLUE}<{Fore.CYAN}'
                f'{self._apiname}{Fore.BLUE}>{Fore.RESET}')
        return value

    def __str__(self):
        return f'{self.name}'

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, value2):
        return not bool(self.differences(value2))

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name

    def __le__(self, other):
        return self.name <= other.name

    def __ge__(self, other):
        return self.name >= other.name

    def serialize(self, output_type):
        ''' Serializes object into the selected output '''
        if output_type == OutputType.XML:
            return self._xml
        message = (f'Output Type {output_type} is not yet available for '
                   f'serialization')
        raise NotImplementedError(message)

    def differences(self, value2):
        ''' Gets the differences between two instances '''
        values1 = self.__dict__
        values2 = value2.__dict__
        missing = set(values1).symmetric_difference(set(values2))
        different = {key for key, value in self.__dict__.items()
                     if not key.startswith('_')
                     and value != values2.get(key, '')}
        return missing.union(different)

    def get_xml(self):
        ''' Returns the xml of the object '''
        return self._xml


class CompoundMetadataType(ChildMetadataType):
    ''' CompoundMetadataType class implementation '''
    def __repr__(self):
        return (f'{Fore.BLUE}<{Fore.CYAN}'
                f'{self._apiname}{Fore.BLUE}>{Fore.RESET}')


class ChildObject(ChildMetadataType):
    ''' Child Object Implementation '''
    def __repr__(self):
        return (f'{Fore.BLUE}<{Fore.CYAN}'
                f'{self._apiname}{Fore.BLUE}>{Fore.RESET}')


def no_ns(tag):
    ''' Erases the namespace of the tag '''
    return re.sub(r'\{.+\}', '', tag)


def get_child_objects(module):
    ''' Return all the Child Classes of the passed module '''
    return {class_.TAG_NAME: class_
            for name, class_ in inspect.getmembers(sys.modules[module],
                                                   inspect.isclass)
            if issubclass(class_, ChildMetadataType)
            and name != ChildMetadataType.__name__
            and name != CompoundMetadataType.__name__
            and name != ChildObject.__name__
            }


def get_first_value(set_object):
    ''' Returns the first value of a set '''
    value = set_object.pop()
    set_object.add(value)
    return value
