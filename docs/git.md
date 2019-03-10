```
# see the status of changed files
git status

# add all pending changes to git
git add --all

# commit (you will be prompted for a message)
git commit

# push the commits to the repository on github
git push

# stash you changes
git stash

# re apply stashed changes
git stash apply

# get the latest changes
git pull

#Pull put ignore local changes
git reset --hard
git pull

# Tell git to remember your login add password
## Set git to use the credential memory cache
git config --global credential.helper cache
## Change the default password cache timeout, enter the following:
git config --global credential.helper 'cache --timeout=3600'

```