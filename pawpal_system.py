from dataclasses import dataclass, field
from datetime import date, time
from typing import List, Dict, Optional
from uuid import UUID, uuid4


@dataclass
class TimeWindow:
    start: time
    end: time


@dataclass
class Owner:
    owner_id: UUID = field(default_factory=uuid4)
    name: str = ""
    date_of_birth: Optional[date] = None
    age: Optional[int] = None
    availability: List[TimeWindow] = field(default_factory=list)
    preferences: Dict[str, object] = field(default_factory=dict)

    def update_owner(self, data: Dict[str, object]) -> None:
        pass

    def is_available(self, scheduled_date: date, start_time: time, end_time: time) -> bool:
        pass


@dataclass
class Pet:
    pet_id: UUID = field(default_factory=uuid4)
    owner_id: Optional[UUID] = None
    name: str = ""
    date_of_birth: Optional[date] = None
    age: Optional[int] = None
    species: str = ""
    breed: str = ""

    def update_pet(self, data: Dict[str, object]) -> None:
        pass

    def remove_pet(self) -> None:
        pass


@dataclass
class Task:
    task_id: UUID = field(default_factory=uuid4)
    owner_id: Optional[UUID] = None
    pet_id: Optional[UUID] = None
    name: str = ""
    category: str = ""  # e.g., walk, feeding, meds, enrichment, grooming
    priority: int = 0
    duration_minutes: int = 0
    scheduled_date: Optional[date] = None
    scheduled_start: Optional[time] = None
    scheduled_end: Optional[time] = None
    status: str = "pending"
    notes: str = ""

    def set_schedule(self, scheduled_date: date, start: time, end: time) -> None:
        pass

    def update_task(self, data: Dict[str, object]) -> None:
        pass

    def cancel_task(self) -> None:
        pass


@dataclass
class Plan:
    plan_id: UUID = field(default_factory=uuid4)
    owner_id: Optional[UUID] = None
    date: Optional[date] = None
    tasks: List[Task] = field(default_factory=list)
    score: float = 0.0
    explanation: str = ""

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_id: UUID) -> None:
        pass

    def get_tasks(self) -> List[Task]:
        return self.tasks

    def generate_daily_plan(self, tasks: List[Task], owner_availability: List[TimeWindow], preferences: Dict[str, object]) -> "Plan":
        pass

    def explain_plan(self) -> str:
        pass


class Scheduler:
    def build_plan(self, owner: Owner, pets: List[Pet], tasks: List[Task], plan_date: date) -> Plan:
        pass

    def apply_constraints(self, plan: Plan, owner_availability: List[TimeWindow], preferences: Dict[str, object]) -> Plan:
        pass

    def rank_tasks(self, tasks: List[Task]) -> List[Task]:
        pass

    def detect_conflicts(self, plan: Plan) -> List[Task]:
        pass

    def explain_decision(self, plan: Plan) -> str:
        pass

