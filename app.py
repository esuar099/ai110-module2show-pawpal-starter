import importlib
import pawpal_system as _ps
importlib.reload(_ps)

import streamlit as st
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, PawPalSystem, Scheduler

# Patch any existing session_state instances to the freshly reloaded class
if "system" in st.session_state:
    st.session_state.system.__class__ = _ps.PawPalSystem

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")
st.title("🐾 PawPal+")
st.caption("Daily pet care planner — manage owners, pets, tasks, and schedules.")

# ── Bootstrap system on first load ───────────────────────────────────────────
if "system" not in st.session_state:
    system = PawPalSystem()
    owner = Owner(
        owner_name="Jordan",
        date_of_birth=date(1990, 1, 1),
        age=34,
        availability="09:00-17:00",
        preferences="walks, feeding",
    )
    system.add_owner(owner)
    pet = Pet(
        pet_name="Mochi",
        date_of_birth=date(2020, 1, 1),
        age=4,
        species="cat",
        breed="Unknown",
    )
    system.add_pet(pet, owner.owner_id)
    st.session_state.system   = system
    st.session_state.owner_id = owner.owner_id

system: PawPalSystem = st.session_state.system

# owner_id may be missing if system was carried over from an older session
if "owner_id" not in st.session_state:
    st.session_state.owner_id = next(iter(system.owners))

owner: Owner = system.owners[st.session_state.owner_id]

# ── Top-level navigation ──────────────────────────────────────────────────────
tab_owner, tab_tasks, tab_schedule = st.tabs(
    ["👤  Owner & Pets", "📋  Tasks", "📅  Schedule"]
)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — Owner & Pets
# ═════════════════════════════════════════════════════════════════════════════
with tab_owner:

    # ── Owner profile ─────────────────────────────────────────────────────────
    st.subheader("Owner Profile")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Name",         owner.owner_name)
    m2.metric("Age",          owner.age)
    m3.metric("Availability", owner.availability)
    m4.metric("Preferences",  owner.preferences)

    with st.expander("✏️ Edit owner — modify_owner()", expanded=False):
        with st.form("form_modify_owner"):
            c1, c2 = st.columns(2)
            with c1:
                f_name  = st.text_input("Owner name",            value=owner.owner_name)
                f_age   = st.number_input("Age", min_value=1,
                                          max_value=120,          value=owner.age)
                f_dob   = st.date_input("Date of birth",         value=owner.date_of_birth)
            with c2:
                f_avail = st.text_input("Availability (HH:MM-HH:MM)", value=owner.availability)
                f_prefs = st.text_input("Preferences (comma-separated)", value=owner.preferences)
            if st.form_submit_button("Save owner changes", type="primary"):
                owner.modify_owner(
                    owner_name=f_name,
                    date_of_birth=f_dob,
                    age=int(f_age),
                    availability=f_avail,
                    preferences=f_prefs,
                )
                st.success("Owner profile updated.")
                st.rerun()

    st.divider()

    # ── Pet list ──────────────────────────────────────────────────────────────
    st.subheader("Pets")
    pets = list(system.pets.values())

    if pets:
        for pet in pets:
            task_count = len(system.get_tasks_by_pet(pet.pet_id))
            with st.expander(
                f"🐾 **{pet.pet_name}** — {pet.species} / {pet.breed}  "
                f"({task_count} task{'s' if task_count != 1 else ''})",
                expanded=False,
            ):
                pm1, pm2, pm3, pm4 = st.columns(4)
                pm1.metric("Name",    pet.pet_name)
                pm2.metric("Species", pet.species)
                pm3.metric("Breed",   pet.breed)
                pm4.metric("Age",     pet.age)

                with st.form(f"form_edit_pet_{pet.pet_id}"):
                    st.caption("Edit pet — modify_pet()")
                    e1, e2 = st.columns(2)
                    with e1:
                        ep_name    = st.text_input("Pet name",    value=pet.pet_name,
                                                   key=f"pn_{pet.pet_id}")
                        ep_species = st.text_input("Species",     value=pet.species,
                                                   key=f"ps_{pet.pet_id}")
                        ep_dob     = st.date_input("Date of birth", value=pet.date_of_birth,
                                                   key=f"pd_{pet.pet_id}")
                    with e2:
                        ep_breed   = st.text_input("Breed",       value=pet.breed,
                                                   key=f"pb_{pet.pet_id}")
                        ep_age     = st.number_input("Age", min_value=0, max_value=30,
                                                     value=pet.age, key=f"pa_{pet.pet_id}")
                    save_col, remove_col = st.columns(2)
                    with save_col:
                        if st.form_submit_button("Save pet changes"):
                            pet.modify_pet(
                                pet_name=ep_name,
                                date_of_birth=ep_dob,
                                age=int(ep_age),
                                species=ep_species,
                                breed=ep_breed,
                            )
                            st.success(f"{ep_name} updated.")
                            st.rerun()
                    with remove_col:
                        if st.form_submit_button("🗑 Remove pet + tasks"):
                            system.remove_pet(pet.pet_id)
                            st.warning(f"Removed {pet.pet_name} and all linked tasks.")
                            st.rerun()
    else:
        st.info("No pets added yet.")

    st.divider()

    # ── Add pet ───────────────────────────────────────────────────────────────
    st.subheader("Add a Pet — add_pet()")
    with st.form("form_add_pet"):
        a1, a2 = st.columns(2)
        with a1:
            np_name    = st.text_input("Pet name",    value="Buddy")
            np_species = st.selectbox("Species",      ["dog", "cat", "other"])
            np_dob     = st.date_input("Date of birth", value=date(2019, 1, 1))
        with a2:
            np_breed   = st.text_input("Breed",       value="Unknown")
            np_age     = st.number_input("Age", min_value=0, max_value=30, value=2)
        if st.form_submit_button("Add pet", type="primary"):
            new_pet = Pet(
                pet_name=np_name,
                date_of_birth=np_dob,
                age=int(np_age),
                species=np_species,
                breed=np_breed,
            )
            system.add_pet(new_pet, owner.owner_id)
            st.success(f"Added **{np_name}**!")
            st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — Tasks
# ═════════════════════════════════════════════════════════════════════════════
with tab_tasks:

    pet_options: dict = {p.pet_name: p.pet_id for p in system.pets.values()}

    if not pet_options:
        st.warning("Add a pet on the **Owner & Pets** tab before adding tasks.")
    else:
        # ── Add task ──────────────────────────────────────────────────────────
        st.subheader("Add Task — add_task()")
        with st.form("form_add_task"):
            t1, t2 = st.columns(2)
            with t1:
                ta_desc      = st.text_input("Description",  value="Morning walk")
                ta_pet       = st.selectbox("Pet",           list(pet_options.keys()))
                ta_priority  = st.selectbox("Priority",      ["low", "medium", "high"], index=2)
            with t2:
                ta_date      = st.date_input("Scheduled date", value=date.today())
                ta_duration  = st.number_input("Duration (minutes)",
                                               min_value=1, max_value=480, value=30)
                ta_frequency = st.selectbox("Frequency",     ["once", "daily", "weekly"])
            if st.form_submit_button("Add task", type="primary"):
                new_task = Task(
                    description=ta_desc,
                    owner_id=owner.owner_id,
                    pet_id=pet_options[ta_pet],
                    priority=ta_priority,
                    scheduled_date=ta_date,
                    duration=timedelta(minutes=int(ta_duration)),
                    frequency=ta_frequency,
                )
                system.add_task(new_task)
                st.success(f"Added **{ta_desc}** for {ta_pet} ({ta_frequency}).")
                st.rerun()

        st.divider()

        # ── Generate recurring tasks ──────────────────────────────────────────
        with st.expander("🔁 Generate recurring tasks — generate_recurring_tasks()", expanded=False):
            recurring_candidates = {
                f"{t.description} ({t.frequency}) — {t.scheduled_date}": t.task_id
                for t in system.tasks.values()
                if t.frequency in ("daily", "weekly")
            }
            if recurring_candidates:
                with st.form("form_recurring"):
                    r_template = st.selectbox("Template task", list(recurring_candidates.keys()))
                    r_end_date = st.date_input("Generate occurrences up to",
                                               value=date.today() + timedelta(days=7))
                    if st.form_submit_button("Generate", type="primary"):
                        template_task = system.tasks[recurring_candidates[r_template]]
                        generated     = system.generate_recurring_tasks(template_task, r_end_date)
                        if generated:
                            st.success(
                                f"Created {len(generated)} recurring task(s) "
                                f"up to {r_end_date}."
                            )
                            st.rerun()
                        else:
                            st.info("No new occurrences to generate for that date range.")
            else:
                st.info("Add a **daily** or **weekly** task first to use this feature.")

        st.divider()

        # ── Task list with filters ────────────────────────────────────────────
        st.subheader("Current Tasks")

        f1, f2 = st.columns(2)
        with f1:
            filter_status = st.selectbox("Filter by status",
                                         ["all", "pending", "completed"])
        with f2:
            filter_pet = st.selectbox("Filter by pet",
                                      ["all pets"] + list(pet_options.keys()))

        status_arg = {"all": None, "pending": False, "completed": True}[filter_status]
        pet_arg    = None if filter_pet == "all pets" else filter_pet

        filtered = system.filter_tasks(pet_name=pet_arg, completed=status_arg)

        if filtered:
            sorter       = Scheduler(date.today(), owner.owner_id, tasks=filtered)
            sorted_tasks = sorter.sort_by_time()
            st.caption(
                f"{len(sorted_tasks)} task(s) — sorted chronologically "
                f"via Scheduler.sort_by_time()"
            )

            for t in sorted_tasks:
                pet_label   = system.pets[t.pet_id].pet_name if t.pet_id in system.pets else "?"
                start_label = t.scheduled_start_time.strftime("%H:%M") \
                              if t.scheduled_start_time else "TBD"
                status_icon = "✅" if t.completion_status else "🔲"

                with st.expander(
                    f"{status_icon} **{t.description}** — {pet_label} | "
                    f"{t.priority} | {t.frequency} | {start_label}",
                    expanded=False,
                ):
                    with st.form(f"form_task_{t.task_id}"):
                        st.caption("Edit task — modify_task()")
                        e1, e2 = st.columns(2)
                        with e1:
                            ed_desc = st.text_input(
                                "Description", value=t.description,
                                key=f"td_{t.task_id}")
                            ed_pet = st.selectbox(
                                "Pet", list(pet_options.keys()),
                                index=list(pet_options.values()).index(t.pet_id)
                                      if t.pet_id in pet_options.values() else 0,
                                key=f"tp_{t.task_id}")
                            ed_priority = st.selectbox(
                                "Priority", ["low", "medium", "high"],
                                index=["low", "medium", "high"].index(t.priority.lower()),
                                key=f"tpr_{t.task_id}")
                        with e2:
                            ed_date = st.date_input(
                                "Scheduled date", value=t.scheduled_date,
                                key=f"tsd_{t.task_id}")
                            ed_dur = st.number_input(
                                "Duration (min)", min_value=1, max_value=480,
                                value=int(t.duration.total_seconds() // 60),
                                key=f"tdur_{t.task_id}")
                            ed_freq = st.selectbox(
                                "Frequency", ["once", "daily", "weekly"],
                                index=["once", "daily", "weekly"].index(t.frequency.lower()),
                                key=f"tf_{t.task_id}")

                        btn1, btn2, btn3 = st.columns(3)
                        with btn1:
                            if st.form_submit_button("💾 Save changes"):
                                t.modify_task(
                                    description=ed_desc,
                                    pet_id=pet_options[ed_pet],
                                    priority=ed_priority,
                                    scheduled_date=ed_date,
                                    duration=timedelta(minutes=int(ed_dur)),
                                    frequency=ed_freq,
                                )
                                st.success("Task updated.")
                                st.rerun()
                        with btn2:
                            if not t.completion_status:
                                if st.form_submit_button("✅ Mark done"):
                                    next_t = system.complete_task(t.task_id)
                                    if next_t:
                                        st.success(
                                            f"Done! Next **{next_t.description}** "
                                            f"auto-scheduled for {next_t.scheduled_date}."
                                        )
                                    else:
                                        st.success("Task marked complete.")
                                    st.rerun()
                        with btn3:
                            if st.form_submit_button("🗑 Remove task"):
                                system.remove_task(t.task_id)
                                st.warning(f"Removed **{t.description}**.")
                                st.rerun()
        else:
            st.info("No tasks match the current filters.")


# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — Schedule
# ═════════════════════════════════════════════════════════════════════════════
with tab_schedule:

    st.subheader("Generate Daily Schedule — create_plan()")

    sc1, sc2 = st.columns([2, 1])
    with sc1:
        plan_date = st.date_input("Plan date", value=date.today())
    with sc2:
        st.metric("Availability window", owner.availability)

    if st.button("Generate schedule", type="primary"):
        tasks_on_date = [t for t in system.tasks.values()
                         if t.scheduled_date == plan_date]
        if not tasks_on_date:
            st.warning(
                f"No tasks scheduled for **{plan_date}**. "
                "Add tasks on the Tasks tab first."
            )
        else:
            plan      = system.create_plan(owner.owner_id, plan_date)
            scheduled = plan.sort_by_time()     # Scheduler.sort_by_time()

            if scheduled:
                st.success(
                    f"Schedule for **{plan_date}** — "
                    f"{len(scheduled)} task(s) fit within {owner.availability}."
                )
                st.dataframe(
                    [
                        {
                            "Task":      t.description,
                            "Pet":       system.pets[t.pet_id].pet_name
                                         if t.pet_id in system.pets else "—",
                            "Start":     t.scheduled_start_time.strftime("%H:%M")
                                         if t.scheduled_start_time else "TBD",
                            "End":       t.scheduled_end_time.strftime("%H:%M")
                                         if t.scheduled_end_time else "TBD",
                            "Duration":  f"{int(t.duration.total_seconds() // 60)} min",
                            "Priority":  t.priority.capitalize(),
                            "Frequency": t.frequency,
                            "Status":    "Done" if t.completion_status else "Pending",
                        }
                        for t in scheduled
                    ],
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.warning("No tasks fit within the availability window.")

            # Scheduling explanations — get_explanations()
            with st.expander("📝 Scheduling explanations — get_explanations()",
                             expanded=False):
                for note in plan.get_explanations():
                    st.write(f"- {note}")

            # Conflict warnings — get_conflict_warnings()
            st.subheader("Conflict Check — get_conflict_warnings()")
            conflict_warnings = plan.get_conflict_warnings()
            if conflict_warnings:
                st.warning(f"⚠️ {len(conflict_warnings)} conflict(s) detected:")
                for msg in conflict_warnings:
                    st.write(f"- {msg}")
            else:
                st.success("✅ No scheduling conflicts detected.")

    st.divider()

    # ── View plan for a specific scheduler ───────────────────────────────────
    st.subheader("Existing Plans — view_plan()")
    plans = list(system.plans.values())
    if plans:
        plan_options = {
            f"{p.date} (ID: {p.scheduler_id[:8]}…)": p.scheduler_id
            for p in plans
        }
        selected_plan_label = st.selectbox("Select a saved plan", list(plan_options.keys()))
        selected_plan = system.plans[plan_options[selected_plan_label]]

        viewed = selected_plan.view_plan()   # Scheduler.view_plan()
        if viewed:
            st.dataframe(
                [
                    {
                        "Task":     t.description,
                        "Start":    t.scheduled_start_time.strftime("%H:%M")
                                    if t.scheduled_start_time else "TBD",
                        "End":      t.scheduled_end_time.strftime("%H:%M")
                                    if t.scheduled_end_time else "TBD",
                        "Priority": t.priority.capitalize(),
                        "Done":     "✅" if t.completion_status else "🔲",
                    }
                    for t in viewed
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("This plan has no tasks.")

        if st.button("🗑 Remove this plan — remove_plan()"):
            system.remove_plan(selected_plan.scheduler_id)
            st.warning("Plan removed.")
            st.rerun()
    else:
        st.info("No saved plans yet. Generate a schedule above.")
