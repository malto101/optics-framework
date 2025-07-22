import asyncio
import logging
import time
from enum import Enum
from typing import Union, Optional, Dict, List, Any
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from concurrent.futures import ThreadPoolExecutor

internal_logger = logging.getLogger("optics.internal")


class EventStatus(str, Enum):
    """Possible statuses for events."""
    NOT_RUN = "NOT_RUN"
    RUNNING = "RUNNING"
    PASS = "PASS" #nosec
    FAIL = "FAIL"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"
    RETRYING = "RETRYING"


class CommandType(str, Enum):
    """Possible command types."""
    RETRY = "Retry"
    ADD = "Add"
    SKIP = "Skip"
    PAUSE = "Pause"
    RESUME = "Resume"


class Event(BaseModel):
    """Structure for an event."""
    entity_type: str = Field(...,
                             description="Type of entity (e.g., test_case, module, keyword)")
    entity_id: str = Field(..., description="Unique ID of the entity")
    name: str = Field(..., description="Human-readable name of the entity")
    status: EventStatus = Field(..., description="Status of the entity")
    message: str = Field(
        default="", description="Additional details about the event")
    parent_id: Optional[str] = Field(
        default=None, description="ID of the parent entity (e.g., module for keyword, test_case for module)")
    extra: Dict[str, str] = Field(
        default_factory=dict, description="Additional metadata (e.g., session_id for test_case)")
    timestamp: float = Field(default_factory=time.time, description="Event creation time in seconds")
    # NEW FIELDS
    args: Optional[Union[List[Any], Dict[str, Any]]] = Field(default=None, description="Arguments passed to the keyword (if applicable)")
    start_time: Optional[float] = Field(default=None, description="Start time of keyword/module execution (seconds since epoch)")
    end_time: Optional[float] = Field(default=None, description="End time of keyword/module execution (seconds since epoch)")
    elapsed: Optional[float] = Field(default=None, description="Elapsed time for execution (seconds)")
    logs: Optional[List[str]] = None

class Command(BaseModel):
    """Structure for a command."""
    command: CommandType = Field(..., description="Type of command")
    entity_id: str = Field(..., description="ID of the entity to act on")
    params: List[str] = Field(
        default_factory=list, description="Optional parameters for the command")
    parent_id: Optional[str] = Field(
        default=None, description="ID of the parent entity, if applicable")


class EventSubscriber(ABC):
    """Abstract base class for event subscribers."""
    @abstractmethod
    async def on_event(self, event: Event) -> None:
        pass


class EventManager:
    """Centralized manager for events and commands."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.event_queue: asyncio.Queue[Event] = asyncio.Queue()
            self.command_queue: asyncio.Queue[Command] = asyncio.Queue()
            self.subscribers: Dict[str, EventSubscriber] = {}
            self._running = False
            self._process_task = None
            self._initialized = True
            internal_logger.debug(f"EventManager initialized: {id(self)}")

    async def start(self):
        """Start the event processing loop."""
        if not self._running:
            self._running = True
            loop = asyncio.get_running_loop()
            internal_logger.debug(f"Event loop running: {loop.is_running()}")
            self._process_task = loop.create_task(self._process_events())
            internal_logger.debug(
                f"EventManager started, process_task: {self._process_task}")

    async def stop(self):
        """Stop the event processing loop."""
        self._running = False
        if self._process_task:
            self._process_task.cancel()
            try:
                await self._process_task  # Await the task to ensure it's cancelled
            except asyncio.CancelledError:
                pass
            self._process_task = None
        internal_logger.debug("EventManager stopped")

    async def _process_events(self):
        """Background task to process events and notify subscribers."""
        internal_logger.debug("Starting event processing loop")
        while self._running:
            try:
                event = await self.event_queue.get()
                internal_logger.debug(
                    f"Processing event: {event.model_dump()}")
                for subscriber_id, subscriber in self.subscribers.items():
                    internal_logger.debug(
                        f"Dispatching to subscriber {subscriber_id}: {subscriber}")
                    try:
                        await subscriber.on_event(event)
                    except Exception as e:
                        internal_logger.error(
                            f"Error in subscriber {subscriber_id}: {e}")
                self.event_queue.task_done()
            except asyncio.CancelledError:
                internal_logger.debug("Event processing loop cancelled")
                raise
            except Exception as e:
                internal_logger.error(f"Error processing event: {e}")
        internal_logger.debug("Event processing loop stopped")

    async def publish_event(self, event: Event):
        """Publish an event to the queue."""
        internal_logger.debug(f"Publishing event: {event.model_dump()}")
        await self.event_queue.put(event)

    async def publish_command(self, command: CommandType, entity_id: str, params: Optional[List[str]] = None, parent_id: Optional[str] = None):
        """Publish a command to the queue."""
        if params is None:
            params = []
        cmd = Command(command=command, entity_id=entity_id,
                      params=params, parent_id=parent_id)
        internal_logger.debug(f"Publishing command: {cmd.model_dump()}")
        await self.command_queue.put(cmd)

    def subscribe(self, subscriber_id: str, subscriber: EventSubscriber):
        """Register a subscriber to receive events."""
        self.subscribers[subscriber_id] = subscriber
        internal_logger.debug(f"Subscribed {subscriber_id}: {subscriber}")

    def unsubscribe(self, subscriber_id: str):
        """Remove a subscriber."""
        self.subscribers.pop(subscriber_id, None)
        internal_logger.debug(f"Unsubscribed {subscriber_id}")

    async def get_command(self) -> Optional[Command]:
        """Retrieve the next command from the queue, if available."""
        if not self.command_queue.empty():
            return await self.command_queue.get()
        return None

    def dump_state(self):
        """Log the current state of the EventManager."""
        internal_logger.debug(
            f"EventManager state: running={self._running}, subscribers={self.subscribers}, event_queue_size={self.event_queue.qsize()}")

    def shutdown(self):
        """Shutdown EventManager and cleanup subscribers."""
        internal_logger.debug("Shutting down EventManager...")

        for subscriber_id, subscriber in self.subscribers.items():
            if hasattr(subscriber, 'close'):
                internal_logger.debug(f"Closing subscriber {subscriber_id}")
                try:
                    subscriber.close()
                except Exception as e:
                    internal_logger.error(f"Error while closing subscriber {subscriber_id}: {e}")

        self.dump_state()
        self.stop()


# New classes and functions for synchronous wrapper
class SyncEventManager(EventManager):
    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._thread = self._executor.submit(self._start_loop)
        self._event_manager_instance = EventManager()

    def _start_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def _run_async_in_thread(self, coro):
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()

    def start(self):
        self._run_async_in_thread(self._event_manager_instance.start())

    def stop(self):
        self._run_async_in_thread(self._event_manager_instance.stop())

    def publish_event(self, event: Event):
        self._run_async_in_thread(self._event_manager_instance.publish_event(event))

    def publish_command(self, command: CommandType, entity_id: str, params: Optional[List[str]] = None, parent_id: Optional[str] = None):
        self._run_async_in_thread(self._event_manager_instance.publish_command(command, entity_id, params, parent_id))

    def subscribe(self, subscriber_id: str, subscriber: EventSubscriber):
        # Subscribers are async, so they need to be handled in the async thread
        self._run_async_in_thread(self._event_manager_instance.subscribe(subscriber_id, subscriber))

    def unsubscribe(self, subscriber_id: str):
        self._run_async_in_thread(self._event_manager_instance.unsubscribe(subscriber_id))

    def get_command(self) -> Optional[Command]:
        return self._run_async_in_thread(self._event_manager_instance.get_command())

    def dump_state(self):
        self._run_async_in_thread(self._event_manager_instance.dump_state())

    def shutdown(self):
        self._run_async_in_thread(self._event_manager_instance.shutdown())
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._executor.shutdown(wait=True)


def get_event_manager() -> SyncEventManager:
    return SyncEventManager()
