''' Reporter Module '''

from colorama import Fore, Style


def get_tree_string(changes):
    ''' Returns a String with a tree view of all the changes of a builder '''
    output = f'{Style.DIM}'
    for package_name, values in changes.items():
        added = values['A'] if 'A' in values else set()

        modified = values['M'] if 'M' in values else set()
        erased = values['D'] if 'D' in values else set()
        output += get_package_differences(package_name, added,
                                          modified, erased)
    return output


def get_package_differences(child_xml_name, added, modified, erased):
    ''' Returns additions, modifications and deletions
        from a passed package '''
    if added or modified or erased:
        indent = ' ' * 3

        added_string = __difference_line(f'Added ({len(added)})', added)
        modified_string = __difference_line(f'Modified ({len(modified)})',
                                            modified)
        erased_string = __difference_line(f'Erased ({len(erased)})', erased)
        return(f'{indent}▶︎ {Fore.GREEN}{child_xml_name}{Fore.RESET}:\n'
               f'{added_string}{modified_string}{erased_string}')


def __difference_line(name, values):
    ''' Returns a formated string with the Difference type and values '''
    if values:
        indent = ' ' * 6
        return (f'{indent}► {Fore.YELLOW}{name}{Fore.RESET}:\n'
                f'{__difference_item(values)}')
    return ''


def __difference_item(values):
    ''' Returns a string with all the differences of a child element '''
    indent = ' ' * 9

    if isinstance(values, set):
        return '\n'.join(
            [f'{indent}▸ {Fore.LIGHTMAGENTA_EX}{value}{Fore.RESET}'
             for value in values]) + '\n'

    output = ''
    for apiname, child_objects in values.items():
        output += f'{get_apiname(apiname)}\n'
        for child_object, child_values in child_objects.items():
            output += child_differences(child_object, child_values['A'],
                                        child_values['M'], child_values['D'])
    return output


def get_apiname(apiname):
    ''' Print a warning message '''
    indent = ' ' * 9
    return f'{indent}▸ {Fore.LIGHTMAGENTA_EX}{apiname} {Fore.RESET}'


def child_differences(child_xml_name, added, modified, erased):
    ''' Pretty print differences '''
    if added or modified or erased:
        added_string = __difference_line_item(f'Added ({len(added)})', added)
        modified_string = __difference_line_item(f'Modified ({len(modified)})',
                                                 modified)
        erased_string = __difference_line_item(f'Erased ({len(erased)})',
                                               erased)
        indent = ' ' * 12
        return(f'{Style.DIM}{indent}▹ {Fore.MAGENTA}{child_xml_name}'
               f'{Fore.RESET}:\n{added_string}{modified_string}'
               f'{erased_string}')
    return ''


def __difference_line_item(name, values):
    ''' Returns a formated string with the Difference type and values '''
    if values:
        indent = ' ' * 15
        return f'{indent}- {Fore.YELLOW}{name}{Fore.RESET}: {values}\n'
    return ''
