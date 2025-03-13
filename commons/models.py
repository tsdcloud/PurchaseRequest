from bson import ObjectId
import uuid
import os

from datetime import timezone

from django.db import models
from django.contrib.auth.models import AbstractUser, Permission, Group, UserManager
from django.utils.translation import gettext_lazy as _
from django.conf import settings


def get_object_id():
    """Generates a string version of bson ObjectId."""
    # return str(ObjectId())
    return str(uuid.uuid4())


def add_database_to_settings(db_url):
    """
    Adds a database connection to the global settings on the fly.
    That is equivalent to do the following in Django settings file:

    DATABASES = {
        'default': {
            'ENGINE': 'current_database_engine',
            'NAME': 'default_database',
            ...
        },
        'alias': {
            'ENGINE': 'engine_in_db_info',
            'NAME': database,
            ...
        }
    }

    That connection is named 'database'
    @param db_url: string representing database under the form engine://<username>:<password>@<host>[:<port>]/database
    """
    # Defaults
    engine = getattr(settings, 'DATABASES')['default']['ENGINE']
    host = getattr(settings, 'DATABASES')['default'].get('HOST', '127.0.0.1')
    port = getattr(settings, 'DATABASES')['default'].get('PORT')
    username = getattr(settings, 'DATABASES')['default'].get('USER')
    password = getattr(settings, 'DATABASES')['default'].get('PASSWORD')

    tokens = db_url.strip().split('://')
    if len(tokens) == 1:
        alias = tokens[0]
    else:
        engine = tokens[0]
        db_tokens = tokens[1].split('/')
        if len(db_tokens) == 1:
            alias = db_tokens[0]
        else:
            access = db_tokens[0]
            alias = db_tokens[1]
            access_tokens = access.split('@')
            credentials = access_tokens[0].split(':')
            location = access_tokens[1].split(':')
            username = credentials[0]
            password = credentials[1]
            host = location[0]
            if len(location) > 1:
                port = location[1]
    DATABASES = getattr(settings, 'DATABASES')
    if DATABASES.get(alias) is None:  # If this alias was not yet added
        name = alias
        if engine == 'sqlite':
            engine = 'django.db.backends.sqlite3'
            name = os.path.join(getattr(settings, 'BASE_DIR'), '%s.sqlite3' % alias)
        elif engine == 'mysql':
            engine = 'django.db.backends.mysql'
        elif engine == 'postgres':
            engine = 'django.db.backends.postgresql_psycopg2'
        elif engine == 'oracle':
            engine = 'django.db.backends.oracle'
        DATABASES[alias] = {
            'ENGINE': engine,
            'NAME': name,
            'HOST': host
        }
        if port:
            DATABASES[alias]['PORT'] = port
        if username:
            DATABASES[alias]['USER'] = username
            DATABASES[alias]['PASSWORD'] = password
    setattr(settings, 'DATABASES', DATABASES)
    return alias


class BaseAdapterModel(models.Model):
    """
    This abstract model uses id as a string version of
    bson ObjectId. This is done to support models coming
    from the MongoDB storage; so those models must inherit
    this class to work properly.
    """
    id = models.CharField(max_length=255, primary_key=True, default=get_object_id, editable=True)

    class Meta:
        abstract = True


class BaseModel(models.Model):
    """
    Helper base Model that defines two fields: created_on and updated_on.
    Both are DateTimeField. updated_on automatically receives the current
    datetime whenever the model is updated in the database
    """
    created_on = models.DateTimeField(auto_now_add=True, null=True, editable=False, db_index=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, db_index=True)

    class Meta:
        abstract = True

    # def save(self, **kwargs):
    #     for field in self._meta.fields:
    #         if type(field) == JSONField and isinstance(self.__getattribute__(field.name), models.Model):
    #             self.__setattr__(field.name, to_dict(self.__getattribute__(field.name), False))
    #     super(BaseModel, self).save(**kwargs)

    def _get_display_date(self):
        if not self.created_on:
            return ''
        now = timezone.now()
        if self.created_on.year == now.year and self.created_on.month == now.month \
                and self.created_on.day == now.day:
            return self.created_on.strftime('%H:%M')
        return self.created_on.strftime('%Y-%m-%d')
    display_date = property(_get_display_date)


class TrashQuerySet(models.QuerySet):
    """
    QuerySet whose delete() does not delete items, but instead marks the
    rows as not active, and updates the timestamps
    """
    def delete(self):
        count = self.count()
        for obj in self:
            obj.delete()
        return count


class TrashManager(models.Manager):
    def get_queryset(self):
        return TrashQuerySet(self.model, using=self._db)


class TrashMixin(models.Model):
    objects = TrashManager()

    class Meta:
        abstract = True

    def delete(self, **kwargs):
        try:
            TrashModel.objects.create(model_name=self._meta.label, data=self.to_dict())
        except:
            pass
        super(TrashMixin, self).delete(**kwargs)


def add_database_to_settings(db_url):
    """
    Adds a database connection to the global settings on the fly.
    That is equivalent to do the following in Django settings file:

    DATABASES = {
        'default': {
            'ENGINE': 'current_database_engine',
            'NAME': 'default_database',
            ...
        },
        'alias': {
            'ENGINE': 'engine_in_db_info',
            'NAME': database,
            ...
        }
    }

    That connection is named 'database'
    @param db_url: string representing database under the form engine://<username>:<password>@<host>[:<port>]/database
    """
    # Defaults
    engine = getattr(settings, 'DATABASES')['default']['ENGINE']
    host = getattr(settings, 'DATABASES')['default'].get('HOST', '127.0.0.1')
    port = getattr(settings, 'DATABASES')['default'].get('PORT')
    username = getattr(settings, 'DATABASES')['default'].get('USER')
    password = getattr(settings, 'DATABASES')['default'].get('PASSWORD')

    tokens = db_url.strip().split('://')
    if len(tokens) == 1:
        alias = tokens[0]
    else:
        engine = tokens[0]
        db_tokens = tokens[1].split('/')
        if len(db_tokens) == 1:
            alias = db_tokens[0]
        else:
            access = db_tokens[0]
            alias = db_tokens[1]
            access_tokens = access.split('@')
            credentials = access_tokens[0].split(':')
            location = access_tokens[1].split(':')
            username = credentials[0]
            password = credentials[1]
            host = location[0]
            if len(location) > 1:
                port = location[1]
    DATABASES = getattr(settings, 'DATABASES')
    if DATABASES.get(alias) is None:  # If this alias was not yet added
        name = alias
        if engine == 'sqlite':
            engine = 'django.db.backends.sqlite3'
            name = os.path.join(getattr(settings, 'BASE_DIR'), '%s.sqlite3' % alias)
        elif engine == 'mysql':
            engine = 'django.db.backends.mysql'
        elif engine == 'postgres':
            engine = 'django.db.backends.postgresql_psycopg2'
        elif engine == 'oracle':
            engine = 'django.db.backends.oracle'
        DATABASES[alias] = {
            'ENGINE': engine,
            'NAME': name,
            'HOST': host
        }
        if port:
            DATABASES[alias]['PORT'] = port
        if username:
            DATABASES[alias]['USER'] = username
            DATABASES[alias]['PASSWORD'] = password
    setattr(settings, 'DATABASES', DATABASES)
    return alias


class Model(BaseAdapterModel, BaseModel):
    """
    Helper base Model that creates a model suitable for save in MongoDB
    with fields created_on and updated_on.
    """

    def get_from(self, db):
        add_database_to_settings(db)
        return type(self).objects.using(db).get(pk=self.id)

    class Meta:
        abstract = True


class TrashModel(Model):
    model_name = models.CharField(max_length=100, db_index=True)
    data = models.JSONField()


class BaseUUIDModel(BaseModel, TrashMixin):
    """Base model using UUID4 as primary key"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)

    class Meta:
        abstract = True


class Department(models.Model):
    name = models.CharField(_("Name"), max_length=150)
    acronym = models.CharField(_("Acronym"), max_length=10)


class Position(models.Model):
    name = models.CharField(_("Name"), max_length=150)
    acronym = models.CharField(_("Acronym"), max_length=10)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL)


class Member(BaseUUIDModel, AbstractUser):
    """
    Member class in charge of managing users.
    """
    position = models.ForeignKey(Position, _("Title of position"), max_length=10)


# class Applica(BaseUUIDModel, AbstractUser):
#     """
#     Member class in charge of managing users.
#     """
#     position = models.ForeignKey(Position, _("Title of position"), max_length=10)



