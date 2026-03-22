# logic layer where all your backend classes live

from __future__ import annotations
from datetime import date, datetime, time, timedelta
from typing import List, Optional, Dict, Tuple
import uuid


PRIORITY_LEVELS = {'low': 1, 'medium': 2, 'high': 3}


class Owner:
    def __init__(
        self,
        owner_name: str,
        date_of_birth: date,
        age: int,
        availability: str,
        preferences: str,
        owner_id: Optional[str] = None,
    ):
        self.owner_id = owner_id or str(uuid.uuid4())
        self.owner_name = owner_name
        self.date_of_birth = date_of_birth
        self.age = age
        self.availability = availability
        self.preferences = preferences
        self.pets: List[Pet] = []
        self.tasks: List[Task] = []
        self.plans: List[Scheduler] = []

    def modify_owner(
        self,
        owner_name: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        age: Optional[int] = None,
        availability: Optional[str] = None,
        preferences: Optional[str] = None,
    ) -> None:
        """Update owner profile information."""
        if owner_name is not None:
            self.owner_name = owner_name
        if date_of_birth is not None:
            self.date_of_birth = date_of_birth
        if age is not None:
            self.age = age
        if availability is not None:
            self.availability = availability
        if preferences is not None:
            self.preferences = preferences

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        if pet not in self.pets:
            self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        """Remove a pet from this owner."""
        self.pets = [p for p in self.pets if p.pet_id != pet_id]

    def get_availability_window(self) -> Tuple[time, time]:
        """Parse availability string to start and end time."""
        try:
            start_str, end_str = self.availability.split('-')
            start_time = datetime.strptime(start_str.strip(), '%H:%M').time()
            end_time = datetime.strptime(end_str.strip(), '%H:%M').time()
            return start_time, end_time
        except ValueError:
            # Default to 9-5 if parsing fails
            return time(9, 0), time(17, 0)

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks from all pets managed by this owner."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


class Pet:
    def __init__(
        self,
        pet_name: str,
        date_of_birth: date,
        age: int,
        species: str,
        breed: str,
        pet_id: Optional[str] = None,
    ):
        self.pet_id = pet_id or str(uuid.uuid4())
        self.pet_name = pet_name
        self.date_of_birth = date_of_birth
        self.age = age
        self.species = species
        self.breed = breed
        self.tasks: List[Task] = []

    def modify_pet(
        self,
        pet_name: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        age: Optional[int] = None,
        species: Optional[str] = None,
        breed: Optional[str] = None,
    ) -> None:
        """Modify pet attributes."""
        if pet_name is not None:
            self.pet_name = pet_name
        if date_of_birth is not None:
            self.date_of_birth = date_of_birth
        if age is not None:
            self.age = age
        if species is not None:
            self.species = species
        if breed is not None:
            self.breed = breed

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        if task not in self.tasks:
            self.tasks.append(task)


class Task:
    def __init__(
        self,
        description: str,
        owner_id: str,
        pet_id: str,
        priority: str,
        scheduled_date: date,
        duration: timedelta,
        frequency: str = 'Daily',  # e.g., 'Daily', 'Weekly'
        completion_status: bool = False,
        task_id: Optional[str] = None,
    ):
        self.task_id = task_id or str(uuid.uuid4())
        self.description = description  # Renamed from task_name
        self.owner_id = owner_id
        self.pet_id = pet_id
        self.priority = priority  # 'Low', 'Medium', 'High'
        self.scheduled_date = scheduled_date
        self.duration = duration
        self.frequency = frequency
        self.completion_status = completion_status
        # Scheduled times will be set by the scheduler
        self.scheduled_start_time: Optional[time] = None
        self.scheduled_end_time: Optional[time] = None

    def get_effective_priority(self, owner_preferences: str) -> int:
        """Get priority level, boosted if task matches preferences."""
        base_priority = PRIORITY_LEVELS.get(self.priority.lower(), 1)
        if self.description.lower() in owner_preferences.lower():
            base_priority += 1  # Boost for preferred tasks
        return base_priority

    def set_schedule(self, start_time: time) -> None:
        """Set start and end times based on duration."""
        self.scheduled_start_time = start_time
        self.scheduled_end_time = (datetime.combine(self.scheduled_date, start_time) + self.duration).time()

    def modify_task(
        self,
        description: Optional[str] = None,
        owner_id: Optional[str] = None,
        pet_id: Optional[str] = None,
        priority: Optional[str] = None,
        scheduled_date: Optional[date] = None,
        duration: Optional[timedelta] = None,
        frequency: Optional[str] = None,
        completion_status: Optional[bool] = None,
    ) -> None:
        """Modify task details."""
        if description is not None:
            self.description = description
        if owner_id is not None:
            self.owner_id = owner_id
        if pet_id is not None:
            self.pet_id = pet_id
        if priority is not None:
            self.priority = priority
        if scheduled_date is not None:
            self.scheduled_date = scheduled_date
        if duration is not None:
            self.duration = duration
        if frequency is not None:
            self.frequency = frequency
        if completion_status is not None:
            self.completion_status = completion_status

    def mark_complete(self) -> None:
        """Mark task as completed."""
        self.completion_status = True

    def validate_times(self) -> bool:
        """Validate that start time + duration matches end time."""
        expected_end = (
            datetime.combine(self.scheduled_date, self.scheduled_start_time) + self.duration
        ).time()
        return expected_end == self.scheduled_end_time


class Scheduler:
    def __init__(
        self,
        date: date,
        owner_id: str,
        tasks: Optional[List[Task]] = None,
        scheduler_id: Optional[str] = None,
    ):
        self.scheduler_id = scheduler_id or str(uuid.uuid4())
        self.date = date
        self.owner_id = owner_id
        self.tasks = tasks or []
        self.explanations: List[str] = []  # Reasons for scheduling decisions

    def view_plan(self) -> List[Task]:
        """Return all tasks in the plan."""
        return self.tasks

    def get_explanations(self) -> List[str]:
        """Return explanations for the plan."""
        return self.explanations

    def add_task(self, task: Task, reason: str) -> None:
        """Add a task to the plan with reason."""
        if self.validate_schedule(task):
            self.tasks.append(task)
            self.explanations.append(f"Included '{task.description}': {reason}")
        else:
            self.explanations.append(f"Excluded '{task.description}': Time conflict")

    def remove_task(self, task_id: str) -> None:
        """Remove a task from the plan."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]
        self.explanations = [e for e in self.explanations if task_id not in e]

    def modify_plan(self, tasks: List[Task]) -> None:
        """Replace plan tasks with a new list, validating schedule."""
        if all(self.validate_schedule(t) for t in tasks):
            self.tasks = tasks
            self.explanations = [f"Included '{t.description}': Updated plan" for t in tasks]

    def remove_plan(self) -> None:
        """Clear plan tasks."""
        self.tasks = []
        self.explanations = []

    def validate_schedule(self, new_task: Optional[Task] = None) -> bool:
        """Check for time conflicts in the plan."""
        tasks_to_check = self.tasks + ([new_task] if new_task else [])
        for i, task1 in enumerate(tasks_to_check):
            if not task1.scheduled_start_time or not task1.scheduled_end_time:
                continue  # Skip unscheduled tasks
            for task2 in tasks_to_check[i + 1 :]:
                if not task2.scheduled_start_time or not task2.scheduled_end_time:
                    continue
                if task1.scheduled_date == task2.scheduled_date:
                    start1 = datetime.combine(task1.scheduled_date, task1.scheduled_start_time)
                    end1 = datetime.combine(task1.scheduled_date, task1.scheduled_end_time)
                    start2 = datetime.combine(task2.scheduled_date, task2.scheduled_start_time)
                    end2 = datetime.combine(task2.scheduled_date, task2.scheduled_end_time)
                    if (start1 < end2 and end1 > start2):
                        return False
        return True


class PawPalSystem:
    def __init__(self):
        self.owners: Dict[str, Owner] = {}
        self.pets: Dict[str, Pet] = {}
        self.tasks: Dict[str, Task] = {}
        self.plans: Dict[str, Scheduler] = {}

    def add_owner(self, owner: Owner) -> None:
        """Add an owner to the system."""
        self.owners[owner.owner_id] = owner

    def add_pet(self, pet: Pet, owner_id: str) -> None:
        """Add a pet to the system and link to owner."""
        self.pets[pet.pet_id] = pet
        if owner_id in self.owners:
            self.owners[owner_id].add_pet(pet)

    def add_task(self, task: Task) -> None:
        """Add a task to the system and link to owner and pet."""
        self.tasks[task.task_id] = task
        if task.owner_id in self.owners:
            self.owners[task.owner_id].tasks.append(task)
        if task.pet_id in self.pets:
            self.pets[task.pet_id].tasks.append(task)

    def add_plan(self, plan: Scheduler) -> None:
        """Add a plan to the system and link to owner."""
        self.plans[plan.scheduler_id] = plan
        if plan.owner_id in self.owners:
            self.owners[plan.owner_id].plans.append(plan)

    def remove_owner(self, owner_id: str) -> None:
        """Remove an owner and all associated pets, tasks, plans."""
        if owner_id in self.owners:
            owner = self.owners[owner_id]
            for pet in owner.pets:
                self.remove_pet(pet.pet_id)
            for task in owner.tasks:
                self.remove_task(task.task_id)
            for plan in owner.plans:
                self.remove_plan(plan.scheduler_id)
            del self.owners[owner_id]

    def remove_pet(self, pet_id: str) -> None:
        """Remove a pet and associated tasks."""
        if pet_id in self.pets:
            pet = self.pets[pet_id]
            for task in pet.tasks:
                self.remove_task(task.task_id)
            # Remove from owner's pets
            for owner in self.owners.values():
                owner.remove_pet(pet_id)
            del self.pets[pet_id]

    def remove_task(self, task_id: str) -> None:
        """Remove a task from system and links."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            # Remove from owner's tasks
            if task.owner_id in self.owners:
                self.owners[task.owner_id].tasks = [t for t in self.owners[task.owner_id].tasks if t.task_id != task_id]
            # Remove from pet's tasks
            if task.pet_id in self.pets:
                self.pets[task.pet_id].tasks = [t for t in self.pets[task.pet_id].tasks if t.task_id != task_id]
            # Remove from plans
            for plan in self.plans.values():
                plan.remove_task(task_id)
            del self.tasks[task_id]

    def remove_plan(self, plan_id: str) -> None:
        """Remove a plan from system and links."""
        if plan_id in self.plans:
            plan = self.plans[plan_id]
            # Remove from owner's plans
            if plan.owner_id in self.owners:
                self.owners[plan.owner_id].plans = [p for p in self.owners[plan.owner_id].plans if p.scheduler_id != plan_id]
            del self.plans[plan_id]

    def create_plan(self, owner_id: str, plan_date: date) -> Scheduler:
        """Create a daily plan for the owner by scheduling tasks without overlaps."""
        if owner_id not in self.owners:
            raise ValueError("Owner not found")
        owner = self.owners[owner_id]
        avail_start, avail_end = owner.get_availability_window()
        
        # Get tasks for the date
        relevant_tasks = [t for t in owner.get_all_tasks() if t.scheduled_date == plan_date]
        
        # Sort by effective priority (considering preferences)
        relevant_tasks.sort(key=lambda t: t.get_effective_priority(owner.preferences), reverse=True)
        
        scheduler = Scheduler(plan_date, owner_id)
        current_time = datetime.combine(plan_date, avail_start)
        avail_end_dt = datetime.combine(plan_date, avail_end)
        
        for task in relevant_tasks:
            task_duration = task.duration
            if current_time + task_duration <= avail_end_dt:
                task.set_schedule(current_time.time())
                reason = f"{task.priority} priority"
                if task.description.lower() in owner.preferences.lower():
                    reason += " and matches owner preferences"
                reason += f", scheduled within availability ({avail_start}-{avail_end})"
                scheduler.add_task(task, reason)
                current_time += task_duration
            else:
                scheduler.explanations.append(f"Excluded '{task.description}': No available time slot within {avail_start}-{avail_end}")
        
        self.add_plan(scheduler)
        return scheduler

