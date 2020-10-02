''' Delta Builder '''
import os
import re
import shutil

import jinja2
from jinja2.exceptions import TemplateNotFound

from modules.git import checkout, fetch, prepare_and_merge
from modules.parser import IMPLEMENTED_CHILD, parse_file
from modules.utils import (ERROR_TAG, INFO_TAG, PWD, TEMPLATE_FILE,
                           WARNING_TAG, call_subprocess, check_exist,
                           copy_parents, get_first_set_value, get_xml_names,
                           pprint_xml, remove_file, write_file)
from modules.utils.exceptions import (InvalidPath, NoDifferencesException,
                                      NotControlledFoldersFound)
from modules.utils.models import ChangeType
from modules.utils.reporter import get_tree_string


def merge_delta(source, target, remote, do_fetch, reset, delta_folder,
                source_folder, api_version, do_breakdown, print_tree,
                describepath='describe.log'):
    ''' Builds delta package in the destination folder '''
    print(f'{INFO_TAG} Clean up target folder \'{delta_folder}\'')
    shutil.rmtree(delta_folder, ignore_errors=True, onerror=None)
    os.makedirs(delta_folder)

    print(f'{INFO_TAG} Extracting metadata types from \'{describepath}\'')
    xml_names = get_xml_names(describepath)

    print(f'{INFO_TAG} Preparing to merge \'{source}\' into \'{target}\'')
    prepare_and_merge(source, target, remote, do_fetch, reset)

    print(f'{INFO_TAG} Getting differences')
    differences = get_differences(source_folder, 'HEAD', 'HEAD~1')

    print(f'{INFO_TAG} Handling a total of {len(differences)} differences')
    builder = __handle_differences(differences, delta_folder, api_version,
                                   xml_names, source_folder, do_breakdown,
                                   'HEAD', 'HEAD~1')

    print(f'\n{INFO_TAG} Generating Packages')
    builder.build_xmls()

    print(f'\n{INFO_TAG} Generated Delta')
    builder.build_tree(print_tree)
    builder.build_html(differences)

    print()
    if builder.get_errors():
        raise NotControlledFoldersFound(builder.get_errors())


def build_delta(source_ref, target_ref, remote, do_fetch, delta_folder,
                source_folder, api_version, do_breakdown, print_tree,
                describepath='describe.log'):
    ''' Builds delta package in the destination folder '''
    print(f'{INFO_TAG} Clean up target folder \'{delta_folder}\'')
    shutil.rmtree(delta_folder, ignore_errors=True, onerror=None)
    os.makedirs(delta_folder)

    print(f'{INFO_TAG} Extracting metadata types from \'{describepath}\'')
    xml_names = get_xml_names(describepath)

    if do_fetch:
        print(f'{INFO_TAG} Fetching from \'{remote}\'')
        fetch(remote)
    else:
        print(f'{INFO_TAG} Not fetching, using current local status')

    print(f'{INFO_TAG} Checking out source ref \'{source_ref}\'')
    checkout(source_ref, remote, reset=False)

    print(f'{INFO_TAG} Getting differences')
    differences = get_differences(source_folder, source_ref, target_ref)

    print(f'{INFO_TAG} Handling a total of {len(differences)} differences')
    builder = __handle_differences(differences, delta_folder, api_version,
                                   xml_names, source_folder, do_breakdown,
                                   source_ref, target_ref)

    print(f'\n{INFO_TAG} Generating Packages')
    builder.build_xmls()

    print(f'\n{INFO_TAG} Generated Delta')
    builder.build_tree(print_tree)
    builder.build_html(differences)

    print()
    if builder.get_errors():
        raise NotControlledFoldersFound(builder.get_errors())


def get_differences(source_folder, source, target):
    ''' Extract the differences between two references '''
    diff_command = f'git diff --name-status {target} {source}'
    output, _ = call_subprocess(diff_command)

    regex_string = r'([A-Z0-9]+)\t*({}\/[a-zA-Z0-9]+\/.+)'.format(source_folder)
    differences = re.findall(regex_string, output)

    if not differences:
        raise NoDifferencesException(source_folder)
    return differences


# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# Differences Handlers


def __handle_differences(differences, delta_folder, api_version, xml_names,
                         source_folder, do_breakdown, source_ref, target_ref):
    ''' Handles a list of differences copying the files into the
        delta folder '''
    builders = Builders(delta_folder, api_version, xml_names)
    for status, filename in differences:

        folder, apiname = splitFolderApiname( source_folder, filename )
        xml_definition = xml_names.get(folder, None)
        if not xml_definition:
            print( f'Warning : {folder} not in describe' )
            continue

        if status.startswith('R'):
            __handle_rename(differences, filename)
            continue
        
        if filename.startswith(f'{source_folder}/aura/') or filename.startswith(f'{source_folder}/lwc/'):
            __handle_aura_folder(source_folder, filename, delta_folder, builders)

        elif filename.startswith(f'{source_folder}/territory2Models/'):
            __handle_territoryModels_folder(source_folder, filename, delta_folder, builders, status)

        elif status == 'A':
            __handle_creation(source_folder, filename, delta_folder, builders, xml_names)
        elif status == 'M':
            __handle_modification(source_folder, filename, delta_folder,
                                  builders, xml_names, do_breakdown,
                                  source_ref, target_ref)
        elif status == 'D':
            __handle_deletion(filename, builders, source_folder, xml_names)
    return builders

def __handle_creation(source_folder, filename, delta_folder, builders, xml_names):
    ''' Method for handling creation '''
    folder, apiname = splitFolderApiname( source_folder, filename )
    xml_definition = xml_names.get(folder, None)

    if '/' in apiname:
        #folderMeta = apiname.split( '/' )[ 0 ]
        #builders.add_change(folder, folderMeta, ChangeType.MODIFICATION)
        copy_parents(filename, delta_folder, 1)
        builders.add_change(folder, apiname, ChangeType.MODIFICATION)
    elif '-meta.xml' in apiname and xml_definition and getattr( xml_definition, "in_folder" ):
        apiname = apiname[ : -len( '-meta.xml' ) ]
        copy_parents(filename, delta_folder, 1)
        builders.add_change(folder, apiname, ChangeType.CREATION)
    else:
        copy_parents(filename, delta_folder, 1)
        builders.add_change(folder, apiname, ChangeType.CREATION)

def __handle_modification(source_folder, filename, delta_folder, builders,
                          xml_names, do_breakdown, source_ref, target_ref):
    ''' Method for handling modification '''
    folder, apiname = splitFolderApiname( source_folder, filename )
    xml_definition = xml_names.get(folder, None)
    # Check if modified file is an implemented compound object
    
    print( f'filename {filename}' )
    print( do_breakdown )
    print( xml_definition )
    print( xml_definition.child_objects )
    print( xml_definition.xml_name )

    if (do_breakdown and xml_definition and xml_definition.xml_name in IMPLEMENTED_CHILD):
        __extract_differences(delta_folder, filename, xml_definition, builders,
                              source_ref, target_ref)
    elif '/' in apiname:
        folderMeta  = apiname.split( '/' )[ 0 ]
        copy_parents(filename, delta_folder, 1)
        builders.add_change(folder, apiname, ChangeType.MODIFICATION)
    elif '-meta.xml' in apiname and xml_definition and getattr( xml_definition, "in_folder" ):
        apiname = apiname[ : -len( '-meta.xml' ) ]
        copy_parents(filename, delta_folder, 1)
        builders.add_change(folder, apiname, ChangeType.MODIFICATION)
    else:
        copy_parents(filename, delta_folder, 1)
        builders.add_change(folder, apiname, ChangeType.MODIFICATION)


def __handle_deletion(filename, builder, source_folder, xml_names):
    ''' Method for handling deletions '''
    folder, apiname = splitFolderApiname( source_folder, filename )
    xml_definition = xml_names.get(folder, None)
    if '-meta.xml' in apiname and xml_definition and getattr( xml_definition, "in_folder" ):
        apiname = apiname[ : -len( '-meta.xml' ) ]
    builder.add_change(folder, apiname, ChangeType.DELETION)


def __handle_rename(differences, filename):
    ''' Method for handling renames '''
    source, target = filename.split('\t')
    differences.append(('D', source))
    differences.append(('A', target))


def __handle_aura_folder(source_folder, filename, delta_folder, builders):
    ''' Handles the specific case of changes in an aura folder when
        it is necessary to add all the aura folder '''
    folder, apiname = get_folder_apiname(source_folder, filename)
    aura_folder_path = f'{source_folder}/{folder}/{apiname}'
    if os.path.isdir(aura_folder_path):  # modified or created aura
        builders.add_change(folder, apiname, ChangeType.MODIFICATION)
        # build dest path (add dest folder cut 'src' folder)
        dest = f'{delta_folder}/{folder}/{apiname}'
        try:
            shutil.copytree(aura_folder_path, dest)
        except FileExistsError:  # if already exits, dont do anything
            pass
    else:  # erased aura
        builders.add_change(folder, apiname, ChangeType.DELETION)


def __handle_territoryModels_folder(source_folder, filename, delta_folder, builders, status):
    metaFolder = 'territory2Models'
    modelFolder, apiname = splitFolderApiname( f'{source_folder}/{metaFolder}', filename )
    if 'rules/' in apiname:
        ruleFile        = apiname.split( 'rules/' )[ 1 ]
        metaFolderRules = 'territory2Rule'
        if 'D' == status:
            builders.add_change(metaFolderRules, f'{modelFolder}.{ruleFile}', ChangeType.DELETION)
        else:
            copy_parents(filename, delta_folder, 1)
            builders.add_change(metaFolderRules, f'{modelFolder}.{ruleFile}', ChangeType.MODIFICATION)
    elif 'territories/' in apiname:
        territoryFile           = apiname.split( 'territories/' )[ 1 ]
        metaFolderTerritories   = 'territory2'
        if 'D' == status:
            builders.add_change(metaFolderTerritories, f'{modelFolder}.{territoryFile}', ChangeType.DELETION)
        else:
            copy_parents(filename, delta_folder, 1)
            builders.add_change(metaFolderTerritories, f'{modelFolder}.{territoryFile}', ChangeType.MODIFICATION)
    else:
        if 'D' == status:
            builders.add_change(metaFolder, apiname, ChangeType.DELETION)
        else:
            copy_parents(filename, delta_folder, 1)
            builders.add_change(metaFolder, apiname, ChangeType.MODIFICATION)

# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

def splitFolderApiname( source_folder, filename ):
    filenameSplit = filename[len(source_folder) + 1:].split('/')
    if len( filename ) > 2:
        filenameSplit = [ filenameSplit[ 0 ], "/".join( filenameSplit[ 1: ] ) ]
    return filenameSplit

def get_folder_apiname(source_folder, filename):
    ''' Extracts the apiname and the source folder of passed file '''
    filename = filename[len(source_folder) + 1:]

    filename = (filename[:filename.rfind('/')] if filename.count('/') > 1
                else filename)

    return filename.split('/')


def __extract_differences(delta_folder, filename, xml_name, builders,
                          source_ref, target_ref):
    ''' Extracts the differences between a file and its previous version '''
    new = parse_file(filename, xml_name, source_ref)
    old = parse_file(filename, xml_name, target_ref)

    differences = old.compare(new, builders)

    if differences:
        differences.to_file(delta_folder)
        differences.to_builders(builders)


def get_xml_dict(treedict):
    ''' Build a dict with xml as a value '''
    snippet_dict = {}
    for name, value in treedict.items():
        for _, data_dict in value.items():
            if isinstance(data_dict, dict):
                iterate_dicts(data_dict, snippet_dict, name)
    return snippet_dict

# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*


def iterate_dicts(data_dict, dct, name):
    '''Auxiliar method to iterate over nested dicts '''
    for data_dict_name, data_dict_values in data_dict.items():
        for _, attr_dicts in data_dict_values.items():
            for _, attrs_value in attr_dicts.items():
                for sets_value in attrs_value:
                    name_id = get_unique_name(name,
                                              data_dict_name,
                                              sets_value)
                    add_to_dict(dct, name_id, sets_value)


def add_to_dict(dictionary, key, value):
    '''Method to add records on a specific dict '''
    dictionary[key] = pprint_xml(value.get_xml(), False)


def get_unique_name(mdt_type, mtd_name, mdt_value):
    ''' Create unique name for keys in dicts '''
    return f"{mdt_type}.{mtd_name}.{mdt_value._apiname}"


class Builders:
    ''' Wrapper containing the destruvctive and constructive buiders '''
    def __init__(self, delta_folder, api_version, xml_names):
        self.tree = {}
        self.errors = set()
        self.xml_names = xml_names
        self.constructive = PackageBuilder(delta_folder, api_version,
                                           xml_names)
        self.destructive = DestructiveChangesBuilder(delta_folder,
                                                     api_version, xml_names)

    def add_change(self, folder, apiname, change_type, no_tree=False):
        ''' Adds change to the constructive builder '''
        if apiname.endswith('-meta.xml'):
            return

        if not no_tree:
            self.__add_to_tree(folder, apiname, change_type)

        if change_type == ChangeType.DELETION:
            self.destructive.add_change(folder, apiname)
        else:
            self.constructive.add_change(folder, apiname)

    def add_constructive_changes(self, apinames):
        ''' Adds changes to the constructive builder '''
        self.constructive.add_changes(apinames)

    def add_child_differences(self, package_name, apiname, diffs):
        ''' Adds child differences to the tree '''
        if package_name not in self.tree:
            self.tree[package_name] = dict()
        if ChangeType.MODIFICATION.value not in self.tree[package_name]:
            self.tree[package_name][ChangeType.MODIFICATION.value] = dict()
        self.tree[package_name][ChangeType.MODIFICATION.value][apiname] = diffs

    def add_destructive_changes(self, apinames):
        ''' Adds changes to the destructive builder '''
        self.destructive.add_changes(apinames)

    def build_xmls(self):
        ''' Builds XML for the builders '''
        self.constructive.build_xml()
        if self.destructive.has_changes():
            self.destructive.build_xml()

    def get_tree(self):
        ''' Gets tree builder'''
        return self.tree

    def build_tree(self, print_tree, report_folder='artifacts_folder'):
        ''' Builds the tree string '''
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        escaped_tree = ansi_escape.sub('', get_tree_string(self.tree))
        write_file(report_folder, 'mergerReport.txt', escaped_tree,
                   print_log=True)
        if print_tree:
            print(get_tree_string(self.tree))

    def add_error(self, error_message):
        ''' Adds an error to the error list '''
        self.errors.add(error_message)

    def get_errors(self):
        ''' Builds XML for the builders '''
        self.errors.update(self.constructive.errors)
        self.errors.update(self.destructive.errors)
        return self.errors

    def __add_to_tree(self, folder, apiname, change_type):
        ''' Adds simple change to the tree '''
        if folder not in self.xml_names:
            self.add_error(folder)
            return
        package_name = self.xml_names[folder].xml_name
        if package_name not in self.tree:
            self.tree[package_name] = dict()
        if change_type.value not in self.tree[package_name]:
            self.tree[package_name][change_type.value] = set()
        self.tree[package_name][change_type.value].add(apiname)

    def build_html(self, differences, report_folder='artifacts_folder'):
        ''' Builds html manifest for the generated delta package '''
        snippet_dict = get_xml_dict(self.tree)
        template_path = f"{PWD}/resources/templates/"
        if not check_exist(template_path):
            raise InvalidPath(template_path)
        try:
            loader = jinja2.FileSystemLoader(searchpath=(f'{PWD}/resources/'
                                                         f'templates/'))
            template_env = jinja2.Environment(loader=loader)
            template = template_env.get_template(TEMPLATE_FILE)
            report_file = template.render(treedict=self.tree.items(),
                                          len_differences=len(differences),
                                          len_treedict=len(self.tree),
                                          snippet_dict=snippet_dict)
            write_file(report_folder, 'mergerReport.html', report_file,
                       print_log=True)
        except TemplateNotFound as exc:
            print(f"{ERROR_TAG} Cannot found {exc} in {PWD}/resources/" +
                  "templates/")


class PackageBuilder:
    ''' Destructive changes builder '''
    PACKAGE_NAME = 'package.xml'

    def __init__(self, delta_folder, api_version, xml_names):
        self.__tokens = {}
        self.errors = set()
        self.delta_folder = delta_folder
        self.api_version = api_version
        self.xml_names = xml_names

    def add_changes(self, values):
        ''' Adds a list of changes into the a list '''
        xml_name = get_first_set_value(values).PACKAGE_NAME
        if xml_name not in self.__tokens:
            self.__tokens[xml_name] = set()
        self.__tokens[xml_name].update(values)

    def add_change(self, folder, apiname):
        ''' Adds a destructive change into the list '''
        if folder not in self.xml_names:
            self.errors.add(folder)
            print(f'{WARNING_TAG} Detected changes in non-controlled folder '
                  f'\'{folder}\'')
        else:
            xml_name = self.xml_names[folder].xml_name
            if not apiname.endswith('-meta.xml'):
                if xml_name not in self.__tokens:
                    self.__tokens[xml_name] = set()
                if '.' in apiname:  # TODO try to do this in a better way
                    self.__tokens[xml_name].add(apiname[:apiname.rfind('.')])
                else:
                    self.__tokens[xml_name].add(apiname)

    def build_xml(self):
        ''' Generates the xml from the changes detected '''
        file_path = f'{self.delta_folder}/{self.PACKAGE_NAME}'
        remove_file(file_path)
        types_string = ''
        for xml_name, apinames in sorted(self.__tokens.items()):
            types_string += self._generate_type_string(xml_name, apinames)
        package = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                   '<Package xmlns="http://soap.sforce.com'
                   '/2006/04/metadata">\n')
        package += types_string
        package += (f'\t<version>{self.api_version}</version>\n'
                    '</Package>\n')
        write_file(self.delta_folder, self.PACKAGE_NAME, package,
                   print_log=True)

    def has_changes(self):
        ''' Return true if there are changes '''
        return bool(self.__tokens)

    @staticmethod
    def _generate_type_string(xml_name, members):
        ''' Generates a type string with a wildcard as the members '''
        members_string = ''.join([f'\t\t<members>{member}</members>\n'
                                  for member in sorted(members)])
        return (f'\t<types>\n'
                f'{members_string}'
                f'\t\t<name>{xml_name}</name>\n'
                f'\t</types>\n')

    def __repr__(self):
        return f'<{self.__class__.__name__}, {self.__tokens}>'


class DestructiveChangesBuilder(PackageBuilder):
    ''' Destructive changes builder '''
    PACKAGE_NAME = 'preDestructiveChanges.xml'
