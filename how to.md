# How to run virtual enviroment

cd C:\Users\moham\Documents\GitHub\tarteel

python3 -m venv venv
//or//
py -3 -m venv venv

venv\Scripts\activate


# How to run flask
flask run


# How to heroku

 - heroku login
 - first time only|| git init
 - first time only|| git checkout -b main  // change branch to main
 - first time only|| git add .  // add all
 - then ||  git add -A  // add only changes
 - git commit -am "make it better"
 - git push heroku main

 - set local to heroku project (first time only) || heroku git:remote -a zerobytes-flask-lms
 - clone from herku to local (then if needed) || heroku git:clone -a zerobytes-flask-lms


# how to setup heroku project


### Create a new Git repository
### Initialize a git repository in a new or existing directory

- cd C:\Users\moham\Documents\GitHub\flask-quiz
- git init
- heroku git:remote -a tarteel-mknoon

### Deploy your application
### Commit your code to the repository and deploy it to Heroku using Git.

- git checkout -b main  // change branch to main || first time only
- git add . // first time only

- git add -A
- git commit -am "make it better"
- 
- git push heroku main



https://devconnected.com/how-to-clear-git-cache/
- To clear your entire Git cache, use the “git rm” command with the “-r” option for recursive.
  git rm -r --cached .

- When all files are removed from the index, you can add the regular files back (the one you did not want to ignore)

 git add .
 git commit -am 'Removed files from the index (now ignored)'






$ heroku login
Initialize a git repository in a new or existing directory


$ cd C:\Users\moham\Documents\GitHub\tarteel-mknoon
$ git init
$ heroku git:remote -a tarteel-mknoon




Commit your code to the repository and deploy it to Heroku using Git.
$ git checkout -b main 
git add .
$ git commit -am "make it better"
$ git push heroku main