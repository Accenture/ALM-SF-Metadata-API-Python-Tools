''' Create Release Module '''
from modules.git import checkout, cherry_pick, create_branch, fetch
from modules.git.models import MergeCommit
from modules.git.remote import get_merge_requests, get_project_id
from modules.utils import INFO_TAG, call_subprocess, print_key_value_list
from modules.utils.models import OutputType


def list_merge_requests(source_branch, target_branch, token,
                        remote, ssl_verify):
    ''' Returns a list of valid merge requests from source to target branch '''
    project_id = get_project_id(token, ssl_verify)
    print(f'{INFO_TAG} Current Project Id: {project_id}')
    merge_requests = get_merge_requests(project_id, token, source_branch, 0,
                                        25, ssl_verify).values()
    print(f'{INFO_TAG} Found {len(merge_requests)} Merge Requests with '
          f'\'merged\' state to target \'{source_branch}\'')
    return __filter_merge_requests(merge_requests, target_branch, remote)


def __filter_merge_requests(merge_requests, target_branch, remote):
    ''' Erase merge requests already in target branch '''
    fetch(remote, verbose=False)

    checkout(target_branch, remote, reset=False)

    command = 'git log --pretty=format:\'%H\''
    hashes, _ = call_subprocess(command, verbose=False)
    hashes = hashes.split('\n')

    merge_requests = [merge_request for merge_request in merge_requests
                      if merge_request.sha not in hashes]

    print(f'{INFO_TAG} {len(merge_requests)} Merge Requests after filtering')
    for merge_request in merge_requests:
        print(f'\t-{merge_request}')
    return merge_requests


def list_merge_commits(source_branch, columns, output_type):
    ''' List Merge Commits '''
    commits = MergeCommit.get_merge_commits(source_branch)
    commits_string = '\n'.join([commit.output(output_type, columns)
                                for commit in commits])
    row_separator = ''
    if output_type == OutputType.SCREEN.value:
        row_separator = '-' * len(commits_string.split('\n')[0].expandtabs())
        row_separator += '\n'
    whole_output = (f'{MergeCommit.get_header(columns, output_type)}\n'
                    f'{row_separator}{commits_string}')
    print(whole_output)


def create_release(version, target, remote, token, project_id=None,
                   sha_commits=None, iids=None, ssl_verify=False):
    ''' Creates a release branch with the mr passed onto the branch passed '''
    print_key_value_list(f'{INFO_TAG} Creating release',
                         [('Sha Commits', sha_commits), ('Iids', iids),
                          ('Version', version), ('Target Branch', target)])
    if iids:
        sha_commits = get_shas_for_iids(token, iids, project_id,
                                        None, ssl_verify)

    checkout(target, remote, reset=False)

    branch_name = f'release/{version}'
    create_branch(branch_name, do_checkout=True)

    for sha_commit in sha_commits:
        cherry_pick(sha_commit)


def get_shas_for_iids(token, iids, target, project_id=None, ssl_verify=False):
    ''' Returns the shas associated to the Merge Request with iids passed '''
    project_id = (get_project_id(token, ssl_verify)
                  if not project_id else project_id)
    merge_requests = get_merge_requests(project_id, token,
                                        per_page=100, ssl_verify=ssl_verify)

    if not set(iids).issubset(set(merge_requests.keys())):
        raise Exception('We are currently working at this sorry...')

    shas = {iid: merge_requests[iid].sha for iid in iids}
    print(f'{INFO_TAG} SHAs obtainer from iid {shas}')

    return shas.values()
