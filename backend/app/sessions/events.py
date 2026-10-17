from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime, timezone

_SENTINEL = object()
_LOG_MAX = 500
_QUEUE_MAX = 1000


@dataclass(frozen=True)
class Event:
    seq: int
    type: str
    payload: dict


class EventBus:
    def __init__(self) -> None:
        self._seq: dict[str, int] = defaultdict(int)
        self._log: dict[str, deque[Event]] = defaultdict(lambda: deque(maxlen=_LOG_MAX))
        self._subs: dict[str, list[asyncio.Queue]] = defaultdict(list)
        self._closed: set[str] = set()

    def last_seq(self, session_id: str) -> int:
        return self._seq.get(session_id, 0)

    def publish(self, session_id: str, event_type: str, payload: dict) -> Event:
        if session_id in self._closed:
            seq = self._seq[session_id]
            return Event(seq=seq, type=event_type, payload=dict(payload))
        self._seq[session_id] += 1
        seq = self._seq[session_id]
        envelope = {
            "type": event_type,
            "seq": seq,
            "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "session_id": session_id,
            **payload,
        }
        event = Event(seq=seq, type=event_type, payload=envelope)
        self._log[session_id].append(event)
        for queue in list(self._subs.get(session_id, [])):
            self._put(queue, event)
        return event

    def _put(self, queue: asyncio.Queue, item: object) -> None:
        try:
            queue.put_nowait(item)
        except asyncio.QueueFull:
            try:
                queue.get_nowait()
            except asyncio.QueueEmpty:
                pass
            try:
                queue.put_nowait(item)
            except asyncio.QueueFull:
                pass

    async def subscribe(self, session_id: str, since_seq: int = 0) -> AsyncIterator[Event]:
        for event in list(self._log.get(session_id, ())):
            if event.seq > since_seq:
                yield event
        if session_id in self._closed:
            return
        queue: asyncio.Queue = asyncio.Queue(maxsize=_QUEUE_MAX)
        self._subs[session_id].append(queue)
        try:
            while True:
                item = await queue.get()
                if item is _SENTINEL:
                    return
                event = item
                if event.seq > since_seq:
                    yield event
        finally:
            subs = self._subs.get(session_id, [])
            if queue in subs:
                subs.remove(queue)

    def close(self, session_id: str) -> None:
        self._closed.add(session_id)
        for queue in list(self._subs.get(session_id, [])):
            self._put(queue, _SENTINEL)

    def reset(self) -> None:
        self._seq.clear()
        self._log.clear()
        self._subs.clear()
        self._closed.clear()


bus = EventBus()
