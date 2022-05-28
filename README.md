# Git Based MLOps

![](https://pbs.twimg.com/media/FT1FSFiaUAA2lUh?format=jpg&name=large)

This project shows how to realize MLOps in Git/GitHub. In order to achieve this aim, this project heavily leverages the toolse such as [DVC](https://dvc.org/), [DVC Studio](https://studio.iterative.ai/), [DVCLive](https://dvc.org/doc/dvclive) - all products built by [iterative.ai](https://iterative.ai/), [Google Drive](https://www.google.com/drive/), [Jarvislabs.ai](https://jarvislabs.ai/), and [HuggingFace Hub](https://github.com/huggingface/huggingface_hub).

## Instructions

### Prior work

1. Click "Use this template" button to create your own repository
2. Wait for few seconds, then `Initial Setup` PR will be automatically created
3. Merge the PR, and you are good to go

### Basic setup

0. Run `pip install -r requirements.txt` ([requirements.txt](https://github.com/codingpot/git-mlops/blob/main/requirements.txt))
1. Run `dvc init` to enable DVC
2. Add your data under `data` directory
3. Run `git rm -r --cached 'data' && git commit -m "stop tracking data"`
4. Run `dvc add [ADDED FILE OR DIRECTORY]` to track your data with DVC
5. Run `dvc remote add -d gdrive_storage gdrive://[ID of specific folder in gdrive]` to add Google Drive as the remote data storage
6. Run `dvc push`, then URL to auth is provided. Copy and paste it to the browser, and autheticate
7. Copy the content of `.dvc/tmp/gdrive-user-credentials.json` and put it as in [GitHub Secret](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository) with the name of `GDRIVE_CREDENTIALS`
8. Run `git add . && git commit -m "initial commit" && git push origin main` to keep the initial setup
9. Write your own pipeline under `pipeline` directory. Codes for basic image classification in TensorFlow are provided initially.
10. Run the following `dvc stage add` for training stage
```bash
$ dvc stage add -n train \
                -p train.train_size,train.batch_size,train.epoch,train.lr \
                -d pipeline/modeling.py -d pipeline/train.py -d data \
                --plots-no-cache dvclive/scalars/loss.tsv \
                --plots-no-cache dvclive/scalars/sparse_categorical_accuracy.tsv \
                --plots-no-cache dvclive/scalars/val_loss.tsv \
                --plots-no-cache dvclive/scalars/val_sparse_categorical_accuracy.tsv \
                -o outputs/model \
                python pipeline/train.py outputs/model
```
10. Run the following `dvc stage add` for evaluate stage
```bash
$ dvc stage add -n evaluate \
                -p evaluate.test,evaluate.batch_size \
                -d pipeline/evaluate.py -d data/test -d outputs/model \
                -M outputs/metrics.json \
                python pipeline/evaluate.py outputs/model
```
11. Update `params.yaml` as you need.
12. Run `git add . && git commit -m "add initial pipeline setup" && git push origin main`
13. Run `dvc repro` to run the pipeline initially
14. Run `dvc add outputs/model.tar.gz` to add compressed version of model 
15. Run `dvc push outputs/model.tar.gz`
16. Run `echo "/pipeline/__pycache__" >> .gitignore` to ignore unnecessary directory
17. Run `git add . && git commit -m "add initial pipeline run" && git push origin main`
18. Add access token and user email of [JarvisLabs.ai](https://jarvislabs.ai/) to GitHub Secret as `JARVISLABS_ACCESS_TOKEN` and `JARVISLABS_USER_EMAIL`
19. Add GitHub access token to GitHub Secret as `GH_ACCESS_TOKEN`
20. Create a PR and write `#train` as in comment (you have to be the onwer of the repo)

### HuggingFace Integration Setup

1. Add access token of HugginFace to GitHub Secret as `HF_AT`
2. Add username of HugginfFace to GitHub Secret as `HF_USER_ID`
3. Write `#deploy-hf` in comment of PR you want to deploy to HuggingFace Space
   - GitHub Action assumes your model is archieved as `model.tar.gz` under `outputs` directory
   - Algo GitHub Action assumes your HuggingFace Space app is written in [Gradio](https://gradio.app/) under `hf-space` directory. You need to change [`app_template.py`](https://github.com/codingpot/git-mlops/blob/main/hf-space/app_template.py) as you need(you shouldn't remove any environment variables in the file).

## TODO

- [X] Write solid steps to reproduce this repo for other tasks 
- [X] Deploy experimental model to [HF Space](https://huggingface.co/spaces)
- [ ] Deploy current model to [GKE](https://cloud.google.com/kubernetes-engine) with [auto TFServing deployment project](https://github.com/deep-diver/ml-deployment-k8s-tfserving)
- [ ] Add more cloud providers
- [ ] Add more scripts

## Brief description of each tools

- **DVC(Data Version Control)**: Manages data in somewhere else(i.e. cloud storage) while keeping the version and remote information in metadata file in Git repository.
- **DVCLive**: Provides callbacks for ML framework(i.e. TensorFlow, Keras) to record metrics during training in tsv format. 
- **DVC Studio**: Visuallize the metrics from files in Git repository. What to visuallize is recorded in `dvc.yaml`.
- **Google Drive**: Is used as a remote data repository. However, you can use others such as AWS S3, Google Cloud Storage, or your own file server.
- **Jarvislabs.ai**:  Is used to provision cloud GPU VM instances to conduct each experiments. 
