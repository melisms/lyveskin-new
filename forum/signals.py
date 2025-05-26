from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django_redis import get_redis_connection
from .models import Post
from django.core.paginator import Paginator

def clear_post_list_cache():
    redis_conn = get_redis_connection("default")
    cursor = 0
    keys_to_delete = []
    while True:
        cursor, keys = redis_conn.scan(cursor=cursor, match="post_list_page_*", count=100)
        keys_to_delete.extend([key.decode('utf-8') if isinstance(key, bytes) else key for key in keys])
        if cursor == 0:
            break
    keys_to_delete.append('post_list_all_ids')
    keys_to_delete = list(set(keys_to_delete))
    if keys_to_delete:
        redis_conn.delete(*keys_to_delete)

def rebuild_post_list_cache():
    all_post_ids = list(Post.objects.order_by('-date_posted').values_list('id', flat=True))
    cache.set('post_list_all_ids', all_post_ids, 60*5)
    paginator = Paginator(all_post_ids, 5)
    if paginator.num_pages > 0:
        first_page_ids = all_post_ids[:5]
        cache.set('post_list_page_1', first_page_ids, 60*5)

@receiver(post_save, sender=Post)
def post_saved(sender, instance, **kwargs):
    clear_post_list_cache()
    rebuild_post_list_cache()

@receiver(post_delete, sender=Post)
def post_deleted(sender, instance, **kwargs):
    clear_post_list_cache()
    rebuild_post_list_cache()
