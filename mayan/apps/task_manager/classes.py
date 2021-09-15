import logging

from kombu import Exchange, Queue

from django.utils.encoding import force_text
from django.utils.module_loading import import_string

from mayan.apps.common.class_mixins import AppsModuleLoaderMixin
from mayan.celery import app as celery_app

logger = logging.getLogger(name=__name__)


class TaskType:
    _registry = {}

    @classmethod
    def all(cls):
        return cls._registry.values()

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    def __init__(self, dotted_path, label, name=None, schedule=None):
        self.name = name or dotted_path.split('.')[-1]
        self.label = label
        self.dotted_path = dotted_path
        self.schedule = schedule
        self.__class__._registry[name] = self
        self.validate()

    def __str__(self):
        return force_text(self.label)

    def validate(self):
        try:
            import_string(dotted_path=self.dotted_path)
        except Exception as exception:
            logger.critical(
                'Exception validating task %s; %s', self.label, exception,
                exc_info=True
            )
            raise


class Task:
    def __init__(self, task_type, kwargs):
        self.task_type = task_type
        self.kwargs = kwargs

    def __str__(self):
        return force_text(self.task_type)


class CeleryQueue(AppsModuleLoaderMixin):
    _loader_module_name = 'queues'
    _registry = {}

    @classmethod
    def all(cls):
        return sorted(
            cls._registry.values(), key=lambda instance: instance.label
        )

    @classmethod
    def get(cls, queue_name):
        return cls._registry[queue_name]

    @classmethod
    def load_modules(cls):
        super().load_modules()
        CeleryQueue.update_celery()

    @classmethod
    def update_celery(cls):
        for instance in cls.all():
            instance._update_celery()

    def __init__(self, name, label, worker, default_queue=False, transient=False):
        self.name = name
        self.label = label
        self.default_queue = default_queue
        self.transient = transient
        self.task_types = []
        self.__class__._registry[name] = self
        worker.queues.append(self)

    def __str__(self):
        return force_text(self.label)

    def _process_task_dictionary(self, task_dictionary):
        result = []
        for worker, tasks in task_dictionary.items():
            for task in tasks:
                if task['delivery_info']['routing_key'] == self.name:
                    task_type = TaskType.get(name=task['name'])
                    result.append(Task(task_type=task_type, kwargs=task))

        return result

    def add_task_type(self, *args, **kwargs):
        task_type = TaskType(*args, **kwargs)
        self.task_types.append(task_type)
        return task_type

    def _update_celery(self):
        kwargs = {
            'name': self.name, 'exchange': Exchange(self.name),
            'routing_key': self.name
        }

        if self.transient:
            kwargs['delivery_mode'] = 1

        celery_app.conf.task_queues.append(Queue(**kwargs))

        if self.default_queue:
            celery_app.conf.task_default_queue = self.name

        for task_type in self.task_types:
            celery_app.conf.task_routes.update(
                {
                    task_type.dotted_path: {
                        'queue': self.name
                    },
                }
            )

            if task_type.schedule:
                celery_app.conf.beat_schedule.update(
                    {
                        task_type.name: {
                            'task': task_type.dotted_path,
                            'schedule': task_type.schedule
                        },
                    }
                )


class Worker:
    _registry = {}

    @classmethod
    def all(cls):
        return cls._registry.values()

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    def __init__(self, name, label=None, nice_level=0):
        self.name = name
        self.label = label
        self.nice_level = nice_level
        self.queues = []
        self.__class__._registry[name] = self
