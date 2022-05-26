import typer
from jlclient import jarvisclient
from jlclient.jarvisclient import *

from typing import Optional

app = typer.Typer()

vm_app = typer.Typer()
app.add_typer(vm_app, name="vm")

script_app = typer.Typer()
app.add_typer(script_app, name="script")

@vm_app.command("create")
def vm_create(token: str,
              userid: str,
              scriptid: str,
              gpu_type:str='RTX5000',
              n_gpus:int=1,
              hdd:int=50,
              framework_id:int=2,
              name:str='test',
              is_reserved:bool=False):
    jarvisclient.token = token
    jarvisclient.user_id = userid

    instance = Instance.create(gpu_type=gpu_type,
                                num_gpus=n_gpus,
                                hdd=hdd,
                                framework_id=framework_id,
                                name=name,
                                is_reserved=is_reserved,
                                script_id=scriptid)

#     gpu_types = ['RTX6000', 'A5000', 'A6000', 'A100']
#     gpu_type_idx = 0
    
#     while "error" in instance:
#       if 'No GPU instances available' in instance['error']:
#         gpu_type = gpu_types[gpu_type_idx]
#         gpu_type_idx = gpu_type_idx + 1
        
#         if gpu_type_idx == len(gpu_types): break

#       instance = Instance.create(gpu_type=gpu_type,
#                                   num_gpus=n_gpus,
#                                   hdd=hdd,
#                                   framework_id=framework_id,
#                                   name=name,
#                                   is_reserved=is_reserved,
#                                   script_id=scriptid)        
        
    typer.echo(instance)

@vm_app.command("destroy")
def vm_destroy(token: str,
               userid: str,
               instance_id: int):
    jarvisclient.token = token
    jarvisclient.user_id = userid

    instance = User.get_instance(instance_id)
    instance.destroy()

@script_app.command("add")
def script_add(token: str,
               userid: str,
               script_path: str,
               name: str="test script"):
    jarvisclient.token = token
    jarvisclient.user_id = userid

    script = User.add_script(script_path=script_path,
                             script_name=name)

    typer.echo(script['script_id'])

@script_app.command("remove")
def script_remove(token: str,
                  userid: str,
                  script_id: str):
    jarvisclient.token = token
    jarvisclient.user_id = userid

    User.delete_script(script_id)

if __name__ == "__main__":
    app()