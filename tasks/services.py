from __future__ import annotations

from typing import List

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max, F

from .models import Task, Subtask


@transaction.atomic
def reorder_tasks(board_list, ordered_ids: List[int]) -> None:
    existing_ids = list(board_list.tasks.values_list("id", flat=True))
    if len(ordered_ids) != len(existing_ids) or set(ordered_ids) != set(existing_ids):
        raise ValidationError("Order must include all tasks in the list.")

    ordering_map = {item_id: idx for idx, item_id in enumerate(ordered_ids, start=1)}
    tasks = board_list.tasks.all()
    for task in tasks:
        new_position = ordering_map.get(task.id)
        if new_position is None:
            raise ValidationError("Invalid task id in order payload.")
        if task.position != new_position:
            task.position = new_position
            task.save(update_fields=["position"])


@transaction.atomic
def move_task_to_list(task: Task, target_list, position: int | None = None) -> Task:
    if task.board_list == target_list:
        # nothing to do
        return task
    # Adjust positions on source list: decrement tasks with position > current
    source_list = task.board_list
    source_tasks = source_list.tasks.filter(position__gt=task.position)
    for t in source_tasks:
        t.position = t.position - 1
        t.save(update_fields=["position"])

    # Determine new position in target list
    if position is None:
        max_pos = target_list.tasks.aggregate(max_pos=Max("position")).get("max_pos") or 0
        position = max_pos + 1
    else:
        # shift existing tasks in target list equal or greater than position
        target_list.tasks.filter(position__gte=position).update(position=F("position") + 1)

    task.board_list = target_list
    task.position = position
    task.status = target_list.name
    task.save(update_fields=["board_list", "position", "status"])
    return task
