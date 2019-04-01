# Catalog Application
A simple web application that provides a generic framework to _**catalog**_ items by specified categories.  There are four components to the application:

1. HTML
2. CSS
3. Flask
4. Database


Upon startup, the application will populate a database with example sporting categories.  A user can modify the categories to their own liking by modifying
the following function in `flask_server.py`

```
def load_category_table():
    """
    Pre-populate category table with the following list.
    """
    categories = [ 'Soccer',
                   'Basketball',
                   'Baseball',
                   'Frisbee',
                   'Snowboarding',
                   'Rock Climbing',
                   'Football',
                   'Skating',
                   'Hockey'
                  ]
```
To launch the web service on a Linux system with Python version 2.7:
```
python flask_server.py
```

To use the web service, the web application is configured to service port 8000 and provides the following endpoints:

- `http://localhost:8000/` - root webpage
- `http://localhost:8000/catalog` - alternate root webpage
- `http://localhost:8000/catalog/JSON` - restAPI endpoint that will return the entire contents of the catalog database

_**Note**_: to add, edit or delete data, you will need to authenticate using 3rd party authentication service provided by Google or Facebook.  Additionally, you will not be allowd to edit or delete data that you do not own.

## Technical Overview
The application is built with:
- [Flask](http://flask.pocoo.org/) - Python web service framework
- [Jinja2](http://jinja.pocoo.org/docs/2.10/) - HTML Template engine for Python
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL toolkit and Object Relational Mapper
- [SQLite](https://www.sqlite.org/index.html) - A lightweigh, serverless, SQL database engine (PostgreSQL can easily be plugged into this project)


## Dependencies

This project was done on Mac OS using the following:
- OS X Terminal
- Vagrant (v2.2.3)/VirtualBox (v5.2.4)
  - If you don't have VirtualBox, get it [here](https://www.virtualbox.org/wiki/Downloads). Install the *platform package* for your operating system. You do not need the extension pack or the SDK.
  - If you don't have Vagrant, get it [here](https://www.vagrantup.com/downloads.html). Vagrant is an open-source software product for building and maintaining portable virtual software development environments,; install the version for your operating system.


This Github repository contains the `Vagrantfile` used by this project.  

From a terminal, `cd` to the directory where your cloned or downloaded the Vagrantfile.  Using `ls`, you should now see the Vagrantfile. You are now ready to launch the Ubuntu image.

#### Launch Ubuntu image
- `vagrant up`  - to download (first time only) and start the VM
- `vagrant ssh` - to access the VM
- `cd /vagrant` - to access the volume mount that is shared with the host (same host location where you executed `vagrant up`)
- You can now run `python flask_server.py` as noted above

Point your favorite browser to `http://localhost:8000/` and have fun!
