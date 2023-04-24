from os import environ

from config.settings.components.common import INSTALLED_APPS, MIDDLEWARE

SECRET_KEY = "django-insecure-^w1v$ra&_@^ylx#^=%l&dt%lq$y4o)t0rg-5v!x0lb711qa=$7"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

INSTALLED_APPS += ["debug_toolbar"]

MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]
if environ.get("USE_DOCKER") == "yes":
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [".".join(ip.split(".")[:-1] + ["1"]) for ip in ips]
