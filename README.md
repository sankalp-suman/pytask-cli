# pytask-cli

A lightweight command-line todo manager built with Python and SQLite. Manage tasks with priority levels, deadlines, and smart reminders — no external dependencies required.

## Features

- **Add & manage tasks** — create tasks with a title, priority, and optional deadline
- **Priority levels** — low, medium, and high; tasks are sorted by priority by default
- **Deadline tracking** — set due dates and get automatic reminders for overdue or upcoming tasks
- **Flexible views** — filter by status or priority, sort by deadline or creation date
- **Search** — find tasks by keyword
- **Full CRUD** — update titles, priorities, deadlines, mark complete, or delete tasks
- **Persistent storage** — all data stored locally in a SQLite database (`todo.db`)

## Requirements

- Python 3.7+
- No third-party packages needed (`sqlite3` and `datetime` are standard library)

## Getting Started

```bash
git clone https://github.com/your-username/pytask-cli.git
cd pytask-cli
python todo.py
```

A `todo.db` file will be created automatically in the same directory on first run.

## Usage

On launch, the app checks for overdue or upcoming deadlines and prints a reminder summary. You're then presented with an interactive menu:

```
======== Todo List ========
1.  Add task
2.  View tasks
3.  Mark task complete
4.  Update task title
5.  Update task priority
6.  Update task deadline
7.  Delete task
8.  Filter tasks
9.  Search tasks
10. View by created date
11. Exit
===========================
```

### Adding a task

You'll be prompted for:
- **Title** — required
- **Priority** — `low`, `medium`, or `high` (defaults to `medium`)
- **Deadline** — optional, in `YYYY-MM-DD` format

### Filtering tasks

Choose from:
- Filter by priority
- Show only incomplete tasks
- Show only completed tasks
- Sort by upcoming deadline

### Reminders

Every time the app starts, it highlights:
- **Overdue tasks** — past their deadline and still incomplete
- **Due soon** — deadline is today or within the next 2 days

## Project Structure

```
pytask-cli/
├── todo.py      # Main application
└── todo.db      # SQLite database (auto-generated, git-ignored)
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

## License

[MIT](LICENSE)
