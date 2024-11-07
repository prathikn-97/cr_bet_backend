from builtins import Exception, print, dict, type
from django.apps import apps
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone

from .error import BaseError


class CustomBaseConfig:
    attr = {}

    @classmethod
    def _app_config(cls):
        if cls.app_name is not None:
            try:
                cls.app_config = apps.get_app_config(cls.app_name)
            except Exception as error:
                print(error)
                ref = {"type": "model", "table_name": ""}

                if cls.__dict__.get('attr') is not None:
                    if cls.__dict__.get('attr').get('db_table') is not None:
                        ref["table_name"] = cls.__dict__.get(
                            'attr').get('db_table')

                BaseError.unmet_dependency(
                    message="App with provided app name is not found!",
                    details={"app_name": cls.app_name, "ref": ref}
                )
        else:
            ref = {"type": "model", "table_name": ""}
            if cls.__dict__.get('attr') is not None:
                if cls.__dict__.get('attr').get('db_table') is not None:
                    ref["table_name"] = cls.__dict__.get(
                        'attr').get('db_table')

                    BaseError.unmet_dependency(
                        message="app name is not provided in the model Mata Class!",
                        details={"app_name": cls.app_config.name, "ref": ref}
                    )

            BaseError.unmet_dependency(
                message="table prefix is not defined in the app config!",
                details={"app_name": cls.app_config.name, "ref": ref}
            )

    """
        Set the necessary class vars for the current class
    """

    @classmethod
    def _cls_app_vars(cls):
        try:
            cls._table = dict({"prefix": cls.app_config.table["prefix"]})
        except Exception as e:
            BaseError.unmet_dependency(
                message="table prefix is not defined in the app config!",
                details={"app_name": cls.app_config.name},
                error=e
            )

    """
        Init the current config class
    """

    @classmethod
    def init(cls):
        cls._app_config()
        cls._cls_app_vars()

    """
        Set the table name for the model with prefix provided by the app config
    """

    @classmethod
    def _set_table_name(cls, name):
        try:
            cls.attr["db_table"] = cls._table["prefix"] + "_" + name
        except Exception as e:
            BaseError.unmet_dependency(
                message="init method for the class has not been called!",
                details={"class": {"name": "CustomBaseConfig"}},
                error=e,
                extra={"cls": cls}
            )

    """
        Get the table name for the model
    """

    @classmethod
    def _get_table_name(cls):
        try:
            return cls.attr["db_table"]
        except Exception as e:
            BaseError.unmet_dependency(
                message="_set_table_name method for the class has not been called!",
                details={"class": {"name": "CustomBaseConfig", }},
                error=e,
                extra={"cls": cls}
            )


class BaseModelMeta(CustomBaseConfig):
    @classmethod
    def __new__(cls, *args, **kwargs):
        cls._set_class_vars(kwargs)

        return type("Meta", cls.bases, cls.attr)

    @classmethod
    def _set_class_vars(cls, kwargs):
        cls.kwargs = kwargs
        cls._set_class_bases()
        cls._set_app_name()
        cls._set_attr()

    @classmethod
    def _set_class_bases(cls):
        cls.bases = cls.kwargs["bases"] if 'bases' in cls.kwargs else ()

    @classmethod
    def _set_app_name(cls):
        cls.app_name = cls.kwargs["app_name"] if 'app_name' in cls.kwargs else None

    @classmethod
    def _set_attr(cls):
        cls.attr = cls.kwargs["attr"] if 'attr' in cls.kwargs else {}
        cls._set_attr_table_name()

    @classmethod
    def _set_attr_table_name(cls):
        if 'db_table' in cls.attr:
            cls.init()
            cls._set_table_name(cls.attr["db_table"])
        else:
            BaseError.unmet_dependency(
                message="attr db_table is not set for the model!",
                details={"class": {"name": "ModelBaseMeta"}},
                extra={'cls': cls}
            )


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    status = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def day_suffix(self, day):
        suffix = ""
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]
        return suffix

    def date_formatter(self, date, format):
        try:
            if format == "-dsMMMYYYY":
                return date.strftime("%-d" + self.day_suffix(date.day) + " %B %Y")
            elif format == "dsMMMYYYY":
                return date.strftime("%d" + self.day_suffix(date.day) + " %B %Y")
            elif format == "dMMMYYYY":
                return date.strftime("%d" + " %B %Y")
            elif format == "dmmmYYYY":
                return date.strftime("%d" + " %b %Y")
            elif format == "HHIIA":
                return date.strftime("%I:%M %p")
            elif format == "ymd":
                return date.strftime("%Y-%m-%d")
        except Exception as error:
            print(error)
            return ""
        return ""

    def delete(self, using=None, keep_parents=False):
        # self._do_backup(type=10)
        return models.Model.delete(self, using=None, keep_parents=False)


@receiver(pre_save, sender=BaseModel)
def pre_save_updated_date_receiver(sender, instance, *args, **kwargs):
    if instance:
        instance.updated_at = timezone.now()
