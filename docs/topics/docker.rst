.. _docker:


============
Docker image
============

How to use this image
=====================

Start a Mayan EDMS instance
------------------------------

With Docker properly installed, proceed to download the Mayan EDMS image using the command::

    docker pull mayanedms/mayanedms:<version>

Then download version 9.5 of the Docker PostgreSQL image::

    docker pull postgres:9.5

Create and run a PostgreSQL container::

    docker run -d \
    --name mayan-edms-postgres \
    --restart=always \
    -p 5432:5432 \
    -e POSTGRES_USER=mayan \
    -e POSTGRES_DB=mayan \
    -e POSTGRES_PASSWORD=mayanuserpass \
    -v /docker-volumes/mayan-edms/postgres:/var/lib/postgresql/data \
    -d postgres:9.5

The PostgreSQL container will have one database named ``mayan``, with an user
named ``mayan`` too, with a password of ``mayanuserpass``. The container will
expose its internal 5432 port (PostgreSQL's default port) via the host's
5432 port. The data of this container will reside on the host's
``/docker-volumes/mayan-edms/postgres`` folder.

Finally create and run a Mayan EDMS container. Change <version> with the
latest version in numeric form (example: 2.7.3) or use the ``latest``
identifier::

    docker run -d \
    --name mayan-edms \
    --restart=always \
    -p 80:8000 \
    -e MAYAN_DATABASE_ENGINE=django.db.backends.postgresql \
    -e MAYAN_DATABASE_HOST=172.17.0.1 \
    -e MAYAN_DATABASE_NAME=mayan \
    -e MAYAN_DATABASE_PASSWORD=mayanuserpass \
    -e MAYAN_DATABASE_USER=mayan \
    -e MAYAN_DATABASE_CONN_MAX_AGE=60 \
    -v /docker-volumes/mayan-edms/media:/var/lib/mayan \
    mayanedms/mayanedms:<version>

The Mayan EDMS container will connect to the PostgreSQL container via the
``172.17.0.1`` IP address (the Docker host's default IP address). It will
connect using the ``django.db.backends.postgresql`` database drivern and
connect to the ``mayan`` database using the ``mayan`` user with the password
``mayanuserpass``. The container will keep connections to the database
for up to 60 seconds in an attempt to reuse them increasing response time
and reducing memory usage. The files of the container will be store in the
host's ``/docker-volumes/mayan-edms/media`` folder. The container will
expose its web service running on port 8000 on the host's port 80.

The container will be available by browsing to ``http://localhost`` or to
the IP address of the computer running the container.

If another web server is running on port 80 use a different port in the
``-p`` option. For example: ``-p 81:8000``.


Stopping and starting the container
--------------------------------------

To stop the container use::

    docker stop mayan-edms


To start the container again::

    docker start mayan-edms


Environment Variables
---------------------

The Mayan EDMS image can be configure via environment variables.

``MAYAN_DATABASE_ENGINE``

Defaults to ``None``. This environment variable configures the database
backend to use. If left unset, SQLite will be used. The database backends
supported by this Docker image are:

- ``'django.db.backends.postgresql'``
- ``'django.db.backends.mysql'``
- ``'django.db.backends.sqlite3'``

When using the SQLite backend, the database file will be saved in the Docker
volume. The SQLite database as used by Mayan EDMS is meant only for development
or testing, never use it in production.

``MAYAN_DATABASE_NAME``

Defaults to 'mayan'. This optional environment variable can be used to define
the database name that Mayan EDMS will connect to. For more information read
the pertinent Django documentation page: `Connecting to the database`_

.. _Connecting to the database: https://docs.djangoproject.com/en/1.10/ref/databases/#connecting-to-the-database

``MAYAN_DATABASE_USER``

Defaults to 'mayan'. This optional environment variable is used to set the
username that will be used to connect to the database. For more information
read the pertinent Django documentation page: `Settings, USER`_

.. _Settings, USER: https://docs.djangoproject.com/en/1.10/ref/settings/#user

``MAYAN_DATABASE_PASSWORD``

Defaults to ''. This optional environment variable is used to set the
password that will be used to connect to the database. For more information
read the pertinent Django documentation page: `Settings, PASSWORD`_

.. _Settings, PASSWORD: https://docs.djangoproject.com/en/1.10/ref/settings/#password

``MAYAN_DATABASE_HOST``

Defaults to `None`. This optional environment variable is used to set the
hostname that will be used to connect to the database. This can be the
hostname of another container or an IP address. For more information read
the pertinent Django documentation page: `Settings, HOST`_

.. _Settings, HOST: https://docs.djangoproject.com/en/1.10/ref/settings/#host

``MAYAN_DATABASE_PORT``

Defaults to `None`. This optional environment variable is used to set the
port number to use when connecting to the database. An empty string means
the default port. Not used with SQLite. For more information read the
pertinent Django documentation page: `Settings, PORT`_

.. _Settings, PORT: https://docs.djangoproject.com/en/1.11/ref/settings/#port

``MAYAN_BROKER_URL``

This optional environment variable determines the broker that Celery will use
to relay task messages between the frontend code and the background workers.
For more information read the pertinent Celery Kombu documentation page: `Broker URL`_

.. _Broker URL: http://kombu.readthedocs.io/en/latest/userguide/connections.html#connection-urls

This Docker image supports using Redis and RabbitMQ as brokers.

Caveat: If the `MAYAN_BROKER_URL` and `MAYAN_CELERY_RESULT_BACKEND` environment
variables are specified, the built-in Redis server inside the container will
be disabled.

``MAYAN_CELERY_RESULT_BACKEND``

This optional environment variable determines the results backend that Celery
will use to relay result messages from the background workers to the frontend
code. For more information read the pertinent Celery Kombu documentation page:
`Task result backend settings`_

.. _Task result backend settings: http://docs.celeryproject.org/en/3.1/configuration.html#celery-result-backend

This Docker image supports using Redis and RabbitMQ as result backends.

Caveat: If the `MAYAN_BROKER_URL` and `MAYAN_CELERY_RESULT_BACKEND` environment
variables are specified, the built-in Redis server inside the container will
be disabled.

``MAYAN_SETTINGS_MODULE``

Optional. Allows loading an alternate settings file.


``MAYAN_DATABASE_CONN_MAX_AGE``

Amount in seconds to keep a database connection alive. Allow reuse of database
connections. For more information read the pertinent Django documentation
page: `Settings, CONN_MAX_AGE`_

.. _Settings, CONN_MAX_AGE: https://docs.djangoproject.com/en/1.10/ref/settings/#conn-max-age


``MAYAN_SETTINGS_FILE``

Optional. Previously only the ``local.py`` file was the only settings file
available to allow users to make configuration changes to their installations.
Now with this environment variable, users are free to create multiple settings
files and tell the Mayan EDMS container which setting file to import. The
only requirement is that the setting file starts with a global import of
``mayan.settings.production``. In the form::

    from mayan.settings.production import *


``MAYAN_GUNICORN_WORKERS``

Optional. This environment variable controls the number of frontend workers
that will be executed. If not specified the default is 2. For heavier loads,
user a higher number. A formula recommended for this setting is the number
of CPU cores + 1.

Accessing outside data
======================

To use Mayan EDMS's staging folders or watch folders from Docker, the data
for these source must be made accessible to the container. This is done by
mounting the folders in the host computer to folders inside the container.
This is necessary because Docker containers do not have access to host data
on purpose. For example, to make a folder in the host accessible as a watch
folder, add the following to the Docker command line when starting the
container::

    -v /opt/scanned_files:/srv/watch_folder

The command line would look like this::

    docker run ... -v /opt/scanned_files:/srv/watch_folder mayanedms/mayanedms:latest

Now create a watch folder in Mayan EDMS using the path ``/srv/watch_folder``
and the documents from the host folder ``/opt/scanned_files`` will be
automatically available. Use the same procedure to mount host folders to be
used as staging folderes. In this example ``/srv/watch_folder`` was as the
container directory, but any path can be used as long as it is not an
already existing path or a path used by any other program.


Performing backups
==================

To backup the existing data, stop the image and copy the content of the volume.
For the example::

    docker run -d --name mayan-edms --restart=always -p 80:8000 \
    -v /docker-volumes/mayan:/var/lib/mayan \
    -v /opt/scanned_files:/srv/watch_folder mayanedms/mayanedms:latest

That would be the ``/docker-volumes/mayan folder``::

    sudo tar -zcvf backup.tar.gz /docker-volumes/mayan
    sudo chown `whoami` backup.tar.gz

If using an external PostgreSQL or MySQL database or database containers, these
too need to be backed up using their respective procedures. A simple solution
is to copy the entire database container volume after the container has
been stopped.

Restoring from a backup
=======================

Uncompress the backup archive in the original docker volume using::

    sudo tar -xvzf backup.tar.gz -C /

Upgrading
=========

Upgrading a Mayan EDMS Docker container is actually a matter of stopping and
deleting the container, downloading the most recent version of the image and
starting a container again. The container will take care of updating the
database structure to the newest version if necessary.

**IMPORTANT!** Do not delete the volume storing the data, only the container.

Stop the container to be upgraded::

    docker stop mayan-edms


Remove the container::

    docker rm mayan-edms


Pull the new image version::

    docker pull mayanedms/mayanedms:latest


Start the container again with the new image version::

    docker run -d --name mayan-edms --restart=always -p 80:8000 -v /docker-volumes/mayan:/var/lib/mayan mayanedms/mayanedms:latest

Building the image
==================

Clone the repository with::

    git clone https://gitlab.com/mayan-edms/mayan-edms.git

Change to the directory of the cloned repository::

    cd mayan-edms

Execute Docker's build command using the provided makefile::

    make docker-build

Or using an apt cacher to speed up the build::

    make docker-build-with-proxy APT_PROXY=172.17.0.1:3142

Replace the IP address `172.17.0.1` with the IP address of the computer
running the APT proxy and caching service.

Customizing the image
=====================

Simple method
-------------

If you just need to add a few Ubuntu or Python packages to your installation,
you can use the following environment variables:

``MAYAN_APT_INSTALLS``

Specifies a list of Ubuntu .deb packages to be installed via APT when the
container is first created. The installed packages are not lost when the image
is stopped. Example: To install the Tesseract OCR language packs for German
and Spanish add the following in your ``docker start`` command line::

    -e MAYAN_APT_INSTALLS="tesseract-ocr-deu tesseract-ocr-spa"

``MAYAN_PIP_INSTALLS``

Specifies a list of Python packages to be installed via ``pip``. Packages will
be downloaded from the Python Package Index (https://pypi.python.org) by
default.

Using Docker compose
====================

To deploy a complete production stack using the included Docker compose file
execute::

    docker-compose -f docker-compose.yml up -d

This Docker compose file will provision four containers:

- Postgres as the database
- Redis as the Celery result storage
- RabbitMQ as the Celery broker
- Mayan EDMS using the above service containers

To stop the stack use::

    docker-compose -f docker-compose.yml stop

The stack will also create four volumes to store the data of each container.
These are:

- mayan_app - The Mayan EDMS data container, normally called `mayan_data` when not using Docker compose.
- mayan_broker - The broker volume, in this case RabbitMQ.
- mayan_db - The database volume, in this case Postgres.
- mayan_results - The celery result backend volume, in this case Redis.


Nightly images
==============
The continious integration pipeline used for testing development builds also
produces a resulting Docker image. These are build automatically and their
stability is not guaranteed. They should never be used in production.
If you want to try out the Docker images the development uses or want a sneak
peek at the new features being worked on checkout the container registry at:
https://gitlab.com/mayan-edms/mayan-edms/container_registry
