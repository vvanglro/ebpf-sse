from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from redis.exceptions import ResponseError
from sse_starlette.sse import EventSourceResponse
from starlette import status

from ebpf_sse.stream import RedisServerObj

app = FastAPI(title=__name__)


@app.get("/sse")
async def sse() -> EventSourceResponse:
    return EventSourceResponse(RedisServerObj)


@app.post("/message", status_code=status.HTTP_201_CREATED)
async def send_message(message: str, event: str) -> dict:
    await RedisServerObj.pool.xadd(name="ebpf_sse", fields={"data": message, "event": event},
                                   maxlen=100)
    return {'success': True}


app.mount("/", StaticFiles(directory="./"))


@app.on_event("startup")
async def startup() -> None:
    await RedisServerObj.connect()
    try:
        await RedisServerObj.pool.xgroup_create(name="ebpf_sse", groupname="bash_readline", id="$", mkstream=True)
    except ResponseError as e:
        # https://github.com/redis/redis/issues/9893
        if e == "BUSYGROUP Consumer Group name already exists":
            pass


@app.on_event("shutdown")
async def stop_event() -> None:
    await RedisServerObj.close()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
