# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling
### Core data
- Tied to a specific date and owner_id
- Holds a list of Task objects and a parallel list of explanations (reasoning for each scheduling decision)

### Viewing & Sorting
- view_plan() — returns tasks sorted chronologically; unscheduled tasks appended at the end
- sort_by_time(tasks?) — same sort logic, optionally on an external task list

### Plan Management
- add_task(task, reason) — validates no conflict before adding; logs reason or exclusion explanation
- remove_task(task_id) — removes task and its explanation entry
- modify_plan(tasks) — replaces all tasks if the new list is conflict-free
- remove_plan() — clears all tasks and explanations

### Conflict Detection
- validate_schedule(new_task?) — returns bool; blocks additions that would create overlaps
- detect_conflicts() — returns all overlapping task pairs using interval-overlap math (O(n²))
- get_conflict_warnings() — human-readable strings classifying conflicts as same-pet or cross-pet

### Explanations
- get_explanations() — returns the log of why each task was included or excluded

### Auto-generated via PawPalSystem.create_plan()
- Greedy priority algorithm: tasks sorted by effective priority (base + preference boost)
- Slots tasks sequentially within the owner's availability window (HH:MM-HH:MM)
- Excludes tasks that don't fit the remaining window, with an explanation recorded

## Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest tests/test_pawpal.py -v
```

The tests cover four areas of the scheduling system:

**Sorting correctness** — verifies that tasks are always returned in chronological order regardless of insertion order, including tasks from multiple pets interleaved by time and unscheduled tasks appended last.

**Recurrence logic** — confirms that completing a `daily` task creates exactly one new task for the following day, that the next occurrence starts as pending, and that month/year boundary rollovers (e.g. Jan 31 → Feb 1) are handled correctly. Also verifies that `once` tasks produce no follow-up.

**Conflict detection** — verifies that the `Scheduler` flags overlapping tasks including exact duplicate start times, partial overlaps, and three-way overlaps, while correctly leaving sequential tasks (touching endpoints) clear. Checks that warning messages are labelled `same-pet` or `cross-pet` as appropriate.

**Filtering** — verifies that tasks can be filtered by pet name (case-insensitive), completion status, or both combined, and that the system returns an empty list for unknown pet names rather than raising an error.

Confidence Level (1-5 stars): 5 stars
