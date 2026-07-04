import streamlit as st

from pawpal_system import Owner, Pet, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
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

    if st.button("Add task"):
        # Pet.add_task() attaches a real Task object to the chosen pet.
        selected_pet.add_task(
            Task(
                name=task_title,
                duration_minutes=int(duration),
                priority=priority,
                category=category,
            )
        )
else:
    st.caption("Add a pet first, then you can give it tasks.")

# Read the objects back out of the owner and render them.
for pet in owner.get_pets():
    st.write(f"**{pet.name}** ({pet.species})")
    tasks = pet.get_tasks()
    if tasks:
        st.table(
            [
                {
                    "task": t.name,
                    "duration_minutes": t.duration_minutes,
                    "priority": t.priority,
                    "category": t.category,
                }
                for t in tasks
            ]
        )
    else:
        st.caption("No tasks yet for this pet.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    st.warning(
        "Not implemented yet. Next step: create your scheduling logic (classes/functions) and call it here."
    )
    st.markdown(
        """
Suggested approach:
1. Design your UML (draft).
2. Create class stubs (no logic).
3. Implement scheduling behavior.
4. Connect your scheduler here and display results.
"""
    )
