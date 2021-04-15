# Hosting GraphSpace

## Steps to deploy GraphSpace on a server ##

We recommended downloading the [latest release](https://github.com/Murali-group/GraphSpace/releases/latest). Alternatively, you can download the latest code directly from the [master branch](https://github.com/Murali-group/GraphSpace).
Then follow the steps to [run GraphSpace on Apache](https://github.com/Murali-group/GraphSpace#running-graphspace-on-apache). These include steps to install the correct version of python, setup postgreSQL, virtualenv, bower, ElasticSearch, etc.

>**Note**:
>If you have an existing deployment of GraphSpace, be careful when running alembic migration scripts. Understand how to use [alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html#) and alembic commands. Migrations are not needed if you are deploying GraphSpace for the first time.
>`alembic upgrade head` will run migrations if the current *head* is the downgrade version of the latest migration script.

***Useful Links***
- [How to configure Apache to run Django website](https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/modwsgi/#basic-configuration)
- [How to use Django with Apache and mod-wsgi](https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/modwsgi/)
- [How to run migrations with Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html#)
