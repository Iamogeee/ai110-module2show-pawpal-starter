"""PawPal+ logic layer.

Backend classes for PawPal+, translated from diagrams/uml.mmd.
This is a skeleton: attributes and method stubs only — no logic yet.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

# Priority ranking used to compare and sort tasks (higher value = more urgent).
PRIORITY_ORDER = {"low": 1, "medium": 2, "high": 3}


@dataclass
class Task:
    """A single unit of pet care (walk, feeding, meds, grooming, enrichment)."""

    name: str
    duration_minutes: int
    priority: str
    category: str
    done: bool = False

    def is_higher_priority_than(self, other: "Task") -> bool:
        """Return True if this task outranks `other` for scheduling order."""
        raise NotImplementedError

    def mark_done(self) -> None:
        """Mark this task as completed."""
        raise NotImplementedError


@dataclass
class Pet:
    """An animal being cared for, owning a list of care tasks."""

    name: str
    species: str
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        raise NotImplementedError

    def get_tasks(self) -> list[Task]:
        """Return this pet's care tasks."""
        raise NotImplementedError


@dataclass
class Owner:
    """The person using the app; owns pets and sets daily constraints."""

    name: str
    available_minutes: int = 0
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        raise NotImplementedError

    def get_pets(self) -> list[Pet]:
        """Return the owner's pets."""
        raise NotImplementedError

    def set_available_time(self, minutes: int) -> None:
        """Set how many minutes the owner has available today."""
        raise NotImplementedError


@dataclass
class DailyPlan:
    """The generated schedule the user sees, plus what didn't fit."""

    date: date
    scheduled_tasks: list[Task] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    reasoning: str = ""

    def total_time(self) -> int:
        """Return the total minutes of all scheduled tasks."""
        raise NotImplementedError

    def summary(self) -> str:
        """Return a human-readable summary of the plan."""
        raise NotImplementedError


class Scheduler:
    """Turns candidate tasks + constraints into a DailyPlan."""

    def __init__(
        self,
        tasks: list[Task] | None = None,
        available_minutes: int = 0,
        preferences: dict | None = None,
    ) -> None:
        self.tasks = tasks or []
        self.available_minutes = available_minutes
        self.preferences = preferences or {}

    def sort_tasks(self) -> list[Task]:
        """Order tasks by priority, then duration."""
        raise NotImplementedError

    def filter_by_time(self) -> list[Task]:
        """Drop tasks that don't fit the available time budget."""
        raise NotImplementedError

    def generate_plan(self) -> DailyPlan:
        """Build and return a DailyPlan from the candidate tasks."""
        raise NotImplementedError

    def explain(self) -> str:
        """Explain why tasks were included or skipped.

        The returned text is also stored on the produced DailyPlan
        (DailyPlan.reasoning) so the plan and its explanation stay in sync.
        """
        raise NotImplementedError
