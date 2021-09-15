********
Settings
********

Mayan EDMS can be configure via environment variables or by setting files.


.. _environment_variables:

Via environment variables
=========================

To use environment variables, lookup the name of the setting you want to
override in the "Settings" menu. The "Settings" menu is located inside the
"Setup" main menu. To pass a value via an environment variable append
``"MAYAN_"`` to the name of the settings option. For example, to change
the number of documents displayed per page (COMMON_PAGINATE_BY, by default 40),
use::

    export MAYAN_COMMON_PAGINATE_BY=10

Restart Mayan EDMS and the new value will take effect. The "Settings" menu
can be used to verify if the overridden setting value is being interpreted
correctly.


.. _configuration_file:

Via YAML configuration file
===========================

.. versionadded:: 3.1

It is possible to modify the different settings by creating or editing the
``media/config.yml`` file. This file is formatted in the YAML markup language (
http://yaml.org/). Here is an example of what the looks like::

    DOCUMENT_PARSING_AUTO_PARSING: true
    DOCUMENT_PARSING_PDFTOTEXT_PATH: /usr/bin/pdftotext
    EMAIL_BACKEND: django.core.mail.backends.smtp.EmailBackend
    EMAIL_HOST: localhost
    EMAIL_HOST_PASSWORD: ''
    EMAIL_HOST_USER: ''
    EMAIL_PORT: 25
    EMAIL_TIMEOUT: null
    EMAIL_USE_SSL: false
    EMAIL_USE_TLS: false
    FILE_UPLOAD_MAX_MEMORY_SIZE: 2621440
    HOME_VIEW: common:home

Every time Mayan EDMS is able to start correctly it will copy the ``config.yml``
and create a backup copy in the same directory named ``config_backup.yml``.
This file is used to revert to the last know configuration file known
to be valid. You can revert manually by copy the file or by using the
``revertsettings`` management command from the command line.


Via Python settings files
=========================

Another way to configure Mayan EDMS is via Python-style, settings files.
If Mayan EDMS was installed using the Python package a ``mayan_settings``
folder will created for this purpose. If you installed Mayan EDMS
according to the :doc:`../chapters/deploying` instructions provided in this
documentation your ``mayan_settings`` folder should be located in the directory:
``/usr/share/mayan-edms/mayan/media/mayan_settings``.

If Mayan EDMS was installed using Docker, the ``mayan_settings`` folder
will be found inside the install Docker volume. If you installed Mayan EDMS
according to the :doc:`../chapters/docker` instructions provided in this
documentation your ``mayan_settings`` folder should be located in the directory:
``/docker-volumes/mayan/mayan_settings``.

Create a file with any valid name and a ``.py`` extension in the
``mayan_settings`` folder. The file must starts with a global import of
``mayan.settings.production``. In the form::

    from mayan.settings.production import *

Now add the corresponding lines to override the default settings.
In the settings file, it is not necessary to prepend the string ``MAYAN_`` to
the setting option. For example, to change the number of documents displayed
per page (COMMON_PAGINATE_BY, by default 40),
use::

    COMMON_PAGINATE_BY=10

versus::

    export MAYAN_COMMON_PAGINATE_BY=10

when using the environment variable method.

For this example let's assume the file was saved with the name ``mysettings.py``.

The way used to tell Mayan EDMS to import this file will vary based on the
installation method.

For the :doc:`../chapters/deploying` method, the full import path will be
``mayan.media.mayan_settings.mysettings`` and can be passed via the
``--settings`` command line argument like this::

    python manage.py runserver --settings=mayan.media.mayan_settings.mysettings

or via the ``DJANGO_SETTINGS_MODULE`` environment variable like this::

    export DJANGO_SETTINGS_MODULE=mayan.media.mayan_settings.mysettings

For the :doc:`../chapters/docker` installation method, the full import path will be
``mayan_settings.mysettings`` and can only be passed via the
``MAYAN_SETTINGS_MODULE`` environment variable like this::

    docker run <...> -e MAYAN_SETTINGS_MODULE=mayan_settings.mysettings
