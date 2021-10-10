(Draft)

[[_TOC_]]

## Overview

!(To be written)!


## Setting up

### System requirements

* Python 3.8 (other versions of Python 3 may also be fine; one can specify the desired version in [Pipfile](Pipfile))
* [pipenv](https://pypi.org/project/pipenv/)

Clone this repository with `git clone` or otherwise.

### Virtual environment

A Python virtual environment will be used, in which the Django package and other tools will be installed. 
To install the Python packages used in this project, `cd` into the cloned repository and run:

```bash
pipenv install
```

(For deployment, one may want to install the packages directly into the system; see the ['Deployment' section](#deployment-with-gunicorn-and-nginx))

This will create a virtual environment and install into it Django, three other Python packages – `django-upload-validator` (used for file validation), `requests` (used for sending messages over webhooks) and `psycopg2-binary` (used for PostgreSQL; see the ['Database' section](#database)) – and any dependencies.

`pipenv` should print out where the virtual environment is installed (usually it is `$HOME/.virtualenvs/<dir_name>-<hash>`).

To activate the virtual environment:

```bash
pipenv shell
```

When the virtual environment is active, its name should be displayed at the start of the prompt.

To exit the virtual environment, enter `exit` or press Ctrl + D.

### Database

Django works with various database backends, with official or third-party support.
See Django's official documentation on [databses](https://docs.djangoproject.com/en/3.1/ref/databases/#postgresql-notes).

The owner of the repository has opted for PostgreSQL.

#### Example: PostgreSQL

To install the PostgreSQL software on the database host (with may or may not be the system where the Django project is developed/deployed), run:

```bash
sudo apt install postgresql 
```

(`postgresql-contrib`?)

For the Django project to work as PostgreSQL, one needs the Python package `psycopg2-binary` to be present in the virtual environment; see the [package documentation](https://www.psycopg.org/docs/install.html).
This package depends on `python3-dev` and `libpq-dev`, which can be installed with APT.

To create and configure the database, enter PostgreSQL's `psql` prompt:

```bash
sudo -u postgres psql
```

and run the following commands (replacing `django`, `contest` and `password` with custom values):

```postgresql
CREATE USER django WITH ENCRYPTED PASSWORD 'password';
ALTER ROLE django SET client_encoding TO 'utf8';
ALTER ROLE django SET default_transaction_isolation TO 'read committed';
ALTER ROLE django SET timezone TO 'UTC';

CREATE DATABASE contest;
GRANT ALL PRIVILEGES ON DATABASE contest TO django;
```

Exit the `psql` prompt by entering the command `\q`.

!(Configuring the Django project)!


## Working in Visual Studio Code

[vscode-python-ext]: https://marketplace.visualstudio.com/items?itemName=ms-python.python
[vscode-env]: https://code.visualstudio.com/docs/python/environments
[vscode-lint]: https://code.visualstudio.com/docs/python/linting
[vscode-debug]: https://code.visualstudio.com/docs/python/debugging

Text editors may have built-in support or optional extensions that enhance the experience of working with Python.
Visual Studio Code is used as an example here.

To optimise the coding, linting and debugging experience in VS Code, install the [Python extension for VS Code][vscode-python-ext] and modify the workspace settings so that VS Code detects and uses the Python environment (see [official instructions][vscode-env]).
VS Code will then launch its integrated terminal in the virtual environment (when the Python extension is activated).

See [offical instructions][vscode-lint] on configuring VS Code for Python linting.
It appears that VS Code uses the Pylint and autopep8 packages for linting and the Rope package for code refactoring by default.

Pylint may not be entirely compatible with Django.
To fix this, use the [`pylint-django` plug-in](https://github.com/PyCQA/pylint-django), and modify the 'Pylint Args' setting in the workspace to include `--load-plugins=pylint_django`.

To install these development packages, simply run `pipenv install --dev`, as they have been specified in [Pipfile](Pipfile).


## Developing

!(Point to the official manual)!

### Frequently used commands

```bash
django-admin startapp <app_name>
python3 manage.py makemigrations
python3 manage.py migrate

# To create an admin account:
python3 manage.py createsuperuser
```

### Running the website

With the virtual environment activated, run the following command and access `localhost:8000` in a browser.

```bash
python3 manage.py runserver [<address>:<port>]
```

If the project is on a remote server, then one can forward the port 8000 to a local machine via SSH.

### Debugging

Follow the [offical instructions][vscode-debug].


## Deployment (with Gunicorn and Nginx)

For deployment, clone this repository into a server, e.g. inside the home directory of a user named "django", and install the Python packages to the system:

```bash
pipenv install --system --deploy --ignore-pipfile
```

### Django project settings

See the official [deployment checklist](https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/).

### Collect static files

Run the following command to copy static files into the path specified as `STATIC_ROOT` in the [Django project settings](contest/settings.py).

```bash
python3 manage.py collectstatic
```

### Gunicorn and Nginx configurations

This section is based on the [tutorial by Erin Glass](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-20-04).
One important addition I have made is the inclusion of a file containing environment variables for deployment.
The tutorial also contains debugging tips, which are omitted here.
I do not yet fully understand everything in this section.

#### Setting environment variables

Store new-line-separated variable assignments in a file on the server (*e.g.* `.env`).
Gunicorn will be referred to this file.

#### Installing and testing Gunicorn

With the virtual environment activated, install Gunicorn:

```bash
pipenv install --system gunicorn
```

Check that Gunicorn works with the project's WSGI module by running:

```bash
gunicorn <project_name>.wsgi
```

(optional argument `--bind <address>:<port>`; if you have simply cloned this repository, the project name is "contest").

This should have a similar effect to running "`python3 manage.py runserver [<address>:<port>]`".

#### Creating `systemd` socket and service files for Gunicorn

Create the file `/etc/systemd/system/gunicorn.socket` and populate it with:

```systemd
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

Create the file `/etc/systemd/system/gunicorn.service` and populate it with the example content below (substituting the paths `<project_directory>`, `<environment_file_path>` and `<virtual_environment_directory>`, and replacing `contest` if you have used a different project name):

```systemd
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=<user>
Group=www-data
WorkingDirectory=<project_directory>
EnvironmentFile=<environment_file_path>
ExecStart=<virtual_environment_directory>/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          contest.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable and start the Gunicorn socket:

```bash
sudo systemctl enable --now gunicorn.socket
```

The socket file `/run/gunicorn.sock` should now have been generated; check by running:

```bash
file /run/gunicorn.sock
```

and expecting output:

```
/run/gunicorn.sock: socket
```

#### Configuring Nginx

Install Nginx:

```bash
sudo apt install nginx
```

Create the file `/etc/nginx/sites-available/<configuration_name>` and populate it with _**e.g.**_

```nginx
server {
    listen 443 ssl;
    server_name contest.icmathscomp.org;

    client_max_body_size 2m;
    
    location = /favicon.ico { access_log off; log_not_found off; }
    location = /robots.txt { 
        alias /home/django/deployment/robots.txt;
        access_log off;
        log_not_found off; }
    location /static/ {
        root /home/django/deployment;
    }
    location /media/ {
        root /home/django/deployment;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

Create a symbolic link:

```bash
sudo ln -s /etc/nginx/sites-available/<configuration_name> /etc/nginx/sites-enabled/
```

Remove the default symbolic link (this was not mentioned in the tutorial but seemed necessary for things to work on my system):

```bash
sudo unlink /etc/nginx/sites-enabled/default
```

Test the Nginx configuration for syntax errors by running:

```bash
sudo nginx -t
```

Restart Nginx to effect the configuration:

```bash
sudo systemctl restart nginx
```

The website should now be available at the server's domain or IP address (don't forget to allow Nginx traffic through the firewall with the `ufw` utility).

### SSL certificates

See one approach [here](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-20-04).
For how to revoke SSL certificates issued with this approach, see [here](https://certbot.eff.org/docs/using.html#revoking-certificates).

### Updating the website

After changes to the Django project, effect the changes by running:

```
sudo systemctl restart gunicorn
```

After changes to the Gunicorn or Nginx configuration, !(complete the paragraph)!

### Other notes

#### Crawling, indexing and `robots.txt`

See [Google Search Central's documentation](https://developers.google.com/search/docs/advanced/crawling/overview) on this subject.
