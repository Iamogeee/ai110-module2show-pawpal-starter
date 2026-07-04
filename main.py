"""PawPal+ demo script.

Builds a small owner/pet/task setup using the classes in pawpal_system.py
and prints today's care schedule to the terminal.

Run with:
    python main.py
"""

from pawpal_system import Owner, Pet, Task


def build_demo_owner() -> Owner:
    """Create an owner with two pets and a few care tasks each."""
    owner = Owner(name="Ogenna", available_minutes=120)

    # Pet 1
    biscuit = Pet(name="Biscuit", species="Dog", breed="Golden Retriever")
    biscuit.add_task(Task("Morning walk", duration_minutes=30, priority="high", category="walk"))
    biscuit.add_task(Task("Feeding", duration_minutes=10, priority="high", category="feeding"))
    biscuit.add_task(Task("Fetch / enrichment", duration_minutes=20, priority="low", category="enrichment"))

    # Pet 2
    mittens = Pet(name="Mittens", species="Cat", breed="Tabby")
    mittens.add_task(Task("Feeding", duration_minutes=5, priority="high", category="feeding"))
    mittens.add_task(Task("Litter box cleaning", duration_minutes=15, priority="medium", category="grooming"))

    owner.add_pet(biscuit)
    owner.add_pet(mittens)
    return owner


def print_schedule(owner: Owner) -> None:
    """Print today's schedule for every pet the owner has."""
    print("=" * 40)
    print(f"Today's Schedule for {owner.name}")
    print(f"Time available today: {owner.available_minutes} min")
    print("=" * 40)

    total_minutes = 0
    for pet in owner.get_pets():
        print(f"\n{pet.name} ({pet.breed} {pet.species})")
        for task in pet.get_tasks():
            print(
                f"  - {task.name:<22} {task.duration_minutes:>3} min"
                f"  [priority: {task.priority}]"
            )
            total_minutes += task.duration_minutes

    print("\n" + "-" * 40)
    print(f"Total care time needed: {total_minutes} min")
    print("-" * 40)


def main() -> None:
    owner = build_demo_owner()
    print_schedule(owner)


if __name__ == "__main__":
    main()
