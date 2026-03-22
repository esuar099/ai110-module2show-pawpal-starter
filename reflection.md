# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

ANSWER: Pet owner should be able to add pets, add pet care tasks, and prduce a daily plan of tasks.

- What classes did you include, and what responsibilities did you assign to each?

ANSWER: 
Class: Owner
Attributes: Owner Name, Date of Birth, Age, Availability, Preferences
Methods: Modify Owner
Responsibility: Stores owner details, including availability, contraints, and preferences.

Class: Pet
Attributes: Pet Name, Date of Birth, Age, Species, Breed
Methods: Add pet, modify pet, remove pet
Responsibility: Stores pet details; it also lets you modify or remove any pets.

Class: Task
Attributes: Task Name, Owner Name, Pet Name, Priority, Scheduled Date, Scheduled Start Time, Scheduled End Time, Duration
Methods: Add task, modify task, remove task
Responsibility: Stores task details, including priority and duration

Class: Plan
Attributes: Date, List of Tasks
Methods: View plan, modify plan, remove plan
Responsibility: Generates a plan based on tasks scheduled for a particular day.


**b. Design changes**

- Did your design change during implementation?

ANSWER: Yes

- If yes, describe at least one change and why you made it.

ANSWER: Added connections properly between Owner and Pet, Task, Plan. It wasn't explicitly mentioned that Owner could own Pet(s), Task(s), and Plan(s). Also, added an ID to Owner, Pet, Task, and Plan, for easy connection amongst them.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

ANSWER: It considers owner's available time, task's duration, and task's priority

- How did you decide which constraints mattered most?

ANSWER: The problem was not clear with what user preferences really meant, leading to ambiguousness. I believe the user's available time and the priorities and durations of a set of task mattered the most when scheduling these tasks. Scheduling is all about time management, so I'd need constraints in relation to times (like availability and durations) and priority to create a simple and straightforward plan.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

ANSWER: As I tested the scheduler, I added a task called "Evening bath", high priority, and duration of 30 minutes. However, the scheduler determined to have it scheduled at 9:00 AM since it was the only task I set as high priority. It doesn't make sense to have an evening bath in the morning.

- Why is that tradeoff reasonable for this scenario?

ANSWER: The scheduler's primary purpose is to take an array of tasks with priorities and durations. Based on the scheduler's logic, it will schedule tasks based upon priority. Because the task was flagged as High priority, the scheduler did its job as codified. The scheduler's logic can be expanded and tailored further as more and more user cases like these emerge.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
