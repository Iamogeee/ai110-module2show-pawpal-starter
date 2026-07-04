"""PawPal+ demo script.

Builds a small owner/pet/task setup using the classes in pawpal_system.py
and prints today's care schedule to the terminal.

Step 2 demo: tasks are added *out of time order* on purpose, then a Scheduler
sorts them chronologically and filters them by pet and by completion status.

Run with:
    python main.py
"""

from datetime import date

from pawpal_system import Owner, Pet, Task, Scheduler


def build_demo_owner() -> Owner:
    """Create an owner with two pets and a few care tasks each.

    Tasks are intentionally added in a scrambled time order so the
    sort-by-time step below has something real to fix.
    """
    owner = Owner(name="Ogenna", available_minutes=120)

    # Pet 1 — note the times are NOT in order as entered.
    biscuit = Pet(name="Biscuit", species="Dog", breed="Golden Retriever")
    biscuit.add_task(Task("Fetch / enrichment", 20, "low", "enrichment", scheduled_time="17:30"))
    biscuit.add_task(Task("Morning walk", 30, "high", "walk", scheduled_time="08:00"))
    biscuit.add_task(Task("Feeding", 10, "high", "feeding", scheduled_time="12:00"))

    # Pet 2 — Mittens' 08:10 feeding overlaps Biscuit's 08:00 walk on purpose
    # so the conflict detector has something to catch.
    mittens = Pet(name="Mittens", species="Cat", breed="Tabby")
    mittens.add_task(Task("Litter box cleaning", 15, "medium", "grooming", scheduled_time="09:15"))
    mittens.add_task(Task("Feeding", 5, "high", "feeding", scheduled_time="08:10"))

    owner.add_pet(biscuit)
    owner.add_pet(mittens)

    # Mark one task done so the status filter has something to hide.
    # (Litter box, not the 08:10 feeding — the feeding needs to stay active
    # so the conflict detector can catch it against Biscuit's 08:00 walk.)
    mittens.get_tasks()[0].mark_done()  # 09:15 Litter box cleaning

    return owner


def print_tasks(title: str, tasks: list[Task]) -> None:
    """Print a labeled list of tasks with time, pet, duration, and priority."""
    print(f"\n{title}")
    print("-" * 52)
    if not tasks:
        print("  (none)")
        return
    for task in tasks:
        time_label = task.scheduled_time or "  —  "
        status = "✓" if task.done else " "
        print(
            f"  [{status}] {time_label}  {task.name:<20} "
            f"{task.duration_minutes:>3} min  ({task.pet_name}, {task.priority})"
        )


def main() -> None:
    owner = build_demo_owner()

    print("=" * 52)
    print(f"Today's Schedule for {owner.name}")
    print(f"Time available today: {owner.available_minutes} min")
    print("=" * 52)

    scheduler = Scheduler(
        tasks=owner.get_all_tasks(),
        available_minutes=owner.available_minutes,
    )

    # As entered — deliberately out of time order.
    print_tasks("Tasks as entered (unsorted):", scheduler.tasks)

    # Sorting by time.
    print_tasks("Sorted by time (sort_by_time):", scheduler.sort_by_time())

    # Conflict detection: warn about overlapping time windows.
    print("\nConflict check (detect_conflicts):")
    print("-" * 52)
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No scheduling conflicts. ")

    # Filtering by pet name.
    print_tasks("Filtered to Biscuit (filter_by_pet):", scheduler.filter_by_pet("Biscuit"))

    # Filtering by completion status.
    print_tasks("Still to do (filter_by_status done=False):", scheduler.filter_by_status(done=False))
    print_tasks("Already done (filter_by_status done=True):", scheduler.filter_by_status(done=True))

    # Recurring tasks: completing a daily task auto-queues tomorrow's instance.
    print("\n" + "=" * 52)
    print("Recurring tasks (complete_task auto-queues the next one)")
    print("=" * 52)

    biscuit = owner.get_pets()[0]
    daily_walk = Task(
        "Daily walk", 30, "high", "walk",
        scheduled_time="08:00", frequency="daily", due_date=date(2026, 7, 4),
    )
    biscuit.add_task(daily_walk)
    print(f"\nBefore completing: {biscuit.name} has {len(biscuit.get_tasks())} tasks.")
    print(f"  Completing '{daily_walk.name}' (due {daily_walk.due_date}, {daily_walk.frequency})...")

    next_walk = biscuit.complete_task(daily_walk)

    print(f"After completing:  {biscuit.name} has {len(biscuit.get_tasks())} tasks.")
    print(f"  Original is now done: {daily_walk.done}")
    print(f"  Auto-queued next instance due: {next_walk.due_date} (done={next_walk.done})")


if __name__ == "__main__":
    main()
