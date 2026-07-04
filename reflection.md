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

The scheduler currently reasons over four constraints: each task's **scheduled time** (used both to order the day and to detect overlaps), its **priority** (ranked through the `PRIORITY_ORDER` constant), its **completion status** (done tasks drop out of conflict checks and can be filtered away), and which **pet** it belongs to (so a busy day can be narrowed one animal at a time). The owner's **time budget** (`available_minutes`) is captured and passed into the `Scheduler`, but the budget-fitting step (`filter_by_time`/`generate_plan`) is designed and not yet implemented.

I decided **time and priority** matter most, because they answer the two questions a pet owner actually asks — "when does this happen?" and "if I can't do everything, what comes first?" Conflict detection came next, since a schedule that quietly double-books the owner is worse than useless. Preferences were deliberately left as a lower-priority extension point rather than a core constraint.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

**Conflict detection *warns* about overlaps rather than resolving them, and does so with a naive O(n²) pairwise scan over same-day "HH:MM" times.** `Scheduler.detect_conflicts()` compares every pair of timed, not-done tasks and checks whether their `[start, start + duration)` windows overlap (`start_a < end_b and start_b < end_a`). I deliberately chose *overlap* detection over the simpler *exact-time-match* check, because a 30-minute 08:00 walk genuinely clashes with an 08:10 feeding even though the start times differ — exact matching would miss that. The tradeoffs I accepted in exchange:

- **Warn, don't auto-resolve.** The scheduler surfaces a human-readable warning and leaves the decision to the owner rather than silently reshuffling or dropping a task. For a pet-care assistant that's the safer default — automatically bumping a medication because it overlapped a walk could be harmful, and the owner has context the app doesn't.
- **O(n²) pairwise scan.** Comparing all pairs is quadratic, but a realistic day has well under ~20 tasks, so this is effectively instant; a sweep-line algorithm would be faster asymptotically but adds complexity that buys nothing at this scale.
- **Single-day, string-based times.** Times are stored as `"HH:MM"` strings converted to minutes-since-midnight, which assumes every task falls within one calendar day (a task crossing midnight would compute a misleading window). That holds for daily pet care and keeps sorting trivial (strings sort chronologically), so real `datetime` objects would be over-engineering here.

These are all reasonable because PawPal+ optimizes for a single owner's daily routine — small task counts, within-day times, and a human kept in the loop — not for large-scale or multi-day calendar scheduling.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used my AI coding assistant across every phase: brainstorming the UML, generating the class skeletons from that diagram, drafting the test suite, reviewing `pawpal_system.py` for missing edge cases, wiring the `Scheduler` into the Streamlit UI, and finally regenerating the UML to match the finished code.

The features that were **most effective for building the scheduler** were:

- **Whole-file context review** — attaching `pawpal_system.py` and asking "what edge cases am I missing?" or "what UML updates should I make based on this implementation?" turned the AI into a second reviewer that could see the whole design at once, not just the line I was editing.
- **Test generation** — the assistant drafted a broad suite (sorting, recurrence, conflict detection, plus edge cases like empty inputs, malformed times, and exact-time ties) far faster than I would have enumerated them by hand.
- **Running the code and reading the output** — the assistant didn't just suggest code; it ran `pytest` and `python main.py`, launched the Streamlit app, and fed the real output back into the next decision. That closed the loop between "suggested" and "verified."

The most helpful prompts were **specific and verification-oriented** — naming the file, stating the goal, and asking the AI to check its work against real output — rather than open-ended "write my scheduler" requests.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

**One example of a suggestion I modified to keep the design clean:** during the code review the assistant flagged that `available_minutes` and `preferences` were duplicated on both `Owner` and `Scheduler` and could be collapsed into one. I rejected that simplification on purpose — the duplication is what keeps the `Scheduler` decoupled from `Owner`, so it can be unit-tested with a plain list of tasks and a number, without constructing a whole object graph. Keeping the two apart made the 24-test suite simple to write.

A second, smaller moment: while writing a conflict-detection test, the AI-drafted assertion expected *three* overlapping pairs, but the run produced *two* — because two of the tasks didn't actually overlap. Rather than "fix" the working code to match the test, I corrected the test's assumption. The lesson was that a failing test is not automatically the code's fault.

I evaluated AI suggestions primarily by **running things**: `pytest` (all 24 tests green), `python main.py` (checking the printed schedule matched what I expected), and launching the Streamlit app to confirm the UI behaved. Code I couldn't verify by running, I read line by line against the UML before accepting.

**c. AI strategy: sessions and being the lead architect**

- How did using separate chat sessions for different phases help you stay organized?
- What did you learn about being the "lead architect" when collaborating with powerful AI tools?

**Separate chat sessions per phase kept each conversation's context tight.** Design, implementation, and this finalization phase each had their own session, so the AI's suggestions stayed relevant to the goal in front of me instead of dragging in stale assumptions from an earlier step. A design session could stay abstract (classes, responsibilities, relationships) without the AI prematurely writing code; an implementation session could focus on one method at a time; and the finalization session could concentrate on tests, docs, and reconciling the UML. It also made each session's history easy to revisit later — the git commits line up with the phase boundaries.

**On being the "lead architect":** the biggest takeaway is that a powerful AI tool shifts my job from *writing* code to *deciding* about code. The AI is excellent at proposing, generating, and executing quickly — but it will happily add complexity (extra fields, `datetime` refactors, collapsed abstractions) that I don't need. My value was in the judgment calls: holding the line on the data/logic/output separation, choosing "warn, don't auto-resolve" for conflicts, and rejecting simplifications that would have hurt testability. The AI accelerated the work enormously, but the design decisions, the verification, and the "no, keep it simple" were mine to own. The tool proposes; the architect disposes.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

The 24-test suite (`tests/test_pawpal.py`) covers the four core behaviors plus their edge cases: **sorting** (chronological order regardless of entry order, untimed tasks last), **recurrence** (a completed daily task auto-queues tomorrow's instance; weekly advances a week; `once` and unknown frequencies never recur), **conflict detection** (overlapping and *identical* start times flagged, each pair reported once, done/untimed/malformed-time tasks safely ignored), and **filtering** (by pet and by status). Edge cases include empty schedulers, pets with no tasks, single tasks, garbage time strings, and zero-duration tasks.

These mattered because they are exactly the behaviors a user would notice if they broke — a mis-sorted day, a missed medication conflict, or a crash on a typo'd time would all destroy trust in the app. Testing the edge cases in particular pins down the "never crash, just warn" contract the scheduler promises.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'm at about **4 out of 5**. Every implemented behavior is covered and passing, so I'm confident in sorting, filtering, recurrence, and conflict detection. I'm holding back the last star because `generate_plan`, `filter_by_time`, `total_time`, `summary`, and `explain` are not yet implemented, so the end-to-end daily plan can't be fully vouched for.

With more time I'd test: the **time-budget fitting** logic once implemented (budget of 0, a single task longer than the whole budget, budget exactly equal to total task time), **priority tie-breaking** when two tasks share a start time, and **midnight-crossing** tasks, which the current within-day time model doesn't handle.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with the **clean separation between data (Owner/Pet/Task), logic (Scheduler), and output (DailyPlan)**. That decision paid off everywhere: the scheduler was trivial to unit-test in isolation, the Streamlit UI just calls the same methods the CLI demo does, and adding conflict detection and recurrence didn't require touching the UI at all. The 24 passing tests are a close second — they gave me the confidence to refactor freely.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I'd implement the pieces still stubbed out — `generate_plan`, `filter_by_time`, `total_time`, `summary`, and `explain` — so the app produces a real time-budgeted daily plan with a human-readable justification, not just a sorted list. I'd also move from `"HH:MM"` strings to real `datetime`/`time` objects so tasks can cross midnight and so priority can cleanly break ties between same-time tasks.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The most important thing I learned is that **with a powerful AI assistant, the scarce skill is judgment, not typing.** The AI could generate classes, tests, and UI faster than I could review them — so my real job was owning the architecture: keeping the design simple, deciding which AI suggestions to accept, and verifying everything by actually running it. Good structure (the data/logic/output split) plus good verification (tests and real runs) is what let me move fast *and* trust the result.
