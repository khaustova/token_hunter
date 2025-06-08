from logging import getLogger
from copy import deepcopy
from django.conf import settings

logger = getLogger(__name__)


DASHBOARD_CUSTOMIZATION = {
    "dashboard_name": "Admin Panel",
    "dashboard_title": "Administration Dashboard",
    "search_model": "",
    "sidebar_icons": {
        "auth.user": "person",
        "auth.group": "groups",
    },
    "hidden_apps": [],
    "hidden_models": [],
    "apps_order": [],
    "extra_links": [],
}


def get_settings() -> dict:
    """
    Returns a dictionary of customization settings, updated with
    project-specific settings from the Django settings file.

    The function:
    1. Starts with default DASHBOARD_CUSTOMIZATION values.
    2. Overrides them with any values specified in settings.DASHBOARD_CUSTOMIZATION.
    3. Filters out None values from project settings.
    4. Returns the merged configuration.

    Returns:
        Merged dictionary containing all dashboard customization settings
    """
    customization_settings = deepcopy(DASHBOARD_CUSTOMIZATION)
    project_settings = {key: value for key, value in getattr(
        settings, "DASHBOARD_CUSTOMIZATION", {}).items() if value is not None}
    customization_settings.update(project_settings)

    return customization_settings
