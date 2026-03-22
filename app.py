import importlib
import pawpal_system as _ps
importlib.reload(_ps)

import streamlit as st
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, PawPalSystem, Scheduler

# session_state objects were created from the old class definition.
# Re-point their __class__ to the freshly reloaded version so new
# methods (complete_task, filter_tasks, etc.) are immediately available.
if "system" in st.session_state:
    st.session_state.system.__class__ = _ps.PawPalSystem

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

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []


if "pet" not in st.session_state:
    st.session_state.pet = Pet(
        pet_name=pet_name,
        date_of_birth=date(2020, 1, 1),
        age=4,
        species=species,
        breed="Unknown"
    )

if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        owner_name=owner_name,
        date_of_birth=date(1990, 1, 1),
        age=34,
        availability="09:00-17:00",
        preferences="walks, feeding"
    )

if "system" not in st.session_state:
    system = PawPalSystem()
    system.add_owner(st.session_state.owner)
    system.add_pet(st.session_state.pet, st.session_state.owner.owner_id)
    st.session_state.system = system

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

if st.button("Add task"):
    task = Task(
        description=task_title,
        owner_id=st.session_state.owner.owner_id,
        pet_id=st.session_state.pet.pet_id,
        priority=priority,
        scheduled_date=date.today(),
        duration=timedelta(minutes=int(duration)),
        frequency=frequency,
    )
    st.session_state.system.add_task(task)
    st.session_state.tasks.append(
        {"title": task_title, "duration_minutes": int(duration), "priority": priority, "frequency": frequency}
    )

# --- Filters ---
st.markdown("#### Filter tasks")
filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    filter_status = st.selectbox("By status", ["all", "pending", "completed"])
with filter_col2:
    filter_pet = st.selectbox("By pet", ["all pets", st.session_state.pet.pet_name])

system: PawPalSystem = st.session_state.system

# Map UI selections to filter_tasks() arguments
status_arg = {"all": None, "pending": False, "completed": True}[filter_status]
pet_arg = None if filter_pet == "all pets" else filter_pet

all_sys_tasks = system.filter_tasks(pet_name=pet_arg, completed=status_arg)

if all_sys_tasks:
    st.write("Current tasks (sorted by scheduled time):")
    sorted_tasks = sorted(
        [t for t in all_sys_tasks if t.scheduled_start_time],
        key=lambda t: t.scheduled_start_time,
    ) + [t for t in all_sys_tasks if not t.scheduled_start_time]

    for t in sorted_tasks:
        col_info, col_btn = st.columns([4, 1])
        with col_info:
            status_icon = "✅" if t.completion_status else "🔲"
            start = t.scheduled_start_time.strftime("%H:%M") if t.scheduled_start_time else "TBD"
            st.markdown(
                f"{status_icon} **{t.description}** &nbsp; `{t.priority}` &nbsp; "
                f"`{t.frequency}` &nbsp; {start} &nbsp; "
                f"`{int(t.duration.total_seconds() // 60)} min`"
            )
        with col_btn:
            if not t.completion_status:
                if st.button("Mark done", key=f"complete_{t.task_id}"):
                    next_task = system.complete_task(t.task_id)
                    if next_task:
                        st.success(
                            f"Done! Next **{next_task.description}** scheduled for {next_task.scheduled_date}."
                        )
                    else:
                        st.success("Task marked complete.")
                    st.rerun()
else:
    st.info("No tasks match the current filters.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        plan = st.session_state.system.create_plan(
            st.session_state.owner.owner_id,
            date.today(),
        )
        scheduled = plan.view_plan()
        explanations = plan.get_explanations()

        if scheduled:
            st.success(f"Schedule for {date.today()} — {len(scheduled)} task(s) planned.")
            st.table([
                {
                    "Task": t.description,
                    "Start": str(t.scheduled_start_time),
                    "End": str(t.scheduled_end_time),
                    "Priority": t.priority,
                }
                for t in scheduled
            ])
        else:
            st.warning("No tasks fit within the availability window.")

        with st.expander("Scheduling explanations"):
            for note in explanations:
                st.write(f"- {note}")

        warnings = plan.get_conflict_warnings()
        if warnings:
            st.warning(f"⚠️ {len(warnings)} scheduling conflict(s) detected:")
            for msg in warnings:
                st.write(f"- {msg}")


