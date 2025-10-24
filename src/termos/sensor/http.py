import asyncio
import logging
from asyncio import Queue
from termos.sensor.sensor import Sensor
from termos.sensor.models import NowData
import httpx
from httpx_retries import RetryTransport, Retry

from pydantic import BaseModel, AwareDatetime

class NowResponse(BaseModel):
    temp: float
    timestamp: AwareDatetime


class HTTP(Sensor):

    ble_queue: Queue = Queue()
    datapoints_count = 0
    
    @property
    def is_connected(self) -> bool:
        return True
    
    def disconnect(self):
        pass

    async def init_notify(self):
        if self.is_connected:
            self.disconnect()
        retry = Retry(total=3, backoff_factor=0.5)

        async with httpx.AsyncClient(
                base_url=f"http://{self.address}:{self.mac}",
                transport=RetryTransport(retry=retry),
            ) as client:
            while client:
                try:
                    r = await client.get(self.uuid_read)
                    data = NowResponse(**r.json())
                    await r.aclose()
                    nowdata = NowData(
                        temp=data.temp,
                        humid=0,
                        location=self.location,
                    )
                    logging.info(f"New data: {nowdata.temp}°C, {nowdata.humid}%, {self.__class__}")
                    self.__class__.queue.put_nowait((nowdata, self.__class__))
                    await asyncio.sleep(70)
                except Exception as e:
                    logging.exception(e)
