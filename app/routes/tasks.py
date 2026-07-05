"""CRUD endpoints for tasks. Every query is scoped to the authenticated user."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.database import get_conn
from app.deps import current_user_id

router = APIRouter()


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    notes: str = ""
    status: str = Field(default="todo", pattern="^(todo|doing|done)$")
    priority: int = Field(default=2, ge=1, le=3)
    due_date: Optional[str] = None


@router.get("")
def list_tasks(status: Optional[str] = None, user_id: int = Depends(current_user_id)):
    query = "SELECT * FROM tasks WHERE user_id = ?"
    params = [user_id]
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY priority DESC, created_at DESC"
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


@router.post("", status_code=201)
def create_task(body: TaskIn, user_id: int = Depends(current_user_id)):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (user_id, title, notes, status, priority, due_date)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, body.title, body.notes, body.status, body.priority, body.due_date),
        )
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (cur.lastrowid,)).fetchone()
    return dict(row)


@router.put("/{task_id}")
def update_task(task_id: int, body: TaskIn, user_id: int = Depends(current_user_id)):
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE tasks SET title=?, notes=?, status=?, priority=?, due_date=?,"
            " updated_at=CURRENT_TIMESTAMP WHERE id=? AND user_id=?",
            (body.title, body.notes, body.status, body.priority, body.due_date, task_id, user_id),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return dict(row)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, user_id: int = Depends(current_user_id)):
    with get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id)
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
