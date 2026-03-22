import sys
from pathlib import Path
proj_root = Path(__file__).resolve().parents[1]
if str(proj_root) not in sys.path:
    sys.path.insert(0, str(proj_root))

import pytest
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task


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
