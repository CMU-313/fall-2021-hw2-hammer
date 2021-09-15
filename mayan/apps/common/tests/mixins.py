from __future__ import unicode_literals

import glob
import os
import random

from furl import furl

from django.apps import apps
from django.conf import settings
from django.conf.urls import url
from django.contrib.contenttypes.models import ContentType
from django.core import management
from django.db import connection. models
from django.db.models.signals import post_save, pre_save
from django.http import HttpResponse
from django.template import Context, Template
from django.test.utils import ContextList
from django.urls import clear_url_caches, reverse
from django.utils.encoding import force_bytes

from mayan.apps.storage.settings import setting_temporary_directory

from .literals import TEST_VIEW_NAME, TEST_VIEW_URL
from .utils import mute_stdout


if getattr(settings, 'COMMON_TEST_FILE_HANDLES', False):
    import psutil


class ClientMethodsTestCaseMixin(object):
    def _build_verb_kwargs(self, viewname=None, path=None, *args, **kwargs):
        data = kwargs.pop('data', {})
        follow = kwargs.pop('follow', False)
        query = kwargs.pop('query', {})

        if viewname:
            path = reverse(viewname=viewname, *args, **kwargs)

        path = furl(url=path)
        path.args.update(query)

        return {'follow': follow, 'data': data, 'path': path.tostr()}

    def delete(self, viewname=None, path=None, *args, **kwargs):
        return self.client.delete(
            **self._build_verb_kwargs(
                path=path, viewname=viewname, *args, **kwargs
            )
        )

    def get(self, viewname=None, path=None, *args, **kwargs):
        return self.client.get(
            **self._build_verb_kwargs(
                path=path, viewname=viewname, *args, **kwargs
            )
        )

    def patch(self, viewname=None, path=None, *args, **kwargs):
        return self.client.patch(
            **self._build_verb_kwargs(
                path=path, viewname=viewname, *args, **kwargs
            )
        )

    def post(self, viewname=None, path=None, *args, **kwargs):
        return self.client.post(
            **self._build_verb_kwargs(
                path=path, viewname=viewname, *args, **kwargs
            )
        )

    def put(self, viewname=None, path=None, *args, **kwargs):
        return self.client.put(
            **self._build_verb_kwargs(
                path=path, viewname=viewname, *args, **kwargs
            )
        )


class ContentTypeCheckMixin(object):
    expected_content_type = 'text/html; charset=utf-8'

    def _pre_setup(self):
        super(ContentTypeCheckMixin, self)._pre_setup()
        test_instance = self

        class CustomClient(self.client_class):
            def request(self, *args, **kwargs):
                response = super(CustomClient, self).request(*args, **kwargs)

                content_type = response._headers.get('content-type', [None, ''])[1]
                if test_instance.expected_content_type:
                    test_instance.assertEqual(
                        content_type, test_instance.expected_content_type,
                        msg='Unexpected response content type: {}, expected: {}.'.format(
                            content_type, test_instance.expected_content_type
                        )
                    )

                return response

        self.client = CustomClient()


class DatabaseConversionMixin(object):
    def _test_database_conversion(self, *app_labels):
        with mute_stdout():
            management.call_command(
                'convertdb', *app_labels, force=True
            )


class OpenFileCheckTestCaseMixin(object):
    def _get_descriptor_count(self):
        process = psutil.Process()
        return process.num_fds()

    def _get_open_files(self):
        process = psutil.Process()
        return process.open_files()

    def setUp(self):
        super(OpenFileCheckTestCaseMixin, self).setUp()
        if getattr(settings, 'COMMON_TEST_FILE_HANDLES', False):
            self._open_files = self._get_open_files()

    def tearDown(self):
        if getattr(settings, 'COMMON_TEST_FILE_HANDLES', False) and not getattr(self, '_skip_file_descriptor_test', False):
            for new_open_file in self._get_open_files():
                self.assertFalse(
                    new_open_file not in self._open_files,
                    msg='File descriptor leak. The number of file descriptors '
                    'at the start and at the end of the test are not the same.'
                )

            self._skip_file_descriptor_test = False

        super(OpenFileCheckTestCaseMixin, self).tearDown()


class RandomPrimaryKeyModelMonkeyPatchMixin(object):
    random_primary_key_random_floor = 100
    random_primary_key_random_ceiling = 10000
    random_primary_key_maximum_attempts = 100

    @staticmethod
    def get_unique_primary_key(model):
        pk_list = model._meta.default_manager.values_list('pk', flat=True)

        attempts = 0
        while True:
            primary_key = random.randint(
                RandomPrimaryKeyModelMonkeyPatchMixin.random_primary_key_random_floor,
                RandomPrimaryKeyModelMonkeyPatchMixin.random_primary_key_random_ceiling
            )

            if primary_key not in pk_list:
                break

            attempts = attempts + 1

            if attempts > RandomPrimaryKeyModelMonkeyPatchMixin.random_primary_key_maximum_attempts:
                raise Exception(
                    'Maximum number of retries for an unique random primary '
                    'key reached.'
                )

        return primary_key

    def setUp(self):
        self.method_save_original = models.Model.save

        def method_save_new(instance, *args, **kwargs):
            if instance.pk:
                return self.method_save_original(instance, *args, **kwargs)
            else:
                # Set meta.auto_created to True to have the original save_base
                # not send the pre_save signal which would normally send
                # the instance without a primary key. Since we assign a random
                # primary key any pre_save signal handler that relies on an 
                # empty primary key will fail.
                # The meta.auto_created and manual pre_save sending emulates
                # the original behavior. Since meta.auto_created also disables
                # the post_save signal we must also send it ourselves.
                # This hack work with Django 1.11 .save_base() but can break
                # in future versions if that method is updated.
                pre_save.send(
                    sender=instance.__class__, instance=instance, raw=False,
                    update_fields=None,
                )
                instance._meta.auto_created = True
                instance.pk = RandomPrimaryKeyModelMonkeyPatchMixin.get_unique_primary_key(
                    model=instance._meta.model
                )
                instance.id = instance.pk

                result = instance.save_base(force_insert=True)
                instance._meta.auto_created = False
                
                post_save.send(
                    sender=instance.__class__, instance=instance, created=True,
                    update_fields=None, raw=False
                )

                return result

        setattr(models.Model, 'save', method_save_new)
        super(RandomPrimaryKeyModelMonkeyPatchMixin, self).setUp()

    def tearDown(self):
        models.Model.save = self.method_save_original
        super(RandomPrimaryKeyModelMonkeyPatchMixin, self).tearDown()


class TempfileCheckTestCaseMixin(object):
    # Ignore the jvmstat instrumentation and GitLab's CI .config files
    # Ignore LibreOffice fontconfig cache dir
    ignore_globs = ('hsperfdata_*', '.config', '.cache')

    def _get_temporary_entries(self):
        ignored_result = []

        # Expand globs by joining the temporary directory and then flattening
        # the list of lists into a single list
        for item in self.ignore_globs:
            ignored_result.extend(
                glob.glob(
                    os.path.join(setting_temporary_directory.value, item)
                )
            )

        # Remove the path and leave only the expanded filename
        ignored_result = map(lambda x: os.path.split(x)[-1], ignored_result)

        return set(
            os.listdir(setting_temporary_directory.value)
        ) - set(ignored_result)

    def setUp(self):
        super(TempfileCheckTestCaseMixin, self).setUp()
        if getattr(settings, 'COMMON_TEST_TEMP_FILES', False):
            self._temporary_items = self._get_temporary_entries()

    def tearDown(self):
        if getattr(settings, 'COMMON_TEST_TEMP_FILES', False):
            final_temporary_items = self._get_temporary_entries()
            self.assertEqual(
                self._temporary_items, final_temporary_items,
                msg='Orphan temporary file. The number of temporary files and/or '
                'directories at the start and at the end of the test are not the '
                'same. Orphan entries: {}'.format(
                    ','.join(final_temporary_items - self._temporary_items)
                )
            )
        super(TempfileCheckTestCaseMixin, self).tearDown()


class TestModelTestMixin(object):
    def _create_test_model(self, fields=None, model_name='TestModel', options=None):
        # Obtain the app_config and app_label from the test's module path
        app_config = apps.get_containing_app_config(
            object_name=self.__class__.__module__
        )
        app_label = app_config.label

        class Meta:
            pass

        setattr(Meta, 'app_label', app_label)

        if options is not None:
            for key, value in options.items():
                setattr(Meta, key, value)

        def save(instance, *args, **kwargs):
            # Custom .save() method to use random primary key values.
            if instance.pk:
                return models.Model.self(instance, *args, **kwargs)
            else:
                instance.pk = RandomPrimaryKeyModelMonkeyPatchMixin.get_unique_primary_key(
                    model=instance._meta.model
                )
                instance.id = instance.pk

                return instance.save_base(force_insert=True)

        attrs = {
            '__module__': self.__class__.__module__, 'save': save, 'Meta': Meta
        }

        if fields:
            attrs.update(fields)

        # Clear previous model registration before re-registering it again to
        # avoid conflict with test models with the same name, in the same app
        # but from another test module.
        apps.all_models[app_label].pop(model_name.lower(), None)

        TestModel = type(
            force_bytes(model_name), (models.Model,), attrs
        )

        setattr(self, model_name, TestModel)

        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(model=TestModel)

        ContentType.objects.clear_cache()

    def _create_test_object(self, model_name='TestModel', **kwargs):
        TestModel = getattr(self, model_name)

        self.test_object = TestModel.objects.create(**kwargs)


class TestViewTestCaseMixin(object):
    has_test_view = False

    def tearDown(self):
        from mayan.urls import urlpatterns

        self.client.logout()
        if self.has_test_view:
            urlpatterns.pop(0)
        super(TestViewTestCaseMixin, self).tearDown()

    def add_test_view(self, test_object):
        from mayan.urls import urlpatterns

        def test_view(request):
            template = Template('{{ object }}')
            context = Context(
                {'object': test_object, 'resolved_object': test_object}
            )
            return HttpResponse(template.render(context=context))

        urlpatterns.insert(0, url(TEST_VIEW_URL, test_view, name=TEST_VIEW_NAME))
        clear_url_caches()
        self.has_test_view = True

    def get_test_view(self):
        response = self.get(TEST_VIEW_NAME)
        if isinstance(response.context, ContextList):
            # template widget rendering causes test client response to be
            # ContextList rather than RequestContext. Typecast to dictionary
            # before updating.
            result = dict(response.context).copy()
            result.update({'request': response.wsgi_request})
            return Context(result)
        else:
            response.context.update({'request': response.wsgi_request})
            return Context(response.context)
