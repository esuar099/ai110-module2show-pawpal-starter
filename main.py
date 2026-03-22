#!/usr/bin/env python3
"""
Temporary testing ground for PawPal system logic.
"""

from datetime import date, time, timedelta
from pawpal_system import Owner, Pet, Task, PawPalSystem, Scheduler


def print_section(title: str) -> None:
    print(f"\n{'─' * 45}")
    print(f"  {title}")
    print(f"{'─' * 45}")


def main():
    system = PawPalSystem()

    owner = Owner(
        owner_name="John Doe",
        date_of_birth=date(1990, 5, 15),
        age=34,
        availability="09:00-17:00",
        preferences="walks, feeding"
    )
    system.add_owner(owner)

    pet1 = Pet(pet_name="Fluffy", date_of_birth=date(2020, 3, 10),
               age=4, species="Cat", breed="Persian")
    pet2 = Pet(pet_name="Buddy", date_of_birth=date(2018, 7, 22),
               age=6, species="Dog", breed="Golden Retriever")
    system.add_pet(pet1, owner.owner_id)
    system.add_pet(pet2, owner.owner_id)

    today = date.today()

    # ── Tasks added OUT OF ORDER (latest time first) ──────────────────────────
    # Playtime  → 14:00  (added first but happens last)
    # Grooming  → 11:30  (added second)
    # Feeding   → 10:00  (added third)
    # Morning walk → 09:00  (added last but happens first)

    task_playtime = Task(
        description="Playtime",
        owner_id=owner.owner_id,
        pet_id=pet2.pet_id,
        priority="Low",
        scheduled_date=today,
        duration=timedelta(minutes=45),
        frequency="once",
    )
    task_playtime.set_schedule(time(14, 0))
    system.add_task(task_playtime)

    task_groom = Task(
        description="Grooming",
        owner_id=owner.owner_id,
        pet_id=pet1.pet_id,
        priority="Medium",
        scheduled_date=today,
        duration=timedelta(minutes=20),
        frequency="weekly",
    )
    task_groom.set_schedule(time(11, 30))
    system.add_task(task_groom)

    task_feed = Task(
        description="Feeding",
        owner_id=owner.owner_id,
        pet_id=pet1.pet_id,
        priority="Medium",
        scheduled_date=today,
        duration=timedelta(minutes=15),
        frequency="daily",
    )
    task_feed.set_schedule(time(10, 0))
    system.add_task(task_feed)

    task_walk = Task(
        description="Morning walk",
        owner_id=owner.owner_id,
        pet_id=pet2.pet_id,
        priority="High",
        scheduled_date=today,
        duration=timedelta(minutes=30),
        frequency="daily",
    )
    task_walk.set_schedule(time(9, 0))
    system.add_task(task_walk)

    # ── 1. Raw insertion order (unsorted) ─────────────────────────────────────
    print_section("Tasks — insertion order (unsorted)")
    for t in system.tasks.values():
        start = t.scheduled_start_time.strftime("%H:%M") if t.scheduled_start_time else "TBD"
        print(f"  {start}  {t.description:<20} ({t.priority})")

    # ── 2. Sorted by scheduled start time ────────────────────────────────────
    print_section("Tasks — sorted by start time (Scheduler.sort_by_time)")
    plan = system.create_plan(owner.owner_id, today)
    for t in plan.sort_by_time():
        start = t.scheduled_start_time.strftime("%H:%M") if t.scheduled_start_time else "TBD"
        end   = t.scheduled_end_time.strftime("%H:%M")   if t.scheduled_end_time   else "TBD"
        print(f"  {start} – {end}  {t.description:<20} ({t.priority})")

    # ── Mark some tasks complete before filtering ─────────────────────────────
    task_walk.mark_complete()
    task_feed.mark_complete()

    # ── 3. Filter by pet name ─────────────────────────────────────────────────
    print_section("filter_tasks(pet_name='Buddy')")
    for t in system.filter_tasks(pet_name="Buddy"):
        status = "✓ Done" if t.completion_status else "○ Pending"
        print(f"  {status}  {t.description}")

    # ── 4. Filter by completion status ───────────────────────────────────────
    print_section("filter_tasks(completed=False)  — pending only")
    for t in system.filter_tasks(completed=False):
        start = t.scheduled_start_time.strftime("%H:%M") if t.scheduled_start_time else "TBD"
        print(f"  {start}  {t.description:<20} pet={t.pet_id[:8]}…")

    # ── 5. Filter by pet name + status combined ───────────────────────────────
    print_section("filter_tasks(pet_name='Fluffy', completed=False)")
    results = system.filter_tasks(pet_name="Fluffy", completed=False)
    if results:
        for t in results:
            print(f"  {t.description}")
    else:
        print("  (no matching tasks)")

    # ── 6. Conflict detection ─────────────────────────────────────────────────
    # Build a Scheduler manually with two deliberately overlapping tasks.
    #
    # Same-pet conflict: both tasks assigned to Buddy (pet2), 09:00–09:30 overlap
    # Cross-pet conflict: Buddy task and Fluffy task overlap at 10:00

    print_section("Conflict detection — get_conflict_warnings()")

    conflict_task1 = Task(
        description="Morning walk",
        owner_id=owner.owner_id,
        pet_id=pet2.pet_id,          # Buddy
        priority="High",
        scheduled_date=today,
        duration=timedelta(minutes=30),
        frequency="daily",
    )
    conflict_task1.set_schedule(time(9, 0))   # 09:00 – 09:30

    conflict_task2 = Task(
        description="Fetch training",
        owner_id=owner.owner_id,
        pet_id=pet2.pet_id,          # Buddy — same pet as task1
        priority="Medium",
        scheduled_date=today,
        duration=timedelta(minutes=20),
        frequency="once",
    )
    conflict_task2.set_schedule(time(9, 15))  # 09:15 – 09:35  ← overlaps task1 (same pet)

    conflict_task3 = Task(
        description="Feeding",
        owner_id=owner.owner_id,
        pet_id=pet1.pet_id,          # Fluffy — different pet from task1
        priority="Medium",
        scheduled_date=today,
        duration=timedelta(minutes=15),
        frequency="daily",
    )
    conflict_task3.set_schedule(time(9, 20))  # 09:20 – 09:35  ← overlaps task1 (cross-pet)

    conflict_plan = Scheduler(today, owner.owner_id,
                              tasks=[conflict_task1, conflict_task2, conflict_task3])

    warnings = conflict_plan.get_conflict_warnings()
    if warnings:
        for w in warnings:
            print(f"  {w}")
    else:
        print("  No conflicts detected.")

    print()