import logging
from typing import Optional
import httpx
from termo_service.config import LametricConfig, app_config
from termo_service.ble.models import NowData

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
        try:
            async with httpx.AsyncClient(
                headers=config.headers, base_url=config.base_url
            ) as client:
                r = await client.post(endpoint, **kwds)
                await r.aclose()
        except Exception as e:
            logging.error(e)
