from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction

from .utils import replace_user_avatar

User = get_user_model()


def create_user_account(**validated_data: Any) -> User:
    avatar = validated_data.pop("avatar", None)
    with transaction.atomic():
        user = User.objects.create_user(**validated_data)
        if avatar:
            user.avatar = avatar
            user.save(update_fields=["avatar"])
    return user


_SENTINEL = object()


def update_user_profile(user: User, **validated_data: Any) -> User:
    avatar = validated_data.pop("avatar", _SENTINEL)
    for attr, value in validated_data.items():
        setattr(user, attr, value)
    if avatar is not _SENTINEL:
        replace_user_avatar(user, avatar)
    user.save()
    return user

