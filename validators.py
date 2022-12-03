from urllib.parse import urlparse

from models import Url


def validate_url(url):
    result = urlparse(url)
    return all([result.scheme, result.netloc, result.path])


def check_base_url(user, base_url):
    if Url.query.filter_by(base_url=base_url, user_id=user.id).count() > 0:
        return True
    return False

