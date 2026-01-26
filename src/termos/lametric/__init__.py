import logging
from typing import Optional
import httpx
from httpx_retries import RetryTransport, Retry
from termos.config import LametricConfig, app_config
from termos.sensor.models import NowData

config: LametricConfig = app_config.lametric


class LametricMeta(type):

    __instance: Optional["Lametric"] = None

    def __call__(cls, *args, **kwds):
        if not cls.__instance:
            cls.__instance = type.__call__(cls, *args, **kwds)
        return cls.__instance

    async def update(cls, data: NowData):
        await cls().post_data(
            config.endpoints.nowdata, json=data.model_dump(mode="json")
        )


class Lametric(object, metaclass=LametricMeta):

    async def post_data(self, endpoint, **kwds):
        retry = Retry(total=50000, backoff_factor=0.5)
        try:
            async with httpx.AsyncClient(
                headers=config.headers,
                base_url=config.base_url,
                transport=RetryTransport(retry=retry),
            ) as client:
                r = await client.post(endpoint, **kwds)
                await r.aclose()
        except Exception as e:
            logging.error(f"failed to connect to LaMetric {endpoint}")
            logging.error(e)
