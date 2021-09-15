============
Docker image
============

How to use this image
=====================

.. _docker_install:

Start a Mayan EDMS Docker image
-------------------------------

With Docker properly installed, proceed to download the Mayan EDMS image using
the command::

    docker pull mayanedms/mayanedms:<version>

Instead of a specific version tag you may use then generic ``:latest`` tag
to the get latest version available automatically. If you use the ``:latest``
tag here, remember to do so in the next steps also.::

    docker pull mayanedms/mayanedms:latest

Then download version 9.6 of the Docker PostgreSQL image::

    docker pull postgres:9.6

Create and run a PostgreSQL container::

    docker run -d \
    --name mayan-edms-postgres \
    --restart=always \
    -p 5432:5432 \
    -e POSTGRES_USER=mayan \
    -e POSTGRES_DB=mayan \
    -e POSTGRES_PASSWORD=mayanuserpass \
    -v /docker-volumes/mayan-edms/postgres:/var/lib/postgresql/data \
    -d postgres:9.6

The PostgreSQL container will have one database named ``mayan``, with an user
named ``mayan`` too, with a password of ``mayanuserpass``. The container will
expose its internal 5432 port (PostgreSQL's default port) via the host's
5432 port. The data of this container will reside on the host's
``/docker-volumes/mayan-edms/postgres`` folder.

Finally create and run a Mayan EDMS container::

    docker run -d \
    --name mayan-edms \
    --restart=always \
    -p 80:8000 \
    -e MAYAN_DATABASES="{'default':{'ENGINE':'django.db.backends.postgresql','NAME':'mayan','PASSWORD':'mayanuserpass','USER':'mayan','HOST':'172.17.0.1'}}" \
    -v /docker-volumes/mayan-edms/media:/var/lib/mayan \
    mayanedms/mayanedms:<version>

The Mayan EDMS container will connect to the PostgreSQL container via the
``172.17.0.1`` IP address (the Docker host's default IP address). It will
connect using the ``django.db.backends.postgresql`` database driver and
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


Using a dedicated Docker network
--------------------------------

Use this method to avoid having to expose PostreSQL port to the host's network
or if you have other PostgreSQL instances but still want to use the default
port of 5432 for this installation.

Create the network::

    docker network create mayan

Launch the PostgreSQL container with the network option and remove the port
binding (``-p 5432:5432``)::

    docker run -d \
    --name mayan-edms-postgres \
    --network=mayan \
    --restart=always \
    -e POSTGRES_USER=mayan \
    -e POSTGRES_DB=mayan \
    -e POSTGRES_PASSWORD=mayanuserpass \
    -v /docker-volumes/mayan-edms/postgres:/var/lib/postgresql/data \
    -d postgres:9.6

Launch the Mayan EDMS container with the network option and change the
database hostname to the PostgreSQL container name (``mayan-edms-postgres``)
instead of the IP address of the Docker host (``172.17.0.1``)::

    docker run -d \
    --name mayan-edms \
    --network=mayan \
    --restart=always \
    -p 80:8000 \
    -e MAYAN_DATABASES="{'default':{'ENGINE':'django.db.backends.postgresql','NAME':'mayan','PASSWORD':'mayanuserpass','USER':'mayan','HOST':'mayan-edms-postgres'}}" \
    -v /docker-volumes/mayan-edms/media:/var/lib/mayan \
    mayanedms/mayanedms:<version>


Stopping and starting the container
-----------------------------------

To stop the container use::

    docker stop mayan-edms


To start the container again::

    docker start mayan-edms


.. _docker_environment_variables:


Environment Variables
---------------------

The common set of settings can also be modified via environment variables when
using the Docker image. In addition to the common set of settings, some Docker
image specific environment variables are available.

``MAYAN_SETTINGS_MODULE``

Optional. Allows loading an alternate settings file.


``MAYAN_GUNICORN_TIMEOUT``

Optional. Changes the amount of time the frontend worker will wait for a
request to finish before raising a timeout error. The default is 120
seconds.

``MAYAN_GUNICORN_WORKERS``

Optional. This environment variable controls the number of frontend workers
that will be executed. If not specified the default is 2. For heavier loads,
user a higher number. A formula recommended for this setting is the number
of CPU cores + 1.

``MAYAN_WORKER_FAST_CONCURRENCY``

Optional. Changes the concurrency (number of child processes) of the Celery
worker consuming the queues in the fast (low latency, short tasks) category.
Default is 1. Use 0 to disable hardcoded concurrency and allow the Celery
worker to launch its default number of child processes (equal to the number
of CPUs detected).

``MAYAN_WORKER_MEDIUM_CONCURRENCY``

Optional. Changes the concurrency (number of child processes) of the Celery
worker consuming the queues in the medium (medium latency, long running tasks)
category. Default is 1. Use 0 to disable hardcoded concurrency and allow the
Celery worker to launch its default number of child processes (equal to the
number of CPUs detected).

``MAYAN_WORKER_SLOW_CONCURRENCY``

Optional. Changes the concurrency (number of child processes) of the Celery
worker consuming the queues in the slow (high latency, very long running tasks)
category. Default is 1. Use 0 to disable hardcoded concurrency and allow the
Celery worker to launch its default number of child processes (equal to the
number of CPUs detected).

``MAYAN_USER_UID``

Optional. Changes the UID of the ``mayan`` user internal to the Docker
container. Defaults to 1000.

``MAYAN_USER_GID``

Optional. Changes the GID of the ``mayan`` user internal to the Docker
container. Defaults to 1000.


Included drivers
----------------

The Docker image supports using Redis and RabbitMQ as result backends. For
databases, the image includes support for PostgreSQL and MySQL/MariaDB.
Support for additional brokers or databases may be added using the
``MAYAN_APT_INSTALL`` environment variable.


.. _docker-accessing-outside-data:

Accessing outside data
======================

To use Mayan EDMS's staging folders or watch folders from Docker, the data
for these source must be made accessible to the container. This is done by
mounting the folders in the host computer to folders inside the container.
This is necessary because Docker containers do not have access to host data
on purpose. For example, to make a folder in the host accessible as a watch
folder, add the following to the Docker command line when starting the
container::

    -v /opt/scanned_files:/scanned_files

The command line would look like this::

    docker run ... -v /opt/scanned_files:/scanned_files mayanedms/mayanedms:latest

Now create a watch folder in Mayan EDMS using the path ``/scanned_files``
and the documents from the host folder ``/opt/scanned_files`` will be
automatically available. Use the same procedure to mount host folders to be
used as staging folders. In this example ``/scanned_files`` was used as the
container directory, but any path can be used as long as:

- the path not an already existing path
- the path is not used by any other program
- the path is a single level path


Performing backups
==================

To backup the existing data, stop the image and copy the content of the volume.
For the example::

    docker run -d --name mayan-edms --restart=always -p 80:8000 \
    -v /docker-volumes/mayan:/var/lib/mayan \
    -v /opt/scanned_files:/scanned_files mayanedms/mayanedms:latest

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

Or using an APT cache to speed up the build::

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

The continuous integration pipeline used for testing development builds also
produces a resulting Docker image. These are build automatically and their
stability is not guaranteed. They should never be used in production.
If you want to try out the Docker images the development uses or want a sneak
peek at the new features being worked on checkout the container registry at:
https://gitlab.com/mayan-edms/mayan-edms/container_registry
