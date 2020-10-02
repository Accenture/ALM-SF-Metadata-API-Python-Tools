''' Argparse Module '''
import argparse
import os
import sys

from modules.git.models import PrettyFormat, Version
from modules.utils import (API_VERSION, DELTA_FOLDER, ENV_GITLAB_ACCESS_TOKEN,
                           ENV_PROJECT_ID, SOURCE_FOLDER)
from modules.utils.models import OutputType


def parse_args():
    ''' Parse args '''
    description = ('Merger method that helps and automates the creation of '
                   'deltas and releases for Salesforce Git Bases projects')
    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers(help='commands', dest='option')
    subparsers.required = True

    subparsers.add_parser('version', help='Returns the version of the script')

    merger_help = ('Builds delta package, from the diff between source and '
                   'target branch after merging them')
    __merge_parser(subparsers.add_parser('merge_delta', help=merger_help))

    build_help = ('Builds delta package, from the diff between two specified '
                  'references (commit, tag or branch)')
    __build_parser(subparsers.add_parser('build_delta', help=build_help))

    list_mr_help = ('Lists all the available MR that were targeted to source '
                    'branch and filter those that are already in the target')
    __list_mr(subparsers.add_parser('list_mr', help=list_mr_help))

    list_mc_help = ('Lists all the Merge Commits, can filter to only get the '
                    'merge commits in a current branch')
    __list_mc(subparsers.add_parser('list_mc', help=list_mc_help))

    release_help = ('Creates release branch from a list of MR iids '
                    'merging them into the target branch')
    __release_parser(subparsers.add_parser('create_release',
                                           help=release_help))

    args = parser.parse_args()

    args.remote_specified = ('remote' in args
                             and ('-r' in sys.argv or '--remote' in sys.argv))

    if args.option == 'list_mr' or args.option == 'create_release':
        if not args.token:
            parser.error('Must provide a token, either by argument (-to TOKEN)'
                         f' or in env variable (${ENV_GITLAB_ACCESS_TOKEN})')
    if args.option == 'create_release':
        if args.shas and len(args.shas) != len(set(args.shas)):
            parser.error('Found duplicate values in the input shas')
        elif args.iids and len(args.iids) != len(set(args.iids)):
            parser.error('Found duplicate values in the input iids')
        if args.version_type:
            raise NotImplementedError('Not implemented yet')  # TODO
    if args.option == 'build_delta':
        if 'target' not in args or not args.target:
            args.target = f'{args.source}~1'
    return args


def __merge_parser(subparser):
    ''' Adds arguments for merge subparser '''
    subparser.add_argument('-r', '--remote', default='origin',
                           help='Remote name from which to fetch '
                                'and checkout, default=\'origin\'')
    subparser.add_argument('-s', '--source', required=True,
                           help='Merge source ref, with the code to be merged')
    subparser.add_argument('-t', '--target', required=True,
                           help='Merge target ref, changes from source will '
                                'end here')
    subparser.add_argument('-d', '--delta-folder', default=DELTA_FOLDER,
                           help='Delta folder name, default=\'srcToDeploy\'')
    subparser.add_argument('-a', '--api-version',
                           default=API_VERSION, type=float,
                           help='API Version of the delta generated default '
                                f'value is {API_VERSION}')
    subparser.add_argument('-nf', '--no-fetch', default=True,
                           action='store_false', dest='fetch',
                           help='Flag to select if it is necessary to fetch '
                                'before checkout')
    subparser.add_argument('-nr', '--no-reset', default=True,
                           action='store_false', dest='reset',
                           help='Flag to select if it is necessary to hard '
                                'reset the branches before merge')
    subparser.add_argument('-sf', '--source-folder', default=SOURCE_FOLDER,
                           help='Source folder name, default=\'src\'')
    subparser.add_argument('-dsc', '--describe', default='describe.log',
                           help='Path to describe log file.')
    subparser.add_argument('-nb', '--no-breakdown', action='store_false',
                           dest='do_breakdown',
                           help='Flag to toggle breakdown in compund objects')
    subparser.add_argument('-pt', '--print-tree', action='store_true',
                           dest='print_tree',
                           help='Prints complete tree in the stdout')



def __build_parser(subparser):
    ''' Adds arguments for merge subparser '''
    subparser.add_argument('-r', '--remote', default='origin',
                           help='Remote name from which to fetch '
                                'and checkout, default=\'origin\'')
    subparser.add_argument('-b', '--branch', default='develop',
                           help='Branch')  # TODO algo
    subparser.add_argument('-s', '--source', default='HEAD',
                           help='Merge source ref, with the code to be merged')
    subparser.add_argument('-t', '--target',
                           help='Merge target ref, changes from source will '
                                'end here')
    subparser.add_argument('-d', '--delta-folder', default=DELTA_FOLDER,
                           help='Delta folder name, default=\'srcToDeploy\'')
    subparser.add_argument('-a', '--api-version',
                           default=API_VERSION, type=float,
                           help='API Version of the delta generated default '
                                f'value is {API_VERSION}')
    subparser.add_argument('-nf', '--no-fetch', default=True,
                           action='store_false', dest='fetch',
                           help='Flag to select if it is necessary to fetch '
                                'before checkout')
    subparser.add_argument('-nr', '--no-reset', default=True,
                           action='store_false', dest='reset',
                           help='Flag to select if it is necessary to hard '
                                'reset the branches before merge')
    subparser.add_argument('-sf', '--source-folder', default=SOURCE_FOLDER,
                           help='Source folder name, default=\'src\'')
    subparser.add_argument('-dsc', '--describe', default='describe.log',
                           help='Path to describe log file.')
    subparser.add_argument('-nb', '--no-breakdown', action='store_false',
                           dest='do_breakdown',
                           help='Flag to toggle breakdown in compund objects')
    subparser.add_argument('-pt', '--print-tree', action='store_true',
                           dest='print_tree',
                           help='Prints complete tree in the stdout')


def __list_mc(subparser):
    ''' Adds arguments for list subparser '''
    default_pretty = PrettyFormat.get_name_list()
    choices_format = OutputType.get_name_list()
    source_help = ('Merge source branch, used to filter merge commits in the '
                   'specified branch, default is None (No filter)')
    subparser.add_argument('-s', '--source', help=source_help)
    columns_help = (f'Merge source branch, with the code to be merged, default'
                    ' value is {default_pretty}')
    subparser.add_argument('-c', '--columns', default=default_pretty,
                           nargs='+', help=columns_help)
    format_help = 'Merge source branch, with the code to be merged'
    subparser.add_argument('-f', '--format', default=OutputType.SCREEN.value,
                           choices=choices_format, help=format_help)
    subparser.add_argument('-ns', '--no-ssl', action='store_false',
                           dest='ssl_verify',
                           help='Flag to verify the SSL in requests')


def __list_mr(subparser):
    ''' Adds arguments for list subparser '''
    subparser.add_argument('-r', '--remote', default='origin',
                           help='Remote name from which to fetch and '
                                'checkout, default=\'origin\'')
    source_help = 'Merge Request target branch, used to filter Merge Requests'
    subparser.add_argument('-s', '--source', required=True, help=source_help)
    target_help = ('Merge target branch, changes from source will end here, '
                   'used to ignore merge requests already in target branch')
    subparser.add_argument('-t', '--target', required=True,
                           help=target_help)
    token_help = ('Gitlab Access token, can be passed as argument or '
                  f'obtained from env variable ${ENV_GITLAB_ACCESS_TOKEN}')
    subparser.add_argument('-to', '--token',
                           default=os.environ.get(ENV_GITLAB_ACCESS_TOKEN),
                           help=token_help)
    subparser.add_argument('-ns', '--no-ssl', action='store_false',
                           dest='ssl_verify',
                           help='Flag to verify the SSL in requests')


def __release_parser(subparser):
    ''' Adds arguments for release subparser '''
    commits_description = ('Provide either MR Iids or Merge Commits SHAS to '
                           'Cherry Pick into the new release branch. REQUIRED')
    commits_group = subparser.add_argument_group('Selector Arguments',
                                                 commits_description)
    commits = commits_group.add_mutually_exclusive_group(required=True)
    help_iid = ('Merge Request Iids for obtaining the commits to '
                'cherry pick into the release branch')
    commits.add_argument('-i', '--iids', nargs='+', type=int, help=help_iid)
    help_sha = ('Merge Commits SHAs for obtaining the commits to '
                'cherry pick into the release branch')
    commits.add_argument('-s', '--shas', nargs='+', help=help_sha)

    token_help = ('Gitlab Access token, can be passed as argument or '
                  f'obtained from env variable ${ENV_GITLAB_ACCESS_TOKEN}')
    subparser.add_argument('-to', '--token',
                           default=os.environ.get(ENV_GITLAB_ACCESS_TOKEN),
                           help=token_help)

    version_description = ('Arguments to select the version associated to the '
                           'new release branch that is going to be created '
                           'the format release/{VERSION}')
    version_group = subparser.add_argument_group('Version Arguments',
                                                 version_description)
    version_group = version_group.add_mutually_exclusive_group()
    version_group.required = True
    version_group.add_argument('-f', '--fix', dest='version_type',
                               const=Version.FIX, action='store_const',
                               help='Flag to select this release as a Fix')
    version_group.add_argument('-m', '--minor', dest='version_type',
                               const=Version.MINOR, action='store_const',
                               help='Flag to select this release as a Minor')
    version_group.add_argument('-M', '--mayor', dest='version_type',
                               const=Version.MAJOR, action='store_const',
                               help='Flag to select this release as a Major')
    version_group.add_argument('-v', '--version',
                               help='Force the version of the new release bran'
                                    'ch to be the specified in this arg')
    project_help = (f'Project id of the current project, '
                    f'default=${ENV_PROJECT_ID}')
    subparser.add_argument('-p', '--project-id', help=project_help,
                           default=os.environ.get(ENV_PROJECT_ID))
    subparser.add_argument('-r', '--remote', default='origin',
                           help='Remote name from which to fetch and checkout,'
                                'default=\'origin\'')

    subparser.add_argument('-t', '--target', required=True,
                           help='Merge target branch, changes from source will'
                                ' end here')
    subparser.add_argument('-d', '--delta-folder', default=DELTA_FOLDER,
                           help='Delta folder name, default=\'srcToDeploy\'')
    subparser.add_argument('-ns', '--no-ssl', action='store_false',
                           dest='ssl_verify',
                           help='Flag to verify the SSL in requests')
