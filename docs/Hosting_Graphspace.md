# Hosting a GraphSpace Server

## How to deploy the latest Github code changes on GraphSpace server? ##

Here are the steps for deploying GraphSpace. It is recommended to download the [latest release](https://github.com/Murali-group/GraphSpace/releases/latest). Otherwise you can download the latest code directly from the [master branch](https://github.com/Murali-group/GraphSpace).
Then follow the steps to [run GraphSpace on Apache](https://github.com/Murali-group/GraphSpace#running-graphspace-on-apache). These include steps to install the correct version of python, setup postgreSQL, virtualenv, bower, ElasticSearch, etc.

>**Note**:
>Be careful when running alembic migration scripts if you plan to continually update a deployment of GraphSpace. Understand how to use [alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html#) and alembic commands. Migrations are not needed if you are creating the database for the first time.

***Useful Links***
- [How to configure Apache to run Django website](https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/modwsgi/#basic-configuration)
- [How to use Django with Apache and mod-wsgi](https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/modwsgi/)
