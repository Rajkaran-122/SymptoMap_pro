import os

env_script = """
if test "$GIT_AUTHOR_EMAIL" = "sajal101agrawal@gmail.com"
then
    GIT_AUTHOR_NAME="Rajkaran yadav"
    GIT_AUTHOR_EMAIL="yadavrajkaran854@gmail.com"
fi
if test "$GIT_COMMITTER_EMAIL" = "sajal101agrawal@gmail.com"
then
    GIT_COMMITTER_NAME="Rajkaran yadav"
    GIT_COMMITTER_EMAIL="yadavrajkaran854@gmail.com"
fi
"""

cmd = 'git filter-branch -f --env-filter \'' + env_script.replace('\n', ' ') + '\' -- --all'
print('Executing git filter-branch...')
os.system(cmd)
