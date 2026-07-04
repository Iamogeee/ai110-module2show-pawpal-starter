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
        return PRIORITY_ORDER.get(self.priority, 0) > PRIORITY_ORDER.get(
            other.priority, 0
        )

    def mark_done(self) -> None:
        """Mark this task as completed."""
        self.done = True


@dataclass
class Pet:
    """An animal being cared for, owning a list of care tasks."""

    name: str
    species: str
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        self.tasks.remove(task)

    def get_tasks(self) -> list[Task]:
        """Return this pet's care tasks."""
        return self.tasks


@dataclass
class Owner:
    """The person using the app; owns pets and sets daily constraints."""

    name: str
    available_minutes: int = 0
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_pets(self) -> list[Pet]:
        """Return the owner's pets."""
        return self.pets

    def set_available_time(self, minutes: int) -> None:
        """Set how many minutes the owner has available today."""
        self.available_minutes = minutes

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of the owner's pets, flattened."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks())
        return tasks


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
        """Create a scheduler for the given tasks, time budget, and preferences."""
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
        """Explain why tasks were included or skipped (also stored on DailyPlan.reasoning)."""
        raise NotImplementedError
