import asyncio
from collections import defaultdict

_handlers = defaultdict(list)
_queue = asyncio.Queue()

def on(event_name):
    def decorator(fn):
        _handlers[event_name].append(fn)
        return fn
    return decorator

async def publish(event_name, data):
    await _queue.put({"event": event_name, "data": data})
    print(f"[EventBus] 📢 publish: {event_name} → {data}")

async def run():
    print("[EventBus] 🟢 เริ่มทำงาน")
    while True:
        msg = await _queue.get()
        handlers = _handlers.get(msg["event"], [])
        for handler in handlers:
            await handler(msg["data"])