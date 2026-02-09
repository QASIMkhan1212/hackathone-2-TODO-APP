from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


class TaskCRUD:
    def create(self, db: Session, user_id: str, task_data: TaskCreate) -> Task:
        """Create a new task."""
        task = Task(
            user_id=user_id,
            title=task_data.title,
            description=task_data.description
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def get(self, db: Session, user_id: str, task_id: int) -> Optional[Task]:
        """Get a task by ID for a specific user."""
        return db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()

    def get_all(
        self,
        db: Session,
        user_id: str,
        status: Optional[str] = None
    ) -> List[Task]:
        """Get all tasks for a user, optionally filtered by status."""
        query = db.query(Task).filter(Task.user_id == user_id)

        if status == "completed":
            query = query.filter(Task.completed == True)
        elif status == "pending":
            query = query.filter(Task.completed == False)

        return query.order_by(Task.created_at.desc()).all()

    def update(
        self,
        db: Session,
        user_id: str,
        task_id: int,
        task_data: TaskUpdate
    ) -> Optional[Task]:
        """Update a task."""
        task = self.get(db, user_id, task_id)
        if not task:
            return None

        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description

        db.commit()
        db.refresh(task)
        return task

    def complete(self, db: Session, user_id: str, task_id: int) -> Optional[Task]:
        """Mark a task as completed."""
        task = self.get(db, user_id, task_id)
        if not task:
            return None

        task.completed = True
        db.commit()
        db.refresh(task)
        return task

    def delete(self, db: Session, user_id: str, task_id: int) -> Optional[Task]:
        """Delete a task."""
        task = self.get(db, user_id, task_id)
        if not task:
            return None

        db.delete(task)
        db.commit()
        return task


task_crud = TaskCRUD()
