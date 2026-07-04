"""PawPal+ logic layer.

Backend classes for PawPal+, translated from diagrams/uml.mmd.
This is a skeleton: attributes and method stubs only — no logic yet.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from itertools import combinations

# Priority ranking used to compare and sort tasks (higher value = more urgent).
PRIORITY_ORDER = {"low": 1, "medium": 2, "high": 3}

# How often a task repeats, mapped to the gap until its next occurrence.
# "once" is absent on purpose: a one-off task has no next occurrence.
RECURRENCE_STEP = {
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
}


@dataclass
class Task:
    """A single unit of pet care (walk, feeding, meds, grooming, enrichment)."""

    name: str
    duration_minutes: int
    priority: str
    category: str
    done: bool = False
    # Start time as a 24-hour "HH:MM" string ("" = no set time yet).
    # Stored as a zero-padded string so it sorts chronologically as text.
    scheduled_time: str = ""
    # Which pet this task belongs to. Set automatically by Pet.add_task().
    pet_name: str = ""
    # How often the task repeats: "once" (default), "daily", or "weekly".
    frequency: str = "once"
    # The calendar day this instance is due (None = undated / "whenever").
    due_date: date | None = None

    def is_higher_priority_than(self, other: "Task") -> bool:
        """Return True if this task outranks `other` for scheduling order."""
        return PRIORITY_ORDER.get(self.priority, 0) > PRIORITY_ORDER.get(
            other.priority, 0
        )

    def mark_done(self) -> None:
        """Mark this task as completed."""
        self.done = True

    def next_occurrence(self) -> "Task | None":
        """Return a fresh, not-done copy of this task for its next due date.

        For a recurring task, the next date is this instance's ``due_date``
        advanced by one step (``timedelta(days=1)`` for daily, one week for
        weekly). If the task has no ``due_date`` yet, we anchor off today so
        a daily task becomes due today + 1 day.

        Returns None for a one-off ("once") task, which never recurs.
        """
        step = RECURRENCE_STEP.get(self.frequency)
        if step is None:
            return None
        base = self.due_date or date.today()
        # replace() copies every field (name, duration, times, pet_name, ...)
        # while overriding just the two that change for the new instance.
        return replace(self, due_date=base + step, done=False)


@dataclass
class Pet:
    """An animal being cared for, owning a list of care tasks."""

    name: str
    species: str
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet.

        Stamps the task with this pet's name so a flat task list (e.g. the
        Scheduler's) can still be filtered back down by pet.
        """
        task.pet_name = self.name
        self.tasks.append(task)

    def complete_task(self, task: Task) -> Task | None:
        """Mark ``task`` done and auto-queue its next occurrence.

        This is the recurrence hook: completing a "daily" or "weekly" task
        immediately adds a fresh instance for the next due date to this pet,
        so the owner never has to re-enter routine care. A "once" task just
        gets marked done. Returns the new instance (or None if not recurring).
        """
        task.mark_done()
        upcoming = task.next_occurrence()
        if upcoming is not None:
            self.add_task(upcoming)
        return upcoming

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

    def sort_by_time(self) -> list[Task]:
        """Return the tasks ordered by their scheduled start time.

        Because ``scheduled_time`` is a zero-padded 24-hour "HH:MM" string,
        plain text ordering is already chronological ("08:00" < "13:30").
        A lambda picks that field as the sort key; tasks with no set time
        ("") fall back to "99:99" so they sort to the end of the day.
        """
        return sorted(self.tasks, key=lambda task: task.scheduled_time or "99:99")

    def filter_by_status(self, done: bool = False) -> list[Task]:
        """Return only the tasks whose completion status matches ``done``.

        ``filter_by_status(done=False)`` gives the still-to-do tasks;
        ``filter_by_status(done=True)`` gives the finished ones.
        """
        return [task for task in self.tasks if task.done == done]

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Return only the tasks belonging to the pet named ``pet_name``."""
        return [task for task in self.tasks if task.pet_name == pet_name]

    @staticmethod
    def _window(task: Task) -> tuple[int, int] | None:
        """Return a task's (start, end) as minutes-since-midnight, or None.

        None means the task has no usable start time, so it can't clash with
        anything on the clock. Malformed times are treated the same way rather
        than raising — conflict detection should warn, never crash.
        """
        if not task.scheduled_time:
            return None
        try:
            hours, minutes = task.scheduled_time.split(":")
            start = int(hours) * 60 + int(minutes)
        except (ValueError, AttributeError):
            return None
        return start, start + task.duration_minutes

    def detect_conflicts(self) -> list[str]:
        """Return a warning for every pair of timed tasks whose times overlap.

        A lightweight O(n^2) pairwise scan: two tasks conflict when their
        time windows overlap (``start_a < end_b and start_b < end_a``), so a
        30-min 08:00 walk clashes with an 08:15 feeding, not just an exact
        08:00 match. Works across pets too — the owner can't be in two places
        at once. Done tasks and untimed tasks are ignored. Returns an empty
        list when there are no conflicts; it never raises.
        """
        warnings: list[str] = []
        # Compute each task's window once (task, start, end); skip done and
        # untimed tasks up front so the pairwise scan only sees real candidates.
        timed = []
        for task in self.tasks:
            if task.done:
                continue
            window = self._window(task)
            if window is not None:
                timed.append((task, window[0], window[1]))

        # combinations() yields each unordered pair once — no index bookkeeping.
        for (first, start_a, end_a), (second, start_b, end_b) in combinations(timed, 2):
            if start_a < end_b and start_b < end_a:
                warnings.append(
                    f"⚠️  Conflict: '{first.name}' ({first.pet_name}, "
                    f"{first.scheduled_time}) overlaps '{second.name}' "
                    f"({second.pet_name}, {second.scheduled_time})"
                )
        return warnings

    def filter_by_time(self) -> list[Task]:
        """Drop tasks that don't fit the available time budget."""
        raise NotImplementedError

    def generate_plan(self) -> DailyPlan:
        """Build and return a DailyPlan from the candidate tasks."""
        raise NotImplementedError

    def explain(self) -> str:
        """Explain why tasks were included or skipped (also stored on DailyPlan.reasoning)."""
        raise NotImplementedError
