from django.apps import AppConfig


class SearchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.search'

    def ready(self):
        """
        Import signal handlers when the app is ready.
        This ensures our category updates happen when cases are saved.
        """
        from apps.search.models import update_categories_on_case_save  # noqa
