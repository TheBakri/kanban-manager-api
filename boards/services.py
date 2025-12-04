from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Board, BoardList, DEFAULT_LISTS


def ensure_default_lists(board: Board) -> None:
    if board.lists.exists():
        return
    for index, name in enumerate(DEFAULT_LISTS, start=1):
        BoardList.objects.create(board=board, name=name, position=index)


@transaction.atomic
def reorder_board_lists(board: Board, ordered_ids: list[int]) -> None:
    existing_ids = list(board.lists.values_list("id", flat=True))
    if len(ordered_ids) != len(existing_ids) or set(existing_ids) != set(ordered_ids):
        raise ValidationError("Order must include all board lists.")

    ordering_map = {item_id: idx for idx, item_id in enumerate(ordered_ids, start=1)}
    lists = board.lists.all()
    for board_list in lists:
        new_position = ordering_map.get(board_list.id)
        if new_position is None:
            raise ValidationError("Invalid list id in order payload.")
        if board_list.position != new_position:
            board_list.position = new_position
            board_list.save(update_fields=["position"])
