import sqlite3
from datetime import datetime, date

DB_FILE = "todo.db"
PRIORITIES = ["low", "medium", "high"]


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def run_query(sql, params=(), fetch=False):
    conn = get_connection()
    cur = conn.execute(sql, params)
    rows = cur.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return rows, cur.rowcount


def init_db():
    """Create the task table if it doesn't already exist"""
    conn = get_connection()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        priority TEXT DEFAULT 'medium',
        done INTEGER DEFAULT 0,
        deadline TEXT,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()


def add_task():
    title = input("Task title: ").strip()
    if not title:
        print("Title cannot be empty.")
        return

    print(f"Priority options: {', '.join(PRIORITIES)}")
    priority = input("Priority [medium]: ").strip().lower()
    if priority not in PRIORITIES:
        priority = "medium"

    deadline = input("Deadline (YYYY-MM-DD, or press Enter to skip): ").strip()
    if deadline:
        try:
            date.fromisoformat(deadline)
        except ValueError:
            print("Invalid date format. Skipping deadline.")
            deadline = None
    else:
        deadline = None

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    run_query(
        "INSERT INTO tasks (title, priority, deadline, created_at) VALUES (?, ?, ?, ?)",
        (title, priority, deadline, now)
    )
    print(f"Task added: '{title}' [{priority}]")


def view_tasks(filter_done=None, filter_priority=None, sort_by=None):
    query = "SELECT * FROM tasks"
    params = []
    conditions = []

    if filter_done is not None:
        conditions.append("done = ?")
        params.append(filter_done)
    if filter_priority:
        conditions.append("priority = ?")
        params.append(filter_priority)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    if sort_by == "created_at":
        query += " ORDER BY created_at DESC"
    elif sort_by == "deadline":
        query += " ORDER BY deadline ASC"
    else:
        query += """
         ORDER BY
         CASE priority
           WHEN 'high' THEN 1
           WHEN 'medium' THEN 2
           WHEN 'low' THEN 3
           ELSE 4
         END,
         deadline ASC
        """

    rows, _ = run_query(query, params, fetch=True)

    if not rows:
        print("No tasks found.")
        return

    print(f"\n{'ID':4}{'Title':30}{'Priority':10}{'Done':6}{'Deadline'}")
    print("-" * 65)
    for row in rows:
        status = "✓" if row["done"] else "o"
        deadline = row["deadline"] or "--"
        print(f"{row['id']:4}{row['title']:30}{row['priority']:10}{status:6}{deadline}")


def complete_task():
    view_tasks(filter_done=0)
    try:
        task_id = int(input("Enter task ID to mark complete: "))
    except ValueError:
        print("Invalid ID.")
        return

    _, rowcount = run_query(
        "UPDATE tasks SET done = 1 WHERE id = ? AND done = 0",
        (task_id,)
    )

    if rowcount == 0:
        print("Task not found or already complete.")
    else:
        print(f"Task {task_id} marked complete!")


def update_title():
    view_tasks()
    try:
        task_id = int(input("Enter task ID to update title: "))
    except ValueError:
        print("Invalid ID.")
        return

    new_title = input("New title: ").strip()
    if not new_title:
        print("Title cannot be empty.")
        return

    _, rowcount = run_query(
        "UPDATE tasks SET title = ? WHERE id = ?",
        (new_title, task_id)
    )

    print("Task updated." if rowcount else "Task not found.")


def update_priority():
    view_tasks()
    try:
        task_id = int(input("Enter task ID to update priority: "))
    except ValueError:
        print("Invalid ID.")
        return

    print(f"Priority options: {', '.join(PRIORITIES)}")
    new_priority = input("New priority: ").strip().lower()
    if new_priority not in PRIORITIES:
        print("Invalid priority.")
        return

    _, rowcount = run_query(
        "UPDATE tasks SET priority = ? WHERE id = ?",
        (new_priority, task_id)
    )

    print("Task updated." if rowcount else "Task not found.")


def update_deadline():
    view_tasks()
    try:
        task_id = int(input("Enter task ID to update deadline: "))
    except ValueError:
        print("Invalid ID.")
        return

    deadline = input("New deadline (YYYY-MM-DD, or blank to clear): ").strip()
    if deadline:
        try:
            date.fromisoformat(deadline)
        except ValueError:
            print("Invalid date format.")
            return
    else:
        deadline = None

    _, rowcount = run_query(
        "UPDATE tasks SET deadline = ? WHERE id = ?",
        (deadline, task_id)
    )

    print("Task updated." if rowcount else "Task not found.")


def delete_task():
    view_tasks()
    try:
        task_id = int(input("Enter task ID to delete: "))
    except ValueError:
        print("Invalid ID.")
        return

    confirm = input(f"Delete task {task_id}? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancelled")
        return

    _, rowcount = run_query(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    print("Task deleted." if rowcount else "Task not found.")


def filter_tasks():
    print("\nFilter by:")
    print("1. Priority")
    print("2. Incomplete tasks only")
    print("3. Completed tasks only")
    print("4. By deadline (upcoming first)")

    choice = input("Filter choice: ").strip()

    if choice == "1":
        priority = input("Priority (low/medium/high): ").strip().lower()
        view_tasks(filter_priority=priority)
    elif choice == "2":
        view_tasks(filter_done=0)
    elif choice == "3":
        view_tasks(filter_done=1)
    elif choice == "4":
        view_tasks(sort_by="deadline")
    else:
        print("Invalid filter.")


def search_tasks():
    term = input("Search title contains: ").strip()
    if not term:
        print("Search term cannot be empty.")
        return

    rows, _ = run_query(
        "SELECT * FROM tasks WHERE title LIKE ? ORDER BY created_at DESC",
        (f"%{term}%",),
        fetch=True
    )

    if not rows:
        print("No matches.")
        return

    print(f"\n{'ID':4}{'Title':30}{'Priority':10}{'Done':6}{'Deadline'}")
    print("-" * 65)
    for row in rows:
        status = "✓" if row["done"] else "o"
        deadline = row["deadline"] or "--"
        print(f"{row['id']:4}{row['title']:30}{row['priority']:10}{status:6}{deadline}")


def show_reminders():
    today = date.today()

    rows, _ = run_query(
        """SELECT * FROM tasks
        WHERE done = 0
        AND deadline IS NOT NULL
        ORDER BY deadline ASC""",
        fetch=True
    )

    overdue = []
    due_soon = []

    for row in rows:
        deadline = date.fromisoformat(row["deadline"])
        days_left = (deadline - today).days

        if days_left < 0:
            overdue.append((row, days_left))
        elif days_left <= 2:
            due_soon.append((row, days_left))

    if overdue:
        print("\nOVERDUE TASKS:")
        for row, days in overdue:
            print(f" [{row['id']}] {row['title']} -- {abs(days)} day(s) overdue!")

    if due_soon:
        print("\nDUE SOON:")
        for row, days in due_soon:
            when = "TODAY" if days == 0 else f"in {days} day(s)"
            print(f"[{row['id']}] {row['title']} -- due {when}")

    if not overdue and not due_soon:
        print("NO upcoming deadlines.")


def show_menu():
    print("\n======== Todo List ========")
    print("1. Add task")
    print("2. View tasks")
    print("3. Mark task complete")
    print("4. Update task title")
    print("5. Update task priority")
    print("6. Update task deadline")
    print("7. Delete task")
    print("8. Filter tasks")
    print("9. Search tasks")
    print("10. View by created date")
    print("11. Exit")
    print("===========================")


def main():
    init_db()
    show_reminders()
    print("Welcome to your Todo List!")

    while True:
        show_menu()
        choice = input("Your choice: ").strip()

        if choice == "1":
            add_task()
        elif choice == "2":
            view_tasks()
        elif choice == "3":
            complete_task()
        elif choice == "4":
            update_title()
        elif choice == "5":
            update_priority()
        elif choice == "6":
            update_deadline()
        elif choice == "7":
            delete_task()
        elif choice == "8":
            filter_tasks()
        elif choice == "9":
            search_tasks()
        elif choice == "10":
            view_tasks(sort_by="created_at")
        elif choice == "11":
            print("Goodbye!")
            break
        else:
            print("Enter a number from 1 to 11")


if __name__ == "__main__":
    main()