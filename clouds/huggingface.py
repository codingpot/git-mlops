import os
import glob
import json
import typer
import pathlib
from huggingface_hub import HfApi
from requests.exceptions import HTTPError

app = typer.Typer()

repo_app = typer.Typer()
app.add_typer(repo_app, name="repo")

@repo_app.command("create")
def create_or_repo(token: str,
                user_id: str,
                repo_name: str,
                repo_type: str='model',
                space_sdk: str='gradio'):
    hf_api = HfApi()
    hf_api.set_access_token(token)
    repo_id = f'{user_id}/{repo_name}-{repo_type}'

    try:
        hf_api.create_repo(token=token,
                           repo_id=repo_id, 
                           repo_type=repo_type,
                           space_sdk=(space_sdk if repo_type == 'space' else None))
        typer.echo(json.dumps({'status': 'success', 'repo_id': repo_id}))
    except HTTPError:
        typer.echo(json.dumps({'status': 'success', 'repo_id': repo_id}))
        
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
                typer.echo(filepath)
                hf_api.upload_file(path_or_fileobj=filepath,
                                path_in_repo=filepath,
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

@repo_app.command("upload")
def upload_to_repo(token: str,
                   repo_id: str,
                   path: str='outputs/model.tar.gz',
                   repo_type: str='model'):
    hf_api = HfApi()
    hf_api.set_access_token(token)

    try:
        count = _upload_files(hf_api, token, repo_id, path, repo_type)
        typer.echo(json.dumps({'status': 'success', 'count': f'{count}'}))
    except ValueError:
        typer.echo(json.dumps({'status': 'fail', 'count': f'{0}'}))

if __name__ == "__main__":
    app()
