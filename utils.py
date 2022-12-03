import secrets

from models import Url


def get_short_urls(user, host):
    if not user.url:
        return []
    return [{"url": host + "/" + obj_url.key, "key": obj_url.key, "cliks": obj_url.clicks} for obj_url in user.url]


def get_obj_url(key):
    obj_url = Url.query.filter_by(key=key).first()
    return obj_url


def generate_key():
    key = secrets.token_urlsafe(5)
    while get_obj_url(key):
        key = secrets.token_urlsafe(5)
    return key
