#!/usr/local/bin/python3
''' Merger module '''
import sys

from modules.create_release import (create_release, list_merge_commits,
                                    list_merge_requests)
from modules.delta_builder import build_delta, merge_delta
from modules.git.utils import (is_commit_user_configured, is_git_repository,
                               is_valid_remote)
from modules.utils import FATAL_LINE, SUCCESS_LINE, WARNING_LINE
from modules.utils.argparser import parse_args
from modules.utils.exceptions import (CommitUserNotConfigured,
                                      InvalidRemoteSpecified, MergerException,
                                      MergerExceptionWarning,
                                      NotAGitRepository)

__version__ = "3.3.1"


def prevalidations(args):
    if not is_git_repository():
        raise NotAGitRepository()

    if args.fetch and not is_valid_remote(args.remote):
        if args.remote_specified:
            raise InvalidRemoteSpecified(args.remote)
        print(f'{WARNING_LINE} Default remote \'{args.remote}\' does not '
              'exist, forcing no fetch')
        args.fetch = False

    if args.option == 'merge_delta' and not is_commit_user_configured():
        raise CommitUserNotConfigured()


def main():
    ''' Main method '''
    args = parse_args()
    if args.option == 'version':
        print(__version__)
        sys.exit(0)
    try:
        prevalidations(args)
        if args.option == 'list_mc':
            list_merge_commits(args.source, args.columns, args.format)
        elif args.option == 'list_mr':
            list_merge_requests(args.source, args.target, args.token,
                                args.remote, args.ssl_verify)
        elif args.option == 'create_release':
            create_release(args.version, args.target, args.remote, args.token,
                           args.project_id, args.shas, args.iids,
                           args.ssl_verify)
        elif args.option == 'merge_delta':
            merge_delta(args.source, args.target, args.remote,
                        args.fetch, args.reset, args.delta_folder,
                        args.source_folder, args.api_version,
                        args.do_breakdown, args.print_tree, args.describe)
            print(f'{SUCCESS_LINE} Build Delta Package Finished correctly')
        elif args.option == 'build_delta':
            build_delta(args.source, args.target, args.remote, args.fetch,
                        args.delta_folder, args.source_folder,
                        args.api_version, args.do_breakdown, args.print_tree,
                        args.describe)
    except MergerExceptionWarning as exception:
        print(f'{WARNING_LINE} {exception}, finished with warnings...')
        sys.exit(exception.ERROR_CODE)
    except MergerException as exception:
        print(f'{FATAL_LINE} {exception}, exiting...')
        sys.exit(exception.ERROR_CODE)


if __name__ == '__main__':
    main()
