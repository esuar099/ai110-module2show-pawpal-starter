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


# ── sorting by time ───────────────────────────────────────────────────────────

def test_owner_get_tasks_sorted_by_time_orders_correctly():
    owner = _make_owner()
    pet = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Unknown")
    owner.add_pet(pet)

    t1 = _make_task("Walk", owner.owner_id, pet.pet_id)
    t2 = _make_task("Feed", owner.owner_id, pet.pet_id)
    t3 = _make_task("Play", owner.owner_id, pet.pet_id)

    t1.scheduled_start_time = time(10, 0)
    t2.scheduled_start_time = time(8, 0)
    t3.scheduled_start_time = time(9, 0)

    pet.add_task(t1)
    pet.add_task(t2)
    pet.add_task(t3)

    sorted_tasks = owner.get_tasks_sorted_by_time()

    assert [t.description for t in sorted_tasks] == ["Feed", "Play", "Walk"]


def test_owner_get_tasks_sorted_by_time_unscheduled_come_last():
    owner = _make_owner()
    pet = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Unknown")
    owner.add_pet(pet)

    scheduled = _make_task("Walk", owner.owner_id, pet.pet_id)
    scheduled.scheduled_start_time = time(9, 0)
    unscheduled = _make_task("Groom", owner.owner_id, pet.pet_id)

    pet.add_task(scheduled)
    pet.add_task(unscheduled)

    result = owner.get_tasks_sorted_by_time()

    assert result[0].description == "Walk"
    assert result[-1].description == "Groom"


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


# ── recurring tasks ───────────────────────────────────────────────────────────

def test_generate_recurring_tasks_daily_creates_correct_count():
    system = PawPalSystem()
    owner = _make_owner()
    system.add_owner(owner)
    pet = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Unknown")
    system.add_pet(pet, owner.owner_id)

    start = date.today()
    template = _make_task("Feed", owner.owner_id, pet.pet_id,
                          scheduled_date=start, frequency="daily")
    system.add_task(template)

    end = start + timedelta(days=4)
    generated = system.generate_recurring_tasks(template, end)

    assert len(generated) == 4
    assert all(t.description == "Feed" for t in generated)
    assert [t.scheduled_date for t in generated] == [start + timedelta(days=i) for i in range(1, 5)]


def test_generate_recurring_tasks_weekly_creates_correct_count():
    system = PawPalSystem()
    owner = _make_owner()
    system.add_owner(owner)
    pet = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Unknown")
    system.add_pet(pet, owner.owner_id)

    start = date.today()
    template = _make_task("Bath", owner.owner_id, pet.pet_id,
                          scheduled_date=start, frequency="weekly")
    system.add_task(template)

    end = start + timedelta(weeks=3)
    generated = system.generate_recurring_tasks(template, end)

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


def test_generate_recurring_tasks_registers_in_system():
    system = PawPalSystem()
    owner = _make_owner()
    system.add_owner(owner)
    pet = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Unknown")
    system.add_pet(pet, owner.owner_id)

    start = date.today()
    template = _make_task("Feed", owner.owner_id, pet.pet_id,
                          scheduled_date=start, frequency="daily")
    system.add_task(template)
    generated = system.generate_recurring_tasks(template, start + timedelta(days=2))

    for t in generated:
        assert t.task_id in system.tasks


# ── conflict detection ────────────────────────────────────────────────────────

def test_detect_conflicts_finds_overlapping_tasks():
    system = PawPalSystem()
    owner = _make_owner()
    system.add_owner(owner)
    pet = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Unknown")
    system.add_pet(pet, owner.owner_id)

    today = date.today()
    t1 = _make_task("Walk", owner.owner_id, pet.pet_id, scheduled_date=today, duration_minutes=60)
    t2 = _make_task("Feed", owner.owner_id, pet.pet_id, scheduled_date=today, duration_minutes=30)

    t1.set_schedule(time(9, 0))   # 09:00 – 10:00
    t2.set_schedule(time(9, 30))  # 09:30 – 10:00  → overlaps t1

    plan = Scheduler(today, owner.owner_id, tasks=[t1, t2])
    conflicts = plan.detect_conflicts()

    assert len(conflicts) == 1
    assert set([t1, t2]) == set(conflicts[0])


def test_detect_conflicts_no_conflict_for_sequential_tasks():
    system = PawPalSystem()
    owner = _make_owner()
    system.add_owner(owner)
    pet = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Unknown")
    system.add_pet(pet, owner.owner_id)

    today = date.today()
    t1 = _make_task("Walk", owner.owner_id, pet.pet_id, scheduled_date=today, duration_minutes=30)
    t2 = _make_task("Feed", owner.owner_id, pet.pet_id, scheduled_date=today, duration_minutes=30)

    t1.set_schedule(time(9, 0))   # 09:00 – 09:30
    t2.set_schedule(time(9, 30))  # 09:30 – 10:00  → no overlap

    plan = Scheduler(today, owner.owner_id, tasks=[t1, t2])

    assert plan.detect_conflicts() == []


def test_detect_conflicts_ignores_unscheduled_tasks():
    today = date.today()
    owner = _make_owner()
    pet = Pet(pet_name="Mochi", date_of_birth=date(2020, 1, 1), age=4,
              species="Cat", breed="Unknown")

    t1 = _make_task("Walk", owner.owner_id, pet.pet_id, scheduled_date=today)
    t2 = _make_task("Feed", owner.owner_id, pet.pet_id, scheduled_date=today)
    # neither task has scheduled_start_time set

    plan = Scheduler(today, owner.owner_id, tasks=[t1, t2])

    assert plan.detect_conflicts() == []


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
