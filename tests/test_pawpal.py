"""Simple tests for the PawPal+ logic layer (pawpal_system.py)."""

from datetime import date, timedelta

from pawpal_system import Pet, Scheduler, Task


def _sample_tasks():
    """Two pets' worth of tasks, added out of time order, one marked done."""
    dog = Pet("Biscuit", "Dog")
    dog.add_task(Task("Fetch", 20, "low", "enrichment", scheduled_time="17:30"))
    dog.add_task(Task("Walk", 30, "high", "walk", scheduled_time="08:00"))

    cat = Pet("Mittens", "Cat")
    feeding = Task("Feeding", 5, "high", "feeding", scheduled_time="07:45")
    feeding.mark_done()
    cat.add_task(feeding)
    cat.add_task(Task("Litter", 15, "medium", "grooming", scheduled_time="09:15"))

    return dog.get_tasks() + cat.get_tasks()


def test_task_completion():
    """Calling mark_done() changes the task's status to done."""
    task = Task("Morning walk", duration_minutes=30, priority="high", category="walk")
    assert task.done is False
    task.mark_done()
    assert task.done is True


def test_task_addition():
    """Adding a task to a Pet increases that pet's task count."""
    pet = Pet("Biscuit", "Dog", "Golden Retriever")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task("Feeding", duration_minutes=10, priority="high", category="feeding"))
    assert len(pet.get_tasks()) == 1


def test_add_task_stamps_pet_name():
    """Pet.add_task records which pet the task belongs to."""
    pet = Pet("Biscuit", "Dog")
    task = Task("Feeding", 10, "high", "feeding")
    pet.add_task(task)
    assert task.pet_name == "Biscuit"


def test_sort_by_time_orders_chronologically():
    """sort_by_time() returns tasks earliest-first regardless of entry order."""
    scheduler = Scheduler(tasks=_sample_tasks())
    times = [task.scheduled_time for task in scheduler.sort_by_time()]
    assert times == ["07:45", "08:00", "09:15", "17:30"]


def test_sort_by_time_puts_untimed_tasks_last():
    """Tasks with no scheduled_time sort to the end of the day."""
    scheduler = Scheduler(
        tasks=[
            Task("Anytime meds", 5, "high", "meds"),  # no scheduled_time
            Task("Walk", 30, "high", "walk", scheduled_time="08:00"),
        ]
    )
    names = [task.name for task in scheduler.sort_by_time()]
    assert names == ["Walk", "Anytime meds"]


def test_filter_by_status():
    """filter_by_status splits done from not-done tasks."""
    scheduler = Scheduler(tasks=_sample_tasks())
    assert [t.name for t in scheduler.filter_by_status(done=True)] == ["Feeding"]
    assert len(scheduler.filter_by_status(done=False)) == 3


def test_filter_by_pet():
    """filter_by_pet returns only the named pet's tasks."""
    scheduler = Scheduler(tasks=_sample_tasks())
    assert len(scheduler.filter_by_pet("Biscuit")) == 2
    assert all(t.pet_name == "Mittens" for t in scheduler.filter_by_pet("Mittens"))


def test_daily_task_next_occurrence_is_tomorrow():
    """A daily task's next occurrence is due one day later, and not done."""
    today = date(2026, 7, 4)
    task = Task("Feeding", 10, "high", "feeding", frequency="daily", due_date=today)
    nxt = task.next_occurrence()
    assert nxt.due_date == today + timedelta(days=1)
    assert nxt.done is False


def test_weekly_task_next_occurrence_is_next_week():
    """A weekly task's next occurrence is due seven days later."""
    today = date(2026, 7, 4)
    task = Task("Bath", 30, "medium", "grooming", frequency="weekly", due_date=today)
    assert task.next_occurrence().due_date == today + timedelta(weeks=1)


def test_once_task_does_not_recur():
    """A one-off task has no next occurrence."""
    task = Task("Vet visit", 60, "high", "meds", frequency="once")
    assert task.next_occurrence() is None


def test_complete_task_auto_queues_recurring_instance():
    """Completing a recurring task marks it done and adds the next instance to the pet."""
    pet = Pet("Biscuit", "Dog")
    walk = Task("Walk", 30, "high", "walk", frequency="daily", due_date=date(2026, 7, 4))
    pet.add_task(walk)

    new_task = pet.complete_task(walk)

    assert walk.done is True
    assert len(pet.get_tasks()) == 2          # original + next occurrence
    assert new_task in pet.get_tasks()
    assert new_task.done is False
    assert new_task.pet_name == "Biscuit"     # add_task re-stamps the pet
    assert new_task.due_date == date(2026, 7, 5)


def test_complete_task_once_does_not_queue():
    """Completing a one-off task marks it done without adding anything."""
    pet = Pet("Mittens", "Cat")
    task = Task("Vet visit", 60, "high", "meds", frequency="once")
    pet.add_task(task)

    assert pet.complete_task(task) is None
    assert len(pet.get_tasks()) == 1
    assert task.done is True


def test_detect_conflicts_flags_overlap():
    """Two tasks whose time windows overlap produce one warning."""
    scheduler = Scheduler(
        tasks=[
            Task("Walk", 30, "high", "walk", scheduled_time="08:00", pet_name="Biscuit"),
            Task("Feeding", 10, "high", "feeding", scheduled_time="08:15", pet_name="Mittens"),
        ]
    )
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Feeding" in warnings[0]


def test_no_conflict_when_times_do_not_overlap():
    """Back-to-back tasks that don't overlap produce no warnings."""
    scheduler = Scheduler(
        tasks=[
            Task("Walk", 30, "high", "walk", scheduled_time="08:00"),
            Task("Feeding", 10, "high", "feeding", scheduled_time="08:30"),
        ]
    )
    assert scheduler.detect_conflicts() == []


def test_conflict_ignores_untimed_and_done_tasks():
    """Untimed tasks and completed tasks are excluded from conflict checks."""
    done_walk = Task("Walk", 30, "high", "walk", scheduled_time="08:00")
    done_walk.mark_done()
    scheduler = Scheduler(
        tasks=[
            done_walk,  # same time as feeding, but already done
            Task("Anytime meds", 5, "high", "meds"),  # no scheduled_time
            Task("Feeding", 10, "high", "feeding", scheduled_time="08:00"),
        ]
    )
    assert scheduler.detect_conflicts() == []
