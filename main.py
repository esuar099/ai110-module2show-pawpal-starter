#!/usr/bin/env python3
"""
Temporary testing ground for PawPal system logic.
"""

from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, PawPalSystem


def main():
    # Create the system
    system = PawPalSystem()

    # Create an Owner
    owner = Owner(
        owner_name="John Doe",
        date_of_birth=date(1990, 5, 15),
        age=34,
        availability="09:00-17:00",
        preferences="walks, feeding"
    )
    system.add_owner(owner)
    print(f"Created owner: {owner.owner_name}")

    # Create two Pets
    pet1 = Pet(
        pet_name="Fluffy",
        date_of_birth=date(2020, 3, 10),
        age=4,
        species="Cat",
        breed="Persian"
    )
    system.add_pet(pet1, owner.owner_id)
    print(f"Added pet: {pet1.pet_name}")

    pet2 = Pet(
        pet_name="Buddy",
        date_of_birth=date(2018, 7, 22),
        age=6,
        species="Dog",
        breed="Golden Retriever"
    )
    system.add_pet(pet2, owner.owner_id)
    print(f"Added pet: {pet2.pet_name}")

    # Create three Tasks with different times
    today = date.today()
    task1 = Task(
        description="Morning walk",
        owner_id=owner.owner_id,
        pet_id=pet2.pet_id,  # Dog
        priority="High",
        scheduled_date=today,
        duration=timedelta(minutes=30),
        frequency="daily"
    )
    system.add_task(task1)
    print(f"Added task: {task1.description}")

    task2 = Task(
        description="Feeding",
        owner_id=owner.owner_id,
        pet_id=pet1.pet_id,  # Cat
        priority="Medium",
        scheduled_date=today,
        duration=timedelta(minutes=15),
        frequency="daily"
    )
    system.add_task(task2)
    print(f"Added task: {task2.description}")

    task3 = Task(
        description="Playtime",
        owner_id=owner.owner_id,
        pet_id=pet2.pet_id,  # Dog
        priority="Low",
        scheduled_date=today,
        duration=timedelta(minutes=45),
        frequency="daily"
    )
    system.add_task(task3)
    print(f"Added task: {task3.description}")

    # Create the daily plan
    plan = system.create_plan(owner.owner_id, today)
    print("\nToday's Schedule:")
    for task in plan.view_plan():
        start = task.scheduled_start_time.strftime("%H:%M") if task.scheduled_start_time else "TBD"
        end = task.scheduled_end_time.strftime("%H:%M") if task.scheduled_end_time else "TBD"
        print(f"  {start} - {end}: {task.description} ({task.priority} priority)")

    print("\nScheduling Explanations:")
    for explanation in plan.get_explanations():
        print(f"  - {explanation}")


if __name__ == "__main__":
    main()