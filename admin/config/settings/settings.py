from os import environ

from split_settings.tools import include, optional

ENV = environ.get("DJANGO_ENV") or "production"

base_settings = [
    "components/common.py",  # standard django settings
    "components/database.py",  # postgres
    # 'components/rq.py',  # redis and redis-queue
    # 'components/emails.py',  # smtp
    # You can even use glob:
    # 'components/*.py'
    # Select the right env:
    f"environments/{ENV}.py",
    # Optionally override some settings:
    optional("environments/local.py"),
]

# Include settings:
include(*base_settings)
