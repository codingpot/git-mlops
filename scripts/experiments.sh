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

# move to the repo
git clone https://github.com/deep-diver/git-mlops.git

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

exp_names=("base")
dvc exp run

dvc exp show > exp_results.txt
exp_id_strings=`grep -oe "exp-[a-z0-9]\+" exp_results.txt`
exp_ids=($exp_id_strings)
cur_branch=$(git branch | sed -n -e 's/^\* \(.*\)/\1/p')

exp_result=$(dvc exp show --only-changed --md)
gh pr comment $CUR_PR_ID --body "$exp_result"

git reset --hard
for idx in ${!exp_names[@]}
do
   echo ${exp_ids[$idx]}
   echo ${exp_names[$idx]}
   dvc exp branch ${exp_ids[$idx]} ${exp_names[$idx]}
   git branch -m ${exp_names[$idx]} exp-$cur_branch-${exp_names[$idx]}
   git checkout exp-$cur_branch-${exp_names[$idx]}
   git push origin exp-$cur_branch-${exp_names[$idx]}
   git checkout $CUR_BRANCH
done

VM_ID=$(tail -n 2 /home/.jarviscloud/jarvisconfig | head -n 1)
python clouds/jarvislabs.py vm destroy $CLOUD_AT $CLOUD_ID $VM_ID