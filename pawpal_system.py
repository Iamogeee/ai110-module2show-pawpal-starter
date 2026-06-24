"""PawPal+ logic layer.

Backend classes for PawPal+, translated from diagrams/uml.mmd.
This is a skeleton: attributes and method stubs only — no logic yet.
"""

from __future__ import annotations

from datetime import date


class Task:
    """A single unit of pet care (walk, feeding, meds, grooming, enrichment)."""

    def __init__(
        self,
        name: str,
        duration_minutes: int,
        priority: str,
        category: str,
        done: bool = False,
    ) -> None:
        self.name = name
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category
        self.done = done

    def is_higher_priority_than(self, other: "Task") -> bool:
        """Return True if this task outranks `other` for scheduling order."""
        raise NotImplementedError

    def mark_done(self) -> None:
        """Mark this task as completed."""
        raise NotImplementedError


class Pet:
    """An animal being cared for, owning a list of care tasks."""

    def __init__(self, name: str, species: str, breed: str = "") -> None:
        self.name = name
        self.species = species
        self.breed = breed
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        raise NotImplementedError

    def get_tasks(self) -> list[Task]:
        """Return this pet's care tasks."""
        raise NotImplementedError


class Owner:
    """The person using the app; owns pets and sets daily constraints."""

    def __init__(
        self,
        name: str,
        available_minutes: int = 0,
        preferences: dict | None = None,
    ) -> None:
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences or {}
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        raise NotImplementedError

    def get_pets(self) -> list[Pet]:
        """Return the owner's pets."""
        raise NotImplementedError

    def set_available_time(self, minutes: int) -> None:
        """Set how many minutes the owner has available today."""
        raise NotImplementedError


class DailyPlan:
    """The generated schedule the user sees, plus what didn't fit."""

    def __init__(
        self,
        plan_date: date,
        scheduled_tasks: list[Task] | None = None,
        skipped_tasks: list[Task] | None = None,
    ) -> None:
        self.date = plan_date
        self.scheduled_tasks = scheduled_tasks or []
        self.skipped_tasks = skipped_tasks or []

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
        """Explain why tasks were included or skipped."""
        raise NotImplementedError
