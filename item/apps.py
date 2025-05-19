from django.apps import AppConfig


class ItemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'item'

    def ready(self):
        import item.signals



from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        import users.signals  # signals.py dosyasını burada import ediyoruz
