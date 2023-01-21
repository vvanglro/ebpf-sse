from typing import Optional

from redis.asyncio.client import Redis
from redis.asyncio.connection import ConnectionPool
import redis.asyncio as redis
from sse_starlette import ServerSentEvent


class RedisServer:

    def __init__(self, url):
        self.url = url
        self._pool: Optional[Redis] = None

    def __aiter__(self) -> "RedisServer":
        return self

    async def __anext__(self) -> ServerSentEvent:
        x_read_resp = await self._pool.xreadgroup(groupname="bash_readline", consumername="consumer",
                                                  streams={"ebpf_sse": ">"}, count=1,
                                                  block=3 * 1000, noack=True)
        if x_read_resp:
            _, x_read_resp_data = x_read_resp[0][1][0]
            return ServerSentEvent(data=x_read_resp_data.get("data"), event=x_read_resp_data.get("event"))
        return ServerSentEvent(data="Empty")

    async def connect(self):
        pool = ConnectionPool.from_url(url=self.url, decode_responses=True)
        self._pool = redis.Redis(connection_pool=pool)

    async def close(self) -> None:
        """
        Closes connection and resets pool
        """
        if self._pool is not None:
            await self._pool.close()
        self._pool = None

    @property
    def pool(self):
        return self._pool


RedisServerObj = RedisServer(url="redis://redis:6379")
