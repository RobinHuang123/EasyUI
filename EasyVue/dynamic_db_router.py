"""
https://github.com/ambitioninc/django-dynamic-db-router/blob/master/LICENSE

The MIT License (MIT)

Copyright (c) 2015 Ambition

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import threading
from functools import wraps
from uuid import uuid4

from django.db import connections

THREAD_LOCAL = threading.local()


class DynamicDbRouter(object):
    """A router that decides what db to read from based on a variable
    local to the current thread.
    """

    def db_for_read(self, model, **hints):
        return getattr(THREAD_LOCAL, 'DB_FOR_READ_OVERRIDE', ['default'])[-1]

    def db_for_write(self, model, **hints):
        return getattr(THREAD_LOCAL, 'DB_FOR_WRITE_OVERRIDE', ['default'])[-1]

    def allow_relation(self, *args, **kwargs):
        return True

    def allow_syncdb(self, *args, **kwargs):
        return None

    def allow_migrate(self, *args, **kwargs):
        return None


class in_database(object):
    """A decorator and context manager to do queries on a given database.
    :type database: str or dict
    :param database: The database to run queries on. A string
        will route through the matching database in
        ``django.conf.settings.DATABASES``. A dictionary will set up a
        connection with the given configuration and route queries to it.
    :type read: bool, optional
    :param read: Controls whether database reads will route through
        the provided database. If ``False``, reads will route through
        the ``'default'`` database. Defaults to ``True``.
    :type write: bool, optional
    :param write: Controls whether database writes will route to
        the provided database. If ``False``, writes will route to
        the ``'default'`` database. Defaults to ``False``.
    When used as eithe a decorator or a context manager, `in_database`
    requires a single argument, which is the name of the database to
    route queries to, or a configuration dictionary for a database to
    route to.
    Usage as a context manager:
    .. code-block:: python
        from my_django_app.utils import tricky_query
        with in_database('Database_A'):
            results = tricky_query()
    Usage as a decorator:
    .. code-block:: python
        from my_django_app.models import Account
        @in_database('Database_B')
        def lowest_id_account():
            Account.objects.order_by('-id')[0]
    Used with a configuration dictionary:
    .. code-block:: python
        db_config = {'ENGINE': 'django.db.backends.sqlite3',
                     'NAME': 'path/to/mydatabase.db'}
        with in_database(db_config):
            # Run queries
    """
    def __init__(self, database, read=True, write=False):
        self.read = read
        self.write = write
        self.created_db_config = False
        if isinstance(database, str):
            self.database = database
        elif isinstance(database, dict):
            # Note: this invalidates the docs above. Update them
            # eventually.
            self.created_db_config = True
            self.unique_db_id = str(uuid4())
            connections.databases[self.unique_db_id] = database
            self.database = self.unique_db_id
        else:
            msg = ("database must be an identifier for an existing db, "
                   "or a complete configuration.")
            raise ValueError(msg)

    def __enter__(self):
        if not hasattr(THREAD_LOCAL, 'DB_FOR_READ_OVERRIDE'):
            THREAD_LOCAL.DB_FOR_READ_OVERRIDE = ['default']
        if not hasattr(THREAD_LOCAL, 'DB_FOR_WRITE_OVERRIDE'):
            THREAD_LOCAL.DB_FOR_WRITE_OVERRIDE = ['default']
        read_db = (self.database if self.read
                   else THREAD_LOCAL.DB_FOR_READ_OVERRIDE[-1])
        write_db = (self.database if self.write
                    else THREAD_LOCAL.DB_FOR_WRITE_OVERRIDE[-1])
        THREAD_LOCAL.DB_FOR_READ_OVERRIDE.append(read_db)
        THREAD_LOCAL.DB_FOR_WRITE_OVERRIDE.append(write_db)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        THREAD_LOCAL.DB_FOR_READ_OVERRIDE.pop()
        THREAD_LOCAL.DB_FOR_WRITE_OVERRIDE.pop()
        if self.created_db_config:
            connections[self.unique_db_id].close()
            del connections.databases[self.unique_db_id]

    def __call__(self, querying_func):
        @wraps(querying_func)
        def inner(*args, **kwargs):
            # Call the function in our context manager
            with self:
                return querying_func(*args, **kwargs)
        return inner


# create alias
DynamicDB = in_database
