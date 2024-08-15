from inspect import getmembers
from typing import List

from fastapi import APIRouter


def get_routers() -> List[APIRouter]:
    """Предоставляет все доступные роутеры"""
    import web.api.views

    return [router for _, router in getmembers(web.api.views) if isinstance(router, APIRouter)]
