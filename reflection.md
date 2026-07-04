# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

These are the three things a user should be able to do in PawPal+:

1. **Add a pet and its care tasks** — The user enters basic owner and pet information, then adds the care tasks that pet needs (walks, feeding, meds, grooming, enrichment), giving each task a duration and a priority.
2. **Generate a daily plan** — The user tells PawPal+ how much time they have available, and the app builds a daily schedule that fits the highest-priority tasks into that time while respecting the owner's constraints and preferences.
3. **See and understand today's plan** — The user views the generated schedule for the day, laid out clearly, along with an explanation of why each task was included (or skipped) so they can trust and adjust the plan.

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML used five classes, each with a single clear responsibility:

- **Owner** — represents the person using the app. Holds the owner's name, the time they have available for the day (`available_minutes`), their care `preferences`, and the list of pets they own. Responsible for managing pets (`add_pet`, `get_pets`) and setting the daily time budget (`set_available_time`).
- **Pet** — represents an animal being cared for. Holds the pet's name, species, breed, and its own list of care tasks. Responsible for managing those tasks (`add_task`, `remove_task`, `get_tasks`).
- **Task** — represents a single unit of care (walk, feeding, meds, grooming, enrichment). Holds its name, duration, priority, category, and a done flag. Responsible for comparing itself to other tasks (`is_higher_priority_than`) and marking itself complete (`mark_done`).
- **Scheduler** — the logic engine. Takes the candidate tasks plus the owner's constraints (time, preferences) and is responsible for sorting (`sort_tasks`), filtering to fit the time budget (`filter_by_time`), producing the plan (`generate_plan`), and explaining its choices (`explain`).
- **DailyPlan** — the output the user sees. Holds the scheduled tasks, the tasks that were skipped, and the date. Responsible for reporting total time (`total_time`) and formatting a human-readable summary (`summary`).

The key design decision was separating the **data** (Owner / Pet / Task) from the **logic** (Scheduler) and the **output** (DailyPlan), so the scheduling rules can be unit-tested without touching the Streamlit UI.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes — after generating the skeleton I had my AI assistant review `pawpal_system.py` for missing relationships and logic bottlenecks. Two changes came out of that review:

1. **Added a `PRIORITY_ORDER` ranking constant.** Originally `priority` was a free-form string, which left `is_higher_priority_than` and `sort_tasks` with no defined ordering (and risked inconsistent comparisons). I added a module-level `{"low": 1, "medium": 2, "high": 3}` map so priority comparison and sorting have a single, consistent source of truth.
2. **Moved the scheduling explanation onto `DailyPlan` (new `reasoning` attribute).** Originally `Scheduler.explain()` returned the reasoning as a separate string, which could drift out of sync with the plan it described. Storing the explanation on the `DailyPlan` it belongs to keeps the plan and its justification together. I updated the UML to match.

I considered, but deliberately did **not** make, two other changes to avoid unnecessary complexity: adding start-time slots to tasks (the README sample shows clock times, but I'll add this only if the scheduler needs true time-slotting), and collapsing the duplicated `available_minutes`/`preferences` between `Owner` and `Scheduler` (the duplication keeps the `Scheduler` decoupled and easy to test).

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
