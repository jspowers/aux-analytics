from flask import current_app


class AppRegistryService:
    """Service for managing the sub-application registry"""

    def get_enabled_apps(self):
        """
        Get all enabled sub-applications from the configuration

        Returns:
            list: List of enabled sub-application dictionaries
        """
        all_apps = current_app.config.get('SUB_APPS', [])
        return [app for app in all_apps if app.get('enabled', True)]

    def get_app_by_id(self, app_id):
        """
        Retrieve a specific sub-application by its ID

        Args:
            app_id (str): The unique identifier for the sub-application

        Returns:
            dict: The sub-application dictionary, or None if not found
        """
        all_apps = current_app.config.get('SUB_APPS', [])
        for app in all_apps:
            if app.get('id') == app_id:
                return app
        return None

    def format_app_for_display(self, app):
        """
        Format sub-application data for template rendering

        Args:
            app (dict): The sub-application dictionary

        Returns:
            dict: Formatted sub-application data
        """
        return {
            'id': app.get('id'),
            'name': app.get('name', 'Unnamed App'),
            'description': app.get('description', 'No description available'),
            'url_prefix': app.get('url_prefix', '#'),
            'icon': app.get('icon', '📦'),
            'enabled': app.get('enabled', True)
        }
