import os

from nautobot.core.settings import *
from nautobot.core.settings_funcs import is_truthy

ALLOWED_HOSTS = os.getenv("NAUTOBOT_ALLOWED_HOSTS", "*").split(",")

DATABASES = {
    "default": {
        "NAME": os.getenv("NAUTOBOT_DB_NAME", "nautobot"),
        "USER": os.getenv("NAUTOBOT_DB_USER", "nautobot"),
        "PASSWORD": os.getenv("NAUTOBOT_DB_PASSWORD", "nautobot"),
        "HOST": os.getenv("NAUTOBOT_DB_HOST", "postgres"),
        "PORT": os.getenv("NAUTOBOT_DB_PORT", "5432"),
        "CONN_MAX_AGE": int(os.getenv("NAUTOBOT_DB_CONN_MAX_AGE", 300)),
        "ENGINE": "django.db.backends.postgresql",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{os.getenv('NAUTOBOT_REDIS_HOST', 'redis')}:{os.getenv('NAUTOBOT_REDIS_PORT', '6379')}/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

CELERY_BROKER_URL = f"redis://{os.getenv('NAUTOBOT_REDIS_HOST', 'redis')}:{os.getenv('NAUTOBOT_REDIS_PORT', '6379')}/0"
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

SECRET_KEY = os.getenv("NAUTOBOT_SECRET_KEY", "change-me-in-production")

PLUGINS = [
    "nautobot_plugin_nornir",
    "nautobot_device_onboarding",
    "nautobot_golden_config",
    "nautobot_ssot",
]

PLUGINS_CONFIG = {
    "nautobot_plugin_nornir": {
        "nornir_settings": {
            "credentials": "nautobot_plugin_nornir.plugins.credentials.env_vars.CredentialsEnvVars",
            "runner": {
                "plugin": "threaded",
                "options": {
                    "num_workers": 20,
                },
            },
        },
    },
    "nautobot_device_onboarding": {
        "default_ip_status": "Active",
        "default_device_role": "network",
        "default_device_status": "Active",
        "create_platform_if_missing": True,
        "create_device_type_if_missing": True,
        "create_manufacturer_if_missing": True,
        "skip_device_type_on_update": False,
        "skip_manufacturer_on_update": False,
        "platform_map": {
            "arista_eos": "arista_eos",
        },
        "onboarding_extensions_map": {
            "arista_eos": {
                "onboarding_class": "nautobot_device_onboarding.onboarding_extensions.netmiko_onboarding.NetmikoOnboarding",
                "driver_addon_result_key": "netmiko_device_type",
            }
        },
    },
    "nautobot_golden_config": {
        "enable_backup": True,
        "enable_compliance": True,
        "enable_intended": True,
        "enable_sotagg": True,
        "sot_agg_transposer": None,
        "platform_slug_map": None,
    },
    "nautobot_ssot": {},
}

NAPALM_USERNAME = os.getenv("NAPALM_USERNAME", "admin")
NAPALM_PASSWORD = os.getenv("NAPALM_PASSWORD", "Pack3tC0ders")
NAPALM_ARGS = {
    "transport": "http",
    "port": 80,
}