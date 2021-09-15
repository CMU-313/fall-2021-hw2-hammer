from contextlib import contextmanager
import sys

from django.utils.encoding import force_text


class NullFile:
    def write(self, string):
        """Writes here go nowhere"""


def as_id_list(items):
    return ','.join(
        [force_text(s=item.pk) for item in items]
    )


@contextmanager
def mute_stdout():
    stdout_old = sys.stdout
    sys.stdout = NullFile()
    yield
    sys.stdout = stdout_old
