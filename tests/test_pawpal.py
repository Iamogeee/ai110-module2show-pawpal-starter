"""Simple tests for the PawPal+ logic layer (pawpal_system.py)."""

from pawpal_system import Pet, Task


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
