from django.http import HttpResponse
from django_redis import get_redis_connection
from django.core.serializers.json import DjangoJSONEncoder
from . import const as const
import json
from django.views import View
from datetime import datetime, timedelta
import logging
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.core.cache import cache

redis_cache = get_redis_connection("redis")
redis_cache.connection_pool.connection_kwargs["decode_responses"] = True
redis_cache.connection_pool.reset()
logger = logging.getLogger("APPNAME")


class ResponseBaseClass(View):

    def generate_response(self, response, request_body, source):
        payload = dict()
        payload['status'] = True if response else False
        payload['summary'] =    "Country Name = {} |" \
                                "Total Cases = {} |" \
                                "Active Cases= {} |" \
                                "Total Deaths = {} |" \
                                "Recovery Rate ={:.2f} |" \
                                "Percentage of Population Infected = {:.2f}".format(
            request_body.get('country_name','Not Available'),
            response.get("Total Case",None),
            response.get("Total Active", None),
            response.get("Total Deaths", None),
            int(response.get("Total Recovered").replace(",",""))
            /int(response.get("Total Case",'1').replace(",","")),
            int(response.get("Total Case").replace(",", ""))
            / int(response.get("Population", '1').replace(",", ""))
        )

        payload['data'] = response
        payload['source'] = source
        return payload




def datetime_parser(dct):
    for k, v in dct.items():
        try:
            dct[k] = datetime.strptime(v, const.DATE_TIME_FORMAT)
        except Exception:  # noqa
            pass
    return dct


def load_redis_data(country_name):
    redis_data = redis_cache.get(country_name)
    if not redis_data:
        return {}
    return json.loads(redis_data, object_hook=datetime_parser)


def save_redis_data(country_name, redis_data):
    redis_cache.set(country_name, json.dumps(redis_data, cls=DjangoJSONEncoder))
    redis_cache.expire(country_name, const.CACHE_EXPIRE_TTL)


def check_session_active(redis_data):
    if "verified_session_time" in redis_data:

        if self.redis_data["verified_session_time"]:
            if isinstance(self.redis_data['verified_session_time'], datetime):
                valid_till = redis_data['verified_session_time']
            else:
                valid_till = datetime.strptime(
                    redis_data['verified_session_time'], const.DATE_TIME_FORMAT
                )

            if datetime.now() <= valid_till:
                redis_data['verified_session_time'] = (
                        datetime.now() + timedelta(minutes=8)).strftime(
                    const.DATE_TIME_FORMAT)
                return True, redis_data
            else:
                return False, redis_data
        else:
            return False, redis_data
    else:
        return False, redis_data


def handle_exception_decorator(func, *_args, **_kwargs):
    """Handles exception that might occur in calling function
    Args:
        func (function): Calling function
        _args (list): List of function arguments.
        _kwargs (dict): Dictionary of function arguments.
    Returns:
        API response if no exception occur else agent connect msg
    """

    def handle_exception(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.info(e)
            return e

    return handle_exception
