import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to **PawPal+**, a pet care planning assistant.

Add your pets and their care tasks below, give each task a time, and PawPal+ will
sort your day chronologically, flag any scheduling conflicts, and roll recurring
tasks forward automatically.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")

# One Owner object lives in session_state so it survives Streamlit reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

owner = st.session_state.owner
owner.name = st.text_input("Owner name", value=owner.name)

st.markdown("### Add a Pet")
pet_col1, pet_col2 = st.columns(2)
with pet_col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with pet_col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    # Owner.add_pet() is the method that handles the new pet's data.
    owner.add_pet(Pet(name=pet_name, species=species))

pets = owner.get_pets()
if not pets:
    st.info("No pets yet. Add one above.")

st.markdown("### Add a Task")
if pets:
    # Pick which pet the task belongs to (tasks live on a Pet, per the UML).
    pet_names = [pet.name for pet in pets]
    selected_pet_name = st.selectbox("For which pet?", pet_names)
    selected_pet = pets[pet_names.index(selected_pet_name)]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col4:
        category = st.selectbox(
            "Category", ["walk", "feeding", "meds", "grooming", "enrichment"]
        )

    time_col, freq_col = st.columns(2)
    with time_col:
        # A time is optional — untimed tasks sort to the end of the day and are
        # skipped by conflict detection, matching the Scheduler's behavior.
        has_time = st.checkbox("Set a specific time?", value=True)
        start_time = st.time_input("Start time", value=None) if has_time else None
    with freq_col:
        frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])

    if st.button("Add task"):
        # Scheduler expects a zero-padded "HH:MM" string so it sorts as text.
        scheduled_time = start_time.strftime("%H:%M") if start_time else ""
        # Pet.add_task() attaches a real Task object to the chosen pet.
        selected_pet.add_task(
            Task(
                name=task_title,
                duration_minutes=int(duration),
                priority=priority,
                category=category,
                scheduled_time=scheduled_time,
                frequency=frequency,
            )
        )
else:
    st.caption("Add a pet first, then you can give it tasks.")

st.divider()

st.subheader("📅 Today's Schedule")

all_tasks = owner.get_all_tasks()
if not all_tasks:
    st.info("No tasks yet. Add a pet and a task above to see the schedule.")
else:
    # Feed every task across all pets into the Scheduler — the smart layer.
    scheduler = Scheduler(tasks=all_tasks)

    # --- Conflict warnings: shown first, since they are the most actionable ---
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        # One grouped amber box with a count, then a plain-language bulleted
        # list — easier to scan than one box per conflict. Amber (not red)
        # because an overlap is something to look at, not a system failure.
        st.warning(
            f"**⚠️ {len(conflicts)} scheduling conflict"
            f"{'s' if len(conflicts) > 1 else ''} found** — you can't be in two "
            "places at once. Try moving one of each pair to a different time:\n\n"
            + "\n".join(f"- {c}" for c in conflicts)
        )
    else:
        st.success("✅ No scheduling conflicts — every timed task has its own slot.")

    # --- Filters let the owner narrow the view by pet and by status ---
    pet_names = [pet.name for pet in owner.get_pets()]
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        pet_filter = st.selectbox("Show tasks for", ["All pets"] + pet_names)
    with filter_col2:
        status_filter = st.selectbox("Status", ["To do", "Done", "All"])

    # Sort chronologically first, then apply the chosen filters on top.
    visible = scheduler.sort_by_time()
    if pet_filter != "All pets":
        visible = [t for t in visible if t.pet_name == pet_filter]
    if status_filter == "To do":
        visible = [t for t in visible if not t.done]
    elif status_filter == "Done":
        visible = [t for t in visible if t.done]

    if visible:
        st.table(
            [
                {
                    "": "✓" if t.done else "○",
                    "Time": t.scheduled_time or "—",
                    "Task": t.name,
                    "Pet": t.pet_name,
                    "Duration": f"{t.duration_minutes} min",
                    "Priority": t.priority,
                    "Repeats": t.frequency,
                }
                for t in visible
            ]
        )
    else:
        st.caption("No tasks match this filter.")

    st.divider()

    # --- Complete a task: demonstrates the recurrence auto-queue in the UI ---
    st.markdown("### ✅ Mark a task done")
    st.caption(
        "Completing a daily or weekly task automatically queues the next occurrence."
    )
    # Build (pet, task) pairs for tasks that are still to do, so we can call
    # Pet.complete_task() on the right pet.
    open_pairs = [
        (pet, task)
        for pet in owner.get_pets()
        for task in pet.get_tasks()
        if not task.done
    ]
    if open_pairs:
        labels = [
            f"{task.name} — {pet.name}"
            + (f" @ {task.scheduled_time}" if task.scheduled_time else "")
            for pet, task in open_pairs
        ]
        choice = st.selectbox("Task to complete", range(len(labels)), format_func=lambda i: labels[i])
        if st.button("Mark done"):
            pet, task = open_pairs[choice]
            queued = pet.complete_task(task)
            if queued is not None:
                st.success(
                    f"Done! Queued the next **{task.frequency}** '{queued.name}' "
                    f"for {queued.due_date}."
                )
            else:
                st.success(f"Done! '{task.name}' is complete.")
            st.rerun()
    else:
        st.caption("Nothing left to do — every task is complete. 🎉")
