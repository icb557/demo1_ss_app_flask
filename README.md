# Web App: "Life Organizer"

## General Description

"Life Organizer" is a multifunctional web app that combines a task manager with a personal diary. Users can organize their daily activities and also record their experiences, such as trips, important events, and other notes, all without the need to manage files or photos. Everything is handled simply and effectively through text.

### Use Case 1: Task Manager

**Objective:** Help users organize their daily activities with the ability to add, edit, delete, and mark tasks as completed.

**Workflow:**

1. Main page: The user sees a panel divided into two sections: Tasks and Personal Diary.

2. Add task: Users can add new tasks from the main page with a title, description, due date, and category (work, personal, urgent).

3. Edit and delete: Tasks can be edited or deleted if necessary.

4. Mark as completed: Users can mark completed tasks, and these move to a separate list or are displayed with a different style (such as strikethrough).

5. Filter tasks: The system allows filtering tasks by date, category, or status (pending/completed).

**Features:**

- Organized task list.

- Task filters by category and date.

- Simple forms for adding or editing tasks.

- Authentication with Flask-Login for managing personal tasks.

### Use Case 2: Personal Diary (Events, Notes, Experiences)

**Objective:** Allow users to record important events, life experiences (such as trips or celebrations), and personal notes, all in text format.

**Workflow:**

1. Main page: The home panel shows two sections: one for Tasks and another for the Personal Diary.

2. Add diary entry: Users can add new diary entries with a title, date, location (optional), and a description of the event or experience. Example: "Trip to Barcelona", "Birthday 2025", "Important work meeting".

3. View details: Users can see a summary of each diary entry, with the option to edit or delete it if desired.

4. Search entries: The system allows searching diary entries by date, keywords, or location (if included).

5. Relationship with tasks: Diary entries can be related to tasks. For example, if the user is planning a trip, they can create related tasks (such as "Book hotel", "Buy tickets") that will appear alongside their diary entry.

**Features:**

- Create diary entries with title, date, description, and location (optional).

- Relate tasks to diary entries for tracking.

- Summary view of entries with the option to edit or delete.

- Search entries by date or keywords.

- Authentication with Flask-Login for personalized tracking.

### Interactions between both use cases

Task and Diary Synchronization: Tasks can be linked to diary entries. For example, if the user is planning a trip (diary entry), they can add related tasks (book flights, pack, etc.) and link them to the corresponding entry.

Integrated view: In the Personal Diary view, tasks related to the event or experience can appear as reminders of what the user needs to do in relation to that entry.

### Technologies

- Backend: Flask

- Database: PostgreSQL

- Authentication: Flask-Login

- Frontend: HTML, CSS, and JavaScript
