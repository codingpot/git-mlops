#!/bin/sh

# install gh cli
apt install sudo
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# grant gh access 
export GH_TOKEN='$GH_ACCESS_TOKEN'
git config --global user.name "chansung"
git config --global user.email "deep.diver.csp@gmail.com"

# set W&B specific keys
export WANDB_PROJECT='$WANDB_PROJECT'
export WANDB_API_KEY='$WANDB_API_KEY'

# move to the repo
git clone https://github.com/codingpot/git-mlops.git

# install dependencies
cd git-mlops
gh auth setup-git
git checkout $CUR_BRANCH
pip install -r requirements.txt
pip install git+https://github.com/jarvislabsai/jlclient.git

# set Gdrive credential
mkdir .dvc/tmp
echo '$GDRIVE_CREDENTIAL' > .dvc/tmp/gdrive-user-credentials.json

# pull data
dvc pull

export WANDB_RUN_NAME=$CUR_BRANCH
dvc repro

exp_result=$(dvc exp show --only-changed --md)
wandb_url="https://wandb.ai/codingpot/git-mlops"
gh pr comment $CUR_PR_ID --body "[Visit W&B Log Page for this Pull Request]($wandb_url)"

git reset --hard

echo ${exp_ids[$idx]}
echo ${exp_names[$idx]}
dvc add outputs/model.tar.gz
dvc push outputs/model.tar.gz

VM_ID=$(tail -n 2 /home/.jarviscloud/jarvisconfig | head -n 1)
python clouds/jarvislabs.py vm destroy $CLOUD_AT $CLOUD_ID $VM_ID
