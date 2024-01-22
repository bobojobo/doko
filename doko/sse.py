"""
Server side events 

This looks a bit like overkill for the ready set task. Just poll the db.... But for the game itself I could see value 
in this. Memory should be big enough to store key-value of all users for a couple of change events like someone played 
a card or clicked the k90 button. Data itself stays in db. that's easier. No need to do a caching layer there. And then
it should be in redis anyways I guess. 

Longterm it might be good to define on the event itself where it needs to be broadcast, like group or partner. 
It might also be nice to link the dtos and the events together in some way.

todo: this should probably also integrate further with EventSourceResponse
"""
from __future__ import annotations
from typing import Coroutine
import asyncio
from collections import defaultdict
from enum import Enum


class Event(Enum):
    player_status_update = "player_status_update"
    group_created = "group_created"
    game_created = "game_created"
    game_closed = "game_closed"
    card_played = "card_played"
    turn_changed = "turn_changed"


# keep track of events. Eventually this would evolve into something like a redis 
EventStore: defaultdict[str, dict[Event, asyncio.Event]] = defaultdict(lambda: defaultdict(asyncio.Event))

# keep track of background tasks
background_tasks = set()


async def consume(event: asyncio.Event, event_type: Event) -> Event:
    await event.wait()
    event.clear()
    return event_type


class EventLoop:
    """Loop of selected events happening for a session_token."""

    def __init__(self, session_token: str, events: Event | list[Event]) -> None:
        self.session_token = session_token
        self.event_types = events if isinstance(events, list) else [events]

    def __aiter__(self) -> EventLoop:
        return self

    async def __anext__(self) -> Event:
        """Consume the first event of the given events for the session_token that happens."""
        # todo: raise StopAsyncIteration based on optional argument. E.G.: (..., stop: callable = all_4_player_ready)
        done, _ = await asyncio.wait(self._tasks(), return_when=asyncio.FIRST_COMPLETED)
        result = done.pop()
        return result.result()

    def _tasks(self) -> list[asyncio.Task]:
        tasks = []
        for event_type in self.event_types:
            event = EventStore[self.session_token][event_type]
            task = asyncio.create_task(consume(event, event_type))
            tasks.append(task)
        return tasks


def add_task(coroutine: Coroutine) -> None:
    """Add coroutine as a background task."""
    global background_tasks
    task = asyncio.create_task(coroutine)
    background_tasks.add(coroutine)
    task.add_done_callback(background_tasks.discard)


if __name__ == "__main__":
    db = {}

    def crud_player_ready(session_token: str) -> None:
        print(f"{session_token} clicked ready")
        db[session_token] = "ready"
        EventStore[session_token][Event.player_status_update].set()

    def crud_player_not_ready(session_token: str) -> None:
        print(f"{session_token} clicked not ready")
        db[session_token] = "not_ready"
        EventStore[session_token][Event.player_status_update].set()

    async def mock_players_click() -> None:
        """Mock players clicking on things"""

        await asyncio.sleep(3)
        crud_player_ready("p1")

        await asyncio.sleep(3)
        crud_player_not_ready("p1")

        await asyncio.sleep(3)
        crud_player_ready("p2")

    async def sse_loop(session_token: str) -> None:
        """Mock API SSE endpoint"""

        async for event in EventLoop(session_token, Event.player_status_update):
            print(f"{event.value}: new state for {session_token}: {db[session_token]}")

    async def main() -> None:
        sse_loop_task_p1 = asyncio.create_task(sse_loop("p1"))
        sse_loop_task_p2 = asyncio.create_task(sse_loop("p2"))
        mock_click_tasks = asyncio.create_task(mock_players_click())
        await sse_loop_task_p1
        await sse_loop_task_p2
        await mock_click_tasks

    asyncio.run(main())
