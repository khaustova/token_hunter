from logging import getLogger
from copy import deepcopy
from django.conf import settings

logger = getLogger(__name__)


DASHBOARD_CUSTOMIZATION = {
    'dashboard_name': 'Админпанель',
    'dashboard_title': 'Панель администратора',
    'search_model': '',
    'sidebar_icons': {
        'auth.user': 'person',
        'auth.group': 'groups',
    },
    'hidden_apps': [],
    'hidden_models': [],
    'apps_order': [],
    'extra_links': [],
}


def get_settings() -> dict:
    """
    Возвращает словарь с настройками кастомизации, обновленный в соответствии
    с настройками, указанными в файле настроек проекта.
    """
    customization_settings = deepcopy(DASHBOARD_CUSTOMIZATION)
    project_settings = {key: value for key, value in getattr(
        settings, 'DASHBOARD_CUSTOMIZATION', {}).items() if value is not None}
    customization_settings.update(project_settings)

    return customization_settings
