# charcha
# Introduction

Write about your project in this area.

# Developer Guide

## Getting Started

### Prerequisites
- [virtualenv](https://virtualenv.pypa.io/en/latest/)
- [postgresql]()
- [mysql]()
- [redis]()

### Initialize the project
Create and activate a virtualenv:

```bash
virtualenv venv
source venv/bin/activate
```
Install dependencies:

```bash
pip install -r requirements.txt
```
NOTE: After installing dependencies, pip-tools is also installed. You can now use it to manage package dependencies of your project.
```bash
'''
Add a new package to requirements.in and run the following command to auto-update requirements.txt file
'''
pip-compile requirements.in

'''
Run the following command to sync your virtualenv
'''
pip-sync
```
 For more details, https://github.com/nvie/pip-tools

Migrate, create a superuser, and run the server:
```bash
python manage.py migrate
python manage.py makemigrations hashertalk
python manage.py createsuperuser
python manage.py runserver
```

## Setting up Environment Variables
Edit the environment variables in **'.env.template'** file and then **RENAME** the file to **'.env'**

NOTE: This file has already been added to .gitignore, hence it will not be pushed to your repository.
While deployment or using CI tools like travis or circle-ci, you have to take care of setting the environment variables seperately.

## Database setup
This project uses dj-database-url library to setup databases. Use the  **DATABASE_URL** environment variable to configure your Django application. set this environment variable with the complete database url.
For more info: https://github.com/kennethreitz/dj-database-url

## Email server setup
This project uses dj-email-url library to setup email servers.
Provide your smtp server url in the **EMAIL_URL** environment variable.
For more info: https://github.com/migonzalvar/dj-email-url

## Static Files
There's a 'static' directory configured already inside the project that is to be used to keep satic JavaScript, CSS, etc files to be used in templates.

## Running test Cases
Some test cases have been included in the authentication/test directory.
Use the following command to run test cases in all apps.

```bash
python manage.py test
```

## Travis-CI Setup
If Travis is setup, then use the **.travis.yml** file in the project root directory to configure travis settings, setting up test environment for travis etc.
For more info on travis, https://travis-ci.org/

## Circle-CI Setup
If Circle-CI is setup, then it takes most of the settings from the project itself, but still there is a circle.yml file included at the project root for configuration.
for more info, https://circleci.com/docs/language-python/


# Deployment Guide


## Setting up Heroku
Deployment to heroku requires a Procfile which is present in the main directory. This can always be changed on need basis.

Following steps need to be undertaken to deploy to heroku
  1. Create an account on heroku if not already.
  2. Create a heroku app - you could either use the heroku dashboard to do this or the heroku cli.
  3. Install Heroku cli - [documentation](https://devcenter.heroku.com/articles/heroku-cli)

#### create a heroku app using cli
  1. Use `heroku login` and enter your credentials.
  2. Run `heroku create {app-name}` to create your app on heroku. This would give you the app deployment url and the apps git url. [documentation](https://devcenter.heroku.com/articles/creating-apps).

#### Deployment to heroku
  1. Add the heroku git url using `git remote add heroku {heroku-git-url}` (required only for the first time).
  2. To deploy a build, run `git push heroku HEAD:master` . This should push all changes to heroku which can be viewed at the app url.




## Viewing Logs





## Revert Build


# Troubleshooting
