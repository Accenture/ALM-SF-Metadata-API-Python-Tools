''' Utils module '''
import os
import re
import json
import shutil
import subprocess

from colorama import Fore, Style, init
from lxml import etree

import __main__
from modules.utils.exceptions import NotCreatedDescribeLog
from modules.utils.models import MetadataType, MetadataTypeFromJSON

init(autoreset=True)

INFO_TAG = f'{Fore.YELLOW}[INFO]{Fore.RESET}'
ERROR_TAG = f'{Fore.RED}[ERROR]{Fore.RESET}'
WARNING_TAG = f'{Fore.MAGENTA}[WARNING]{Fore.RESET}'

FATAL_LINE = f'{Fore.RED}[FATAL]'
SUCCESS_LINE = f'{Fore.GREEN}[SUCCESS]'
WARNING_LINE = f'{Fore.MAGENTA}[WARNING]'

API_VERSION = '44.0'
DELTA_FOLDER = 'srcToDeploy'
SOURCE_FOLDER = 'src'
TEMPLATE_FILE = "expansionPanels.html"

PWD = os.path.dirname(os.path.realpath(__main__.__file__))

FOLDER_PATTERN = ['│   ', '    ']
FILE_PATTERN = ['├─ ', '└─ ']

ENV_PROJECT_ID = 'gitMergeRequestTargetProjectId'
ENV_GITLAB_ACCESS_TOKEN = 'GITLAB_ACCESS_TOKEN'


def write_file(folder, filename, content, print_log=False):
    ''' Writes into a file, creating the folders if not exists '''
    if print_log:
        print(f'\t- Writting \'{filename}\' in \'{folder}\''
              f'{Style.NORMAL}')
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(f'{folder}/{filename}', 'w', encoding='utf-8') as output_file:
        output_file.write(content)


def call_subprocess(command, verbose=True):
    ''' Calls subprocess, returns output and return code,
        if verbose flag is active it will print the output '''
    try:
        stdout = subprocess.check_output(command, stderr=subprocess.STDOUT,
                                         shell=True).decode('utf-8')
        if verbose:
            print_output(f'{Style.DIM}{stdout}{Style.NORMAL}')
        return stdout, 0
    except subprocess.CalledProcessError as exc:
        output = exc.output.decode('utf-8')
        returncode = exc.returncode
        if verbose:
            print(f'{ERROR_TAG} Subprocess returned non-zero exit '
                  f'status {returncode}')
            print_output(output, color=Fore.RED)
        return output, returncode


def pprint_xml(xml, declaration=True):
    ''' Pretty print the passed xml '''
    return etree.tostring(xml, pretty_print=True,
                          encoding='utf-8',
                          xml_declaration=declaration).decode('utf-8')


def print_apiname(apiname, package_name):
    ''' Print a warning message '''
    indent = ' ' * 3
    print(f'{Style.DIM}{indent}▶︎ {Fore.GREEN}[{package_name}] {Fore.MAGENTA}'
          f'{apiname} {Fore.RESET}')


def print_differences(child_xml_name, added, modified, erased):
    ''' Pretty print differences '''
    if added or modified or erased:
        added_string = __difference_line(f'Added ({len(added)})',
                                         sorted(added))
        modified_string = __difference_line(f'Modified ({len(modified)})',
                                            sorted(modified))
        erased_string = __difference_line(f'Erased ({len(erased)})',
                                          sorted(erased))
        indent = ' ' * 6
        print(f'{Style.DIM}{indent}► {Fore.MAGENTA}{child_xml_name}'
              f'{Fore.RESET}:\n{added_string}{modified_string}{erased_string}',
              end='')


def print_warning(message):
    ''' Print a warning message '''
    indent = ' ' * 6
    print(f'{Style.DIM}{indent}⚠ {Fore.MAGENTA}{message}{Fore.RESET}')


def __difference_line(name, values):
    ''' Returns a formated string with the Difference type and values '''
    if values:
        indent = ' ' * 9
        return f'{indent}▹ {Fore.YELLOW}{name}{Fore.RESET}: {values}\n'
    return ''


def print_output(output, color='', tab_level=1):
    ''' Prints output in the color passed '''
    formated = '\t' * tab_level + output.replace('\n', '\n' + '\t' * tab_level)
    print(f'{color}{formated}{Fore.RESET}')


def truncate_string(value, size, fill=False):
    ''' Truncates a tring to passed size '''
    string_value = str(value)
    if len(string_value) > size:
        return string_value[:size].strip() + (string_value[size:] and '...')
    if fill:
        return string_value.ljust(size, ' ')
    return string_value


def copy_parents(src, dest_folder, dir_offset=0):
    ''' Copies src tree into dest, offset (optional) omits n
        folders of the src path'''
    if src.endswith('-meta.xml'):  # if its meta file, erase meta part
        src = src[:-len('-meta.xml')]
    prev_offset = (0 if dir_offset == 0 else
                   src.replace('/', '%', dir_offset - 1).find('/') + 1)
    post_offset = src.rfind('/')

    src_dirs = '' if post_offset == -1 else src[prev_offset:post_offset]
    src_filename = src[post_offset + 1:]

    os.makedirs(f'{dest_folder}/{src_dirs}', exist_ok=True)

    dest_file_path = f'{dest_folder}/{src_dirs}/{src_filename}'
    copy_file(src, dest_file_path, True)
    copy_file(f'{src}-meta.xml', f'{dest_file_path}-meta.xml', True)


def copy_file(src, dest, handle_errors):
    ''' Copy a file from source to dest, if handle flag is activated,
        an an exception is launch while trying to copy it will not fail '''
    try:
        shutil.copy(src, dest)
    except Exception as exception:  # noqa # pylint: disable=W0703,W0612
        if not handle_errors:
            raise exception
        else:
            pass  # TODO log verbose level


def get_xml_names(filepath):
    ''' Extracts the xml names from a describe '''
    if not os.path.isfile(filepath):
        raise NotCreatedDescribeLog(filepath)
    
    with open(filepath, 'r') as file:
        try:
            data    = json.load( file )
            isJSON  = True
        except:
            data    = file.read()
            isJSON  = False

    if isJSON:
        dictionary = getXmlNamesFromJSON( data )
    else:
        dictionary = getXmlNamesFromLog( data )

    return dictionary


def getXmlNamesFromJSON(data):

    dictionary = {}

    for metadataInfo in data[ 'metadataObjects' ]:
        inFolder        = metadataInfo[ 'inFolder' ]
        hasMetadata     = metadataInfo[ 'metaFile' ]
        childObjects    = metadataInfo[ 'childXmlNames' ] if 'childXmlNames' in metadataInfo else []
        suffix          = metadataInfo[ 'suffix' ] if 'suffix' in metadataInfo else ''
        xmlName         = metadataInfo[ 'xmlName' ]
        dirName         = metadataInfo[ 'directoryName' ]
        dictKey         = dirName

        if 'territory2Models' == dirName and 'territory2Model' != suffix:
            dictKey = suffix
        dictionary[ dictKey ] = MetadataTypeFromJSON( xmlName, dirName, suffix, hasMetadata, inFolder, childObjects )

    return dictionary


def getXmlNamesFromLog( data ):

    regex_string = (r'\*+\nXMLName: ([a-zA-Z0-9]+)\nDirName: ([a-zA-Z0-9]+)\nSuffix:'
                    r' ([a-zA-Z0-9]+)\nHasMetaFile: ([a-zA-Z]+)\nInFolder:'
                    r' ([a-zA-Z]+)\nChildObjects: (?:([a-zA-Z,]+),|)\*+')
    
    xml_names   = re.findall(regex_string, data, re.MULTILINE)
    dictionary  = dict()

    for (xml_name, dir_name, suffix, has_metadata,
         in_folder, child_objects) in xml_names:
        in_folder = castToBoolean( in_folder )
        has_metadata = castToBoolean( has_metadata )
        dict_key = dir_name
        if 'territory2Models' == dir_name and 'territory2Model' != suffix:
            dict_key = suffix
        dictionary[dict_key] = MetadataType(xml_name, dir_name, suffix,
                                            has_metadata, in_folder,
                                            child_objects)
    return dictionary


def castToBoolean( value ):
    boolValue = False
    if 'true' == value:
        boolValue = True
    return boolValue

def tree(path, do_output=True, print_hidden=False, max_depth=100, margin=1):
    """Print file and directory tree starting at path.

    By default, it prints upto a depth of 100 and doesn't print hidden files,
    ie. files whose name begin with a '.'. It can be modified to only return
    the count of files and directories, and not print anything.

    Returns the tuple of number of files and number of directories
    """

    def _tree(path, depth, margin, output):
        file_count, directory_count = 0, 0
        files = sorted((os.path.join(path, filename)
                        for filename in os.listdir(path)
                        if print_hidden or not filename.startswith('.')),
                       key=lambda s: s.lower())

        files_count = len(files)

        for i, filepath in enumerate(files, start=1):
            # Print current file, based on previously gathered info
            if do_output:
                folder_lines = ''.join(FOLDER_PATTERN[folder]
                                       for folder in parent_folders)
                corner = FILE_PATTERN[i == files_count]
                file_name = os.path.basename(filepath)
                margin_str = '\t' * margin
                output += f'{margin_str}{folder_lines}{corner}{file_name}\n'

            # Recurse if we find a new subdirectory
            if os.path.isdir(filepath) and depth < max_depth:

                # Append whether current directory is last in current list
                parent_folders.append(i == files_count)

                # Print subdirectory and get numbers
                output, subdir_file_count, subdir_directory_count = \
                    _tree(os.path.join(filepath), depth + 1, margin, output)

                # Back in current directory, remove the newly added directory
                parent_folders.pop()

                # Update counters
                file_count += subdir_file_count
                directory_count += subdir_directory_count + 1

            elif os.path.isdir(filepath):
                directory_count += 1

            else:
                file_count += 1

        return output, file_count, directory_count

    parent_folders = []
    output, file_count, directory_count = _tree(path, 1, margin, '')

    output += f'\n\t{file_count} files, {directory_count} directories\n'

    print(f'{Style.DIM}{output}{Style.NORMAL}')


def remove_file(file_path):
    ''' Removes file if exists '''
    if os.path.exists(file_path):
        os.remove(file_path)


def check_exist(path):
    ''' Detects if a file exists '''
    if not os.path.exists(path):
        print(f"{INFO_TAG} The path {path} didn't exists.")
        return False
    return True


def print_key_value_list(top_message, items):
    ''' Prints a key value list '''
    message = f'{top_message}\n'
    for key, value in items:
        message += f'{key_value_list(key, value)}\n'
    print(message)


def key_value_list(key, value):
    ''' Returns a pretty formated list, with key in cyan '''
    return f'\t- {Fore.CYAN}{key}{Fore.RESET}: {value}'


def get_first_set_value(values):
    ''' Extracts the first value of the passed set '''
    value = values.pop()
    values.add(value)
    return value
