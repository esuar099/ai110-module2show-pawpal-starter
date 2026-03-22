import sys
from pathlib import Path
proj_root = Path(__file__).resolve().parents[1]
if str(proj_root) not in sys.path:
    sys.path.insert(0, str(proj_root))

import pytest
from datetime import date, time, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler, PawPalSystem


def test_task_mark_complete_changes_status():
    task = Task(
        description='Feed',
        owner_id='owner1',
        pet_id='pet1',
        priority='medium',
        scheduled_date=date.today(),
        duration=timedelta(minutes=15)
    )
    assert not task.completion_status

    task.mark_complete()

    assert task.completion_status


def test_pet_add_task_increases_task_count():
    pet = Pet(
        pet_name='Fluffy',
        date_of_birth=date(2020, 1, 1),
        age=4,
        species='Cat',
        breed='Persian'
    )

    initial_count = len(pet.tasks)
    task = Task(
        description='Groom',
        owner_id='owner1',
        pet_id='pet1',
        priority='low',
        scheduled_date=date.today(),
        duration=timedelta(minutes=20)
    )

    pet.add_task(task)

    assert len(pet.tasks) == initial_count + 1
    assert pet.tasks[-1] is task


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_owner():
    return Owner(
        owner_name="Jordan",
        date_of_birth=date(1990, 1, 1),
        age=34,
        availability="09:00-17:00",
        preferences="walks",
    )


def _make_task(description, owner_id, pet_id, priority="medium",
               scheduled_date=None, duration_minutes=30, frequency="once"):
    return Task(
        description=description,
        owner_id=owner_id,
        pet_id=pet_id,
        priority=priority,
        scheduled_date=scheduled_date or date.today(),
        duration=timedelta(minutes=duration_minutes),
        frequency=frequency,
    )


# ── sorting correctness ───────────────────────────────────────────────────────
# Goal: tasks are always returned in chronological order regardless of the
# order they were inserted.

def test_owner_sort_returns_chronological_order():
    """Tasks added latest-first must come back earliest-first."""
    owner = _make_owner()
    pet = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Unknown")
    owner.add_pet(pet)

    # Inserted in REVERSE time order to prove sorting is not insertion-order
    for desc, start in [("Playtime", time(14, 0)),
                        ("Grooming", time(11, 0)),
                        ("Feeding",  time(9, 30)),
                        ("Walk",     time(8, 0))]:
        t = _make_task(desc, owner.owner_id, pet.pet_id)
        t.scheduled_start_time = start
        pet.add_task(t)

    result = owner.get_tasks_sorted_by_time()

    assert [t.description for t in result] == ["Walk", "Feeding", "Grooming", "Playtime"]


def test_scheduler_view_plan_returns_chronological_order():
    """Scheduler.view_plan() must sort tasks by start time, not insertion order."""
    owner = _make_owner()
    today = date.today()

    late  = _make_task("Bath",  owner.owner_id, "pet1", scheduled_date=today)
    mid   = _make_task("Feed",  owner.owner_id, "pet1", scheduled_date=today)
    early = _make_task("Walk",  owner.owner_id, "pet1", scheduled_date=today)

    late.set_schedule(time(15, 0))
    mid.set_schedule(time(10, 0))
    early.set_schedule(time(8, 0))

    # Insert deliberately out of order
    plan = Scheduler(today, owner.owner_id, tasks=[late, mid, early])
    result = plan.view_plan()

    assert [t.description for t in result] == ["Walk", "Feed", "Bath"]


def test_scheduler_sort_by_time_matches_view_plan():
    """sort_by_time() and view_plan() must agree on order."""
    owner = _make_owner()
    today = date.today()

    tasks = []
    for desc, hr in [("C", 12), ("A", 8), ("B", 10)]:
        t = _make_task(desc, owner.owner_id, "pet1", scheduled_date=today)
        t.set_schedule(time(hr, 0))
        tasks.append(t)

    plan = Scheduler(today, owner.owner_id, tasks=tasks)

    assert [t.description for t in plan.sort_by_time()] == \
           [t.description for t in plan.view_plan()]


def test_sort_unscheduled_tasks_come_last():
    """Tasks without a start time must always appear after all timed tasks."""
    owner = _make_owner()
    pet = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Unknown")
    owner.add_pet(pet)

    no_time = _make_task("Groom",  owner.owner_id, pet.pet_id)
    timed   = _make_task("Walk",   owner.owner_id, pet.pet_id)
    timed.scheduled_start_time = time(9, 0)

    pet.add_task(no_time)   # unscheduled added first
    pet.add_task(timed)

    result = owner.get_tasks_sorted_by_time()

    assert result[0].description == "Walk"
    assert result[-1].description == "Groom"


def test_sort_multi_pet_interleaves_by_time():
    """Tasks from different pets must be interleaved by time, not grouped by pet."""
    owner = _make_owner()
    cat = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Unknown")
    dog = Pet(pet_name="Buddy", date_of_birth=date(2018, 1, 1), age=6,
              species="Dog", breed="Unknown")
    owner.add_pet(cat)
    owner.add_pet(dog)

    cat_task = _make_task("Feed cat", owner.owner_id, cat.pet_id)
    dog_task = _make_task("Walk dog", owner.owner_id, dog.pet_id)

    cat_task.scheduled_start_time = time(10, 0)
    dog_task.scheduled_start_time = time(8, 0)   # dog task is earlier

    cat.add_task(cat_task)
    dog.add_task(dog_task)

    result = owner.get_tasks_sorted_by_time()

    assert result[0].description == "Walk dog"
    assert result[1].description == "Feed cat"


# ── filtering by pet / status ─────────────────────────────────────────────────

def test_owner_get_tasks_by_pet_returns_only_matching_pet():
    owner = _make_owner()
    pet1 = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
               species="Cat", breed="Unknown")
    pet2 = Pet(pet_name="Buddy", date_of_birth=date(2018, 1, 1), age=6,
               species="Dog", breed="Labrador")
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    t1 = _make_task("Feed cat", owner.owner_id, pet1.pet_id)
    t2 = _make_task("Walk dog", owner.owner_id, pet2.pet_id)
    pet1.add_task(t1)
    pet2.add_task(t2)

    result = owner.get_tasks_by_pet(pet1.pet_id)

    assert len(result) == 1
    assert result[0].description == "Feed cat"


def test_owner_get_tasks_by_status_filters_completed():
    owner = _make_owner()
    pet = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Unknown")
    owner.add_pet(pet)

    done = _make_task("Feed", owner.owner_id, pet.pet_id)
    done.mark_complete()
    pending = _make_task("Walk", owner.owner_id, pet.pet_id)

    pet.add_task(done)
    pet.add_task(pending)

    assert owner.get_tasks_by_status(completed=True) == [done]
    assert owner.get_tasks_by_status(completed=False) == [pending]


def test_system_get_tasks_by_pet_and_status():
    system = PawPalSystem()
    owner = _make_owner()
    system.add_owner(owner)
    pet = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Unknown")
    system.add_pet(pet, owner.owner_id)

    t1 = _make_task("Feed", owner.owner_id, pet.pet_id)
    t2 = _make_task("Walk", owner.owner_id, pet.pet_id)
    t2.mark_complete()
    system.add_task(t1)
    system.add_task(t2)

    assert system.get_tasks_by_pet(pet.pet_id) == [t1, t2]
    assert system.get_tasks_by_status(completed=False) == [t1]
    assert system.get_tasks_by_status(completed=True) == [t2]


# ── recurrence logic ──────────────────────────────────────────────────────────
# Goal: completing a daily task must produce exactly one new task scheduled
# for the following day (original date + 1).

def test_complete_daily_task_next_date_is_exactly_one_day_later():
    """Core recurrence assertion: next occurrence = original date + 1 day."""
    system = PawPalSystem()
    owner = _make_owner()
    system.add_owner(owner)
    pet = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Unknown")
    system.add_pet(pet, owner.owner_id)

    # Use a fixed date so the assertion is unambiguous
    original_date = date(2025, 6, 15)
    task = _make_task("Feed", owner.owner_id, pet.pet_id,
                      scheduled_date=original_date, frequency="daily")
    system.add_task(task)

    next_task = system.complete_task(task.task_id)

    assert next_task.scheduled_date == date(2025, 6, 16)


def test_complete_daily_task_produces_exactly_one_new_task():
    """Only one follow-up task should be created per completion."""
    system = PawPalSystem()
    owner = _make_owner()
    system.add_owner(owner)
    pet = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Unknown")
    system.add_pet(pet, owner.owner_id)

    task = _make_task("Feed", owner.owner_id, pet.pet_id, frequency="daily")
    system.add_task(task)
    task_count_before = len(system.tasks)

    system.complete_task(task.task_id)

    assert len(system.tasks) == task_count_before + 1


def test_complete_daily_task_month_rollover():
    """Date arithmetic must handle month boundaries (Jan 31 → Feb 1)."""
    system = PawPalSystem()
    owner = _make_owner()
    system.add_owner(owner)
    pet = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Unknown")
    system.add_pet(pet, owner.owner_id)

    task = _make_task("Feed", owner.owner_id, pet.pet_id,
                      scheduled_date=date(2025, 1, 31), frequency="daily")
    system.add_task(task)

    next_task = system.complete_task(task.task_id)

    assert next_task.scheduled_date == date(2025, 2, 1)


def test_complete_daily_task_next_occurrence_is_pending():
    """The auto-created next task must start as incomplete."""
    system = PawPalSystem()
    owner = _make_owner()
    system.add_owner(owner)
    pet = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Unknown")
    system.add_pet(pet, owner.owner_id)

    task = _make_task("Feed", owner.owner_id, pet.pet_id, frequency="daily")
    system.add_task(task)

    next_task = system.complete_task(task.task_id)

    assert next_task.completion_status is False


def test_generate_recurring_tasks_daily_creates_correct_count():
    system = PawPalSystem()
    owner = _make_owner()
    system.add_owner(owner)
    pet = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Unknown")
    system.add_pet(pet, owner.owner_id)

    start = date(2025, 3, 1)
    template = _make_task("Feed", owner.owner_id, pet.pet_id,
                          scheduled_date=start, frequency="daily")
    system.add_task(template)

    generated = system.generate_recurring_tasks(template, start + timedelta(days=4))

    assert len(generated) == 4
    assert [t.scheduled_date for t in generated] == [start + timedelta(days=i) for i in range(1, 5)]


def test_generate_recurring_tasks_weekly_creates_correct_count():
    system = PawPalSystem()
    owner = _make_owner()
    system.add_owner(owner)
    pet = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Unknown")
    system.add_pet(pet, owner.owner_id)

    start = date(2025, 3, 1)
    template = _make_task("Bath", owner.owner_id, pet.pet_id,
                          scheduled_date=start, frequency="weekly")
    system.add_task(template)

    generated = system.generate_recurring_tasks(template, start + timedelta(weeks=3))

    assert len(generated) == 3


def test_generate_recurring_tasks_once_generates_nothing():
    system = PawPalSystem()
    owner = _make_owner()
    system.add_owner(owner)
    pet = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Unknown")
    system.add_pet(pet, owner.owner_id)

    template = _make_task("Vet visit", owner.owner_id, pet.pet_id, frequency="once")
    system.add_task(template)

    generated = system.generate_recurring_tasks(template, date.today() + timedelta(days=7))

    assert generated == []


def test_generate_recurring_tasks_end_before_start_generates_nothing():
    """end_date before scheduled_date must produce an empty list, not an error."""
    system = PawPalSystem()
    owner = _make_owner()
    system.add_owner(owner)
    pet = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Unknown")
    system.add_pet(pet, owner.owner_id)

    start = date(2025, 6, 10)
    template = _make_task("Feed", owner.owner_id, pet.pet_id,
                          scheduled_date=start, frequency="daily")
    system.add_task(template)

    generated = system.generate_recurring_tasks(template, date(2025, 6, 9))

    assert generated == []


def test_generate_recurring_tasks_registers_in_system():
    system = PawPalSystem()
    owner = _make_owner()
    system.add_owner(owner)
    pet = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Unknown")
    system.add_pet(pet, owner.owner_id)

    start = date(2025, 3, 1)
    template = _make_task("Feed", owner.owner_id, pet.pet_id,
                          scheduled_date=start, frequency="daily")
    system.add_task(template)
    generated = system.generate_recurring_tasks(template, start + timedelta(days=2))

    for t in generated:
        assert t.task_id in system.tasks


# ── conflict detection ────────────────────────────────────────────────────────
# Goal: Scheduler must flag tasks at the same or overlapping times without
# crashing, and correctly label same-pet vs cross-pet conflicts.

def test_detect_conflicts_exact_same_start_time_is_flagged():
    """Two tasks starting at the identical time are a conflict (duplicate times)."""
    owner = _make_owner()
    today = date(2025, 6, 15)

    t1 = _make_task("Walk", owner.owner_id, "pet1", scheduled_date=today, duration_minutes=30)
    t2 = _make_task("Feed", owner.owner_id, "pet1", scheduled_date=today, duration_minutes=15)

    t1.set_schedule(time(9, 0))  # 09:00 – 09:30
    t2.set_schedule(time(9, 0))  # 09:00 – 09:15  ← exact duplicate start

    plan = Scheduler(today, owner.owner_id, tasks=[t1, t2])

    assert len(plan.detect_conflicts()) == 1


def test_detect_conflicts_partial_overlap_is_flagged():
    """Tasks that overlap by even one minute must be detected."""
    owner = _make_owner()
    today = date(2025, 6, 15)

    t1 = _make_task("Walk", owner.owner_id, "pet1", scheduled_date=today, duration_minutes=60)
    t2 = _make_task("Feed", owner.owner_id, "pet1", scheduled_date=today, duration_minutes=30)

    t1.set_schedule(time(9, 0))   # 09:00 – 10:00
    t2.set_schedule(time(9, 59))  # 09:59 – 10:29  ← 1-minute overlap with t1

    plan = Scheduler(today, owner.owner_id, tasks=[t1, t2])

    assert len(plan.detect_conflicts()) == 1


def test_detect_conflicts_three_mutually_overlapping_tasks():
    """Three tasks all overlapping each other must produce three conflict pairs."""
    owner = _make_owner()
    today = date(2025, 6, 15)

    t1 = _make_task("Walk",  owner.owner_id, "pet1", scheduled_date=today, duration_minutes=60)
    t2 = _make_task("Feed",  owner.owner_id, "pet1", scheduled_date=today, duration_minutes=60)
    t3 = _make_task("Groom", owner.owner_id, "pet1", scheduled_date=today, duration_minutes=60)

    t1.set_schedule(time(9, 0))   # 09:00 – 10:00
    t2.set_schedule(time(9, 15))  # 09:15 – 10:15  overlaps t1
    t3.set_schedule(time(9, 30))  # 09:30 – 10:30  overlaps t1 and t2

    plan = Scheduler(today, owner.owner_id, tasks=[t1, t2, t3])

    assert len(plan.detect_conflicts()) == 3


def test_detect_conflicts_no_conflict_for_sequential_tasks():
    """Tasks that share only an endpoint (end == next start) must NOT conflict."""
    owner = _make_owner()
    today = date(2025, 6, 15)

    t1 = _make_task("Walk", owner.owner_id, "pet1", scheduled_date=today, duration_minutes=30)
    t2 = _make_task("Feed", owner.owner_id, "pet1", scheduled_date=today, duration_minutes=30)

    t1.set_schedule(time(9, 0))   # 09:00 – 09:30
    t2.set_schedule(time(9, 30))  # 09:30 – 10:00  touching, not overlapping

    plan = Scheduler(today, owner.owner_id, tasks=[t1, t2])

    assert plan.detect_conflicts() == []


def test_detect_conflicts_ignores_unscheduled_tasks():
    """Tasks without a start time must be skipped, not cause errors."""
    owner = _make_owner()
    today = date(2025, 6, 15)

    t1 = _make_task("Walk", owner.owner_id, "pet1", scheduled_date=today)
    t2 = _make_task("Feed", owner.owner_id, "pet1", scheduled_date=today)
    # no set_schedule() called — both have scheduled_start_time = None

    plan = Scheduler(today, owner.owner_id, tasks=[t1, t2])

    assert plan.detect_conflicts() == []


def test_get_conflict_warnings_same_pet_label():
    """get_conflict_warnings() must label same-pet conflicts correctly."""
    owner = _make_owner()
    today = date(2025, 6, 15)

    t1 = _make_task("Walk", owner.owner_id, "pet1", scheduled_date=today, duration_minutes=30)
    t2 = _make_task("Feed", owner.owner_id, "pet1", scheduled_date=today, duration_minutes=30)

    t1.set_schedule(time(9, 0))
    t2.set_schedule(time(9, 0))  # duplicate start → same-pet conflict

    plan = Scheduler(today, owner.owner_id, tasks=[t1, t2])
    warnings = plan.get_conflict_warnings()

    assert len(warnings) == 1
    assert "same-pet" in warnings[0]


def test_get_conflict_warnings_cross_pet_label():
    """get_conflict_warnings() must label cross-pet conflicts correctly."""
    owner = _make_owner()
    today = date(2025, 6, 15)

    t1 = _make_task("Walk cat", owner.owner_id, "pet1", scheduled_date=today, duration_minutes=30)
    t2 = _make_task("Walk dog", owner.owner_id, "pet2", scheduled_date=today, duration_minutes=30)

    t1.set_schedule(time(9, 0))
    t2.set_schedule(time(9, 0))  # duplicate start → cross-pet conflict

    plan = Scheduler(today, owner.owner_id, tasks=[t1, t2])
    warnings = plan.get_conflict_warnings()

    assert len(warnings) == 1
    assert "cross-pet" in warnings[0]


def test_get_conflict_warnings_returns_empty_for_clean_schedule():
    """No warnings must be returned when the schedule has zero conflicts."""
    owner = _make_owner()
    today = date(2025, 6, 15)

    t1 = _make_task("Walk", owner.owner_id, "pet1", scheduled_date=today, duration_minutes=30)
    t2 = _make_task("Feed", owner.owner_id, "pet1", scheduled_date=today, duration_minutes=30)

    t1.set_schedule(time(9, 0))
    t2.set_schedule(time(9, 30))  # sequential, no overlap

    plan = Scheduler(today, owner.owner_id, tasks=[t1, t2])

    assert plan.get_conflict_warnings() == []


# ── filter_tasks ──────────────────────────────────────────────────────────────

def _make_system_with_two_pets():
    """Return (system, owner, pet_cat, pet_dog) pre-populated with tasks."""
    system = PawPalSystem()
    owner = _make_owner()
    system.add_owner(owner)

    cat = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Persian")
    dog = Pet(pet_name="Buddy", date_of_birth=date(2018, 1, 1), age=6,
              species="Dog", breed="Labrador")
    system.add_pet(cat, owner.owner_id)
    system.add_pet(dog, owner.owner_id)

    t_cat_done  = _make_task("Feed cat",  owner.owner_id, cat.pet_id)
    t_cat_pend  = _make_task("Groom cat", owner.owner_id, cat.pet_id)
    t_dog_done  = _make_task("Walk dog",  owner.owner_id, dog.pet_id)
    t_dog_pend  = _make_task("Bath dog",  owner.owner_id, dog.pet_id)

    t_cat_done.mark_complete()
    t_dog_done.mark_complete()

    for t in [t_cat_done, t_cat_pend, t_dog_done, t_dog_pend]:
        system.add_task(t)

    return system, owner, cat, dog


def test_filter_tasks_by_pet_name_only():
    system, _, cat, _ = _make_system_with_two_pets()

    result = system.filter_tasks(pet_name="Mochi")

    assert len(result) == 2
    assert all(t.pet_id == cat.pet_id for t in result)


def test_filter_tasks_by_pet_name_case_insensitive():
    system, _, cat, _ = _make_system_with_two_pets()

    result = system.filter_tasks(pet_name="mochi")

    assert len(result) == 2
    assert all(t.pet_id == cat.pet_id for t in result)


def test_filter_tasks_by_status_pending_only():
    system, _, _, _ = _make_system_with_two_pets()

    result = system.filter_tasks(completed=False)

    assert len(result) == 2
    assert all(not t.completion_status for t in result)


def test_filter_tasks_by_status_completed_only():
    system, _, _, _ = _make_system_with_two_pets()

    result = system.filter_tasks(completed=True)

    assert len(result) == 2
    assert all(t.completion_status for t in result)


def test_filter_tasks_by_pet_name_and_status_combined():
    system, _, _, _ = _make_system_with_two_pets()

    result = system.filter_tasks(pet_name="Mochi", completed=False)

    assert len(result) == 1
    assert result[0].description == "Groom cat"


def test_filter_tasks_no_filters_returns_all():
    system, _, _, _ = _make_system_with_two_pets()

    result = system.filter_tasks()

    assert len(result) == 4


def test_filter_tasks_unknown_pet_name_returns_empty():
    system, _, _, _ = _make_system_with_two_pets()

    result = system.filter_tasks(pet_name="Ghost")

    assert result == []


# ── complete_task / auto-recurrence ───────────────────────────────────────────

def _make_system_with_task(frequency="daily"):
    system = PawPalSystem()
    owner = _make_owner()
    system.add_owner(owner)
    pet = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Unknown")
    system.add_pet(pet, owner.owner_id)
    task = _make_task("Feed", owner.owner_id, pet.pet_id,
                      scheduled_date=date.today(), frequency=frequency)
    system.add_task(task)
    return system, task


def test_complete_task_marks_task_done():
    system, task = _make_system_with_task("daily")

    system.complete_task(task.task_id)

    assert task.completion_status is True


def test_complete_task_daily_creates_next_day_occurrence():
    system, task = _make_system_with_task("daily")

    next_task = system.complete_task(task.task_id)

    assert next_task is not None
    assert next_task.scheduled_date == task.scheduled_date + timedelta(days=1)


def test_complete_task_weekly_creates_next_week_occurrence():
    system, task = _make_system_with_task("weekly")

    next_task = system.complete_task(task.task_id)

    assert next_task is not None
    assert next_task.scheduled_date == task.scheduled_date + timedelta(weeks=1)


def test_complete_task_once_returns_none():
    system, task = _make_system_with_task("once")

    next_task = system.complete_task(task.task_id)

    assert next_task is None


def test_complete_task_next_occurrence_inherits_attributes():
    system, task = _make_system_with_task("daily")

    next_task = system.complete_task(task.task_id)

    assert next_task.description == task.description
    assert next_task.priority == task.priority
    assert next_task.duration == task.duration
    assert next_task.frequency == task.frequency


def test_complete_task_next_occurrence_registered_in_system():
    system, task = _make_system_with_task("daily")

    next_task = system.complete_task(task.task_id)

    assert next_task.task_id in system.tasks


def test_complete_task_next_occurrence_is_not_complete():
    system, task = _make_system_with_task("daily")

    next_task = system.complete_task(task.task_id)

    assert next_task.completion_status is False


def test_complete_task_unknown_id_returns_none():
    system, _ = _make_system_with_task("daily")

    result = system.complete_task("nonexistent-id")

    assert result is None
