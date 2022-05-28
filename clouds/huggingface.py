"""HELLO CLI
Usage:
    huggingface.py
    huggingface.py repo create <token> <userid> <reponame> [--repo-type=<type>] [--space-sdk=<sdk>]
    huggingface.py repo upload <token> <repoid> [--repo-type=<type>] [--target-path=<path>]
    huggingface.py -h|--help
    huggingface.py -v|--version
Options:
    <token>     HuggingFace Access Token
    <userid>    HugginfFace Username
    <reponame>  HuggingFace Repository Name 
    <repoid>    HuggingFace Repository Id (userid/reponame)

    --repo-type=<type>      Repo type [default: model]
    --space-sdk=<sdk>       SDK when --repo-type is set to space [default: gradio]
    --target-path=<path>    Path either filename or directory to upload to repo [default: outputs/model.tar.gz]

    -h --help  Show this screen.
    -v --version  Show version.
"""

import os
import glob
import json
import pathlib
from huggingface_hub import HfApi
from requests.exceptions import HTTPError

from docopt import docopt

def create_or_repo(token: str,
                user_id: str,
                repo_name: str,
                repo_type: str,
                space_sdk: str) -> str:
    hf_api = HfApi()
    hf_api.set_access_token(token)
    repo_id = f'{user_id}/{repo_name}-{repo_type}'

    try:
        hf_api.create_repo(token=token,
                           repo_id=repo_id,
                           repo_type=repo_type,
                           space_sdk=(space_sdk if repo_type == 'space' else None))
        return json.dumps({'status': 'success', 'repo_id': repo_id})
    except HTTPError:
        return json.dumps({'status': 'success', 'repo_id': repo_id})

def _check_allowed_file(filepath):
    prohibited_extensions = ['.dvc', '.gitignore', '.json']

    if pathlib.Path(filepath).suffix in prohibited_extensions:
        return False
    
    return True

def _upload_files(hf_api,
                  token: str, 
                  repo_id: str,
                  path: str,
                  repo_type: str):
    count = 0

    if os.path.isdir(path):
        for filepath in glob.iglob(f'{path}/**/**', recursive=True):
            if os.path.isdir(filepath) is False and \
               _check_allowed_file(filepath):
                hf_api.upload_file(path_or_fileobj=filepath,
                                path_in_repo='/'.join(filepath.split('/')[1:]),
                                repo_id=repo_id,
                                token=token,
                                repo_type=repo_type)
                count = count + 1                            

    else:
        hf_api.upload_file(path_or_fileobj=path,
                           path_in_repo=path,
                           repo_id=repo_id,
                           token=token,
                           repo_type=repo_type)
        count = count+1                           

    return count

def upload_to_repo(token: str,
                   repo_id: str,
                   path: str='outputs/model.tar.gz',
                   repo_type: str='model') -> str:
    hf_api = HfApi()
    hf_api.set_access_token(token)

    count = _upload_files(hf_api, token, repo_id, path, repo_type)
    return json.dumps({'status': 'success', 'count': f'{count}'})

if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')
    if arguments['<token>']:
        token = arguments['<token>']

        if arguments['<userid>'] and arguments['<reponame>']:
            userid = arguments['<userid>']
            reponame = arguments['<reponame>']
            repo_type = arguments['--repo-type']
            if repo_type == 'model':
                space_sdk = None
            else:
                space_sdk = arguments['--space-sdk']

            result = create_or_repo(token, userid, reponame, repo_type, space_sdk)
            print(result)
    
        if arguments['<repoid>']:
            repoid = arguments['<repoid>']
            repo_type = arguments['--repo-type']
            
            if repo_type == 'space' and arguments['--target-path'] == 'outputs/model.tar.gz':
                target_path = 'hf-space'
            else:
                target_path = arguments['--target-path']
                
            result = upload_to_repo(token, repoid, target_path, repo_type)
