import asyncio

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse, ServerSentEvent
from starlette import status


class Stream:
    def __init__(self) -> None:
        self._queue = asyncio.Queue()

    def __aiter__(self) -> "Stream":
        return self

    async def __anext__(self) -> ServerSentEvent:
        try:
            item = self._queue.get_nowait()
        except asyncio.QueueEmpty:
            await asyncio.sleep(3)
            return ServerSentEvent(data="Empty")
        else:
            return item

    async def send(self, value: ServerSentEvent) -> None:
        await self._queue.put(value)


app = FastAPI(title=__name__)
_stream = Stream()
app.dependency_overrides[Stream] = lambda: _stream


@app.get("/sse")
async def sse(stream: Stream = Depends()) -> EventSourceResponse:
    return EventSourceResponse(stream)


@app.post("/message", status_code=status.HTTP_201_CREATED)
async def send_message(message: str, event: str, stream: Stream = Depends()) -> dict:
    await stream.send(
        ServerSentEvent(data=message, event=event)
    )
    return {'success': True}


app.mount("/", StaticFiles(directory="./"))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
