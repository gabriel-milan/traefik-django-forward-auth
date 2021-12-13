from .base import *

import json
from os import getenv

config: dict = json.loads(getenv("CONFIG"))


class ConfigError(Exception):
    pass


def get_key(key: str) -> str:
    key = key.lower()
    if key in config:
        return config[key]
    raise ConfigError(f"Configuration \"{key}\" not found")


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_key("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_key("DEBUG")

# Allowed hosts
ALLOWED_HOSTS = get_key("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = get_key("CSRF_TRUSTED_ORIGINS")

# CORS
CORS_ALLOW_ALL_ORIGINS = get_key("CORS_ALLOW_ALL_ORIGINS")
CORS_ALLOWED_ORIGINS = get_key("CORS_ALLOWED_ORIGINS")

SESSION_COOKIE_DOMAIN = get_key("SESSION_COOKIE_DOMAIN")
TIME_ZONE = get_key("TIME_ZONE")

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = get_key("DATABASES")