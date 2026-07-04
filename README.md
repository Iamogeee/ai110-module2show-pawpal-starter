# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Sample of the CLI output produced by running `python3 main.py`:

```
====================================================
Today's Schedule for Ogenna
Time available today: 120 min
====================================================

Tasks as entered (unsorted):
----------------------------------------------------
  [ ] 17:30  Fetch / enrichment    20 min  (Biscuit, low)
  [ ] 08:00  Morning walk          30 min  (Biscuit, high)
  [ ] 12:00  Feeding               10 min  (Biscuit, high)
  [✓] 09:15  Litter box cleaning   15 min  (Mittens, medium)
  [ ] 08:10  Feeding                5 min  (Mittens, high)

Sorted by time (sort_by_time):
----------------------------------------------------
  [ ] 08:00  Morning walk          30 min  (Biscuit, high)
  [ ] 08:10  Feeding                5 min  (Mittens, high)
  [✓] 09:15  Litter box cleaning   15 min  (Mittens, medium)
  [ ] 12:00  Feeding               10 min  (Biscuit, high)
  [ ] 17:30  Fetch / enrichment    20 min  (Biscuit, low)

Conflict check (detect_conflicts):
----------------------------------------------------
  ⚠️  Conflict: 'Morning walk' (Biscuit, 08:00) overlaps 'Feeding' (Mittens, 08:10)

Filtered to Biscuit (filter_by_pet):
----------------------------------------------------
  [ ] 17:30  Fetch / enrichment    20 min  (Biscuit, low)
  [ ] 08:00  Morning walk          30 min  (Biscuit, high)
  [ ] 12:00  Feeding               10 min  (Biscuit, high)

Still to do (filter_by_status done=False):
----------------------------------------------------
  [ ] 17:30  Fetch / enrichment    20 min  (Biscuit, low)
  [ ] 08:00  Morning walk          30 min  (Biscuit, high)
  [ ] 12:00  Feeding               10 min  (Biscuit, high)
  [ ] 08:10  Feeding                5 min  (Mittens, high)

Already done (filter_by_status done=True):
----------------------------------------------------
  [✓] 09:15  Litter box cleaning   15 min  (Mittens, medium)

====================================================
Recurring tasks (complete_task auto-queues the next one)
====================================================

Before completing: Biscuit has 4 tasks.
  Completing 'Daily walk' (due 2026-07-04, daily)...
After completing:  Biscuit has 5 tasks.
  Original is now done: True
  Auto-queued next instance due: 2026-07-05 (done=False)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
tests/test_pawpal.py ...............                                     [100%]

============================== 15 passed in 0.02s ==============================
```

## 📐 Smarter Scheduling

Beyond the basic data model, `Scheduler` (in `pawpal_system.py`) adds four pieces of
scheduling intelligence. Each is a small, independently testable method:

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Orders tasks chronologically. `scheduled_time` is a zero-padded `"HH:MM"` string, so a `sorted()` lambda key sorts it as text; untimed tasks fall back to `"99:99"` and land at the end of the day. |
| Filtering | `Scheduler.filter_by_status(done)`, `Scheduler.filter_by_pet(pet_name)` | Narrows the task list to just to-do vs. done tasks, or to a single pet. `Pet.add_task()` stamps each task's `pet_name` so a flattened list stays filterable. |
| Conflict detection | `Scheduler.detect_conflicts()` (helper: `Scheduler._window()`) | Pairwise scan (via `itertools.combinations`) that flags any two timed, not-done tasks whose `[start, start + duration)` windows overlap — across pets too. Returns a list of warning strings (empty = no conflicts); never raises. |
| Recurring tasks | `Task.next_occurrence()`, `Pet.complete_task(task)` | Completing a `daily`/`weekly` task marks it done and auto-queues a fresh instance for the next due date, computed with `timedelta` (`days=1` / `weeks=1`). A `once` task never recurs. |

### Sorting behavior
`Scheduler.sort_by_time()` returns tasks earliest-first. Because times are stored as
`"HH:MM"` text, string comparison is already chronological (`"08:00" < "13:30"`), so the
sort key is simply `lambda task: task.scheduled_time or "99:99"`.

### Filtering behavior
`Scheduler.filter_by_status(done=False)` returns the still-to-do tasks (or the finished
ones with `done=True`); `Scheduler.filter_by_pet("Biscuit")` returns just that pet's tasks.

### Conflict detection logic
`Scheduler.detect_conflicts()` compares every pair of timed, not-done tasks and reports an
overlap when `start_a < end_b and start_b < end_a`. It detects *overlapping durations*, not
just identical start times — so a 30-min 08:00 walk is flagged against an 08:10 feeding. It
warns rather than auto-resolving, leaving the final call to the owner.

### Recurring task logic
`Pet.complete_task(task)` is the recurrence hook: it marks the task done, and if the task is
`daily` or `weekly`, `Task.next_occurrence()` builds a not-done copy with its `due_date`
advanced by the right `timedelta`, which `complete_task` adds back to the pet.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
