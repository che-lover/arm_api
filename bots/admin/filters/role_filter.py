from typing import Tuple
from aiogram.filters.base import  Filter as BaseFilter
from aiogram.types import  Message
from aiogram.fsm.context import FSMContext

class RoleFilter(BaseFilter):
    allowed: Tuple[str, ...]  # просто объявляем поле фильтра

    def __init__(self, *allowed_roles: str, **kwargs):
        # Позволяем передавать позиционные аргументы,
        # но сохраняем их в поле `allowed`
        # super().__init__(**kwargs)  # calls BaseFilter internal init
        object.__setattr__(self, "allowed", tuple(allowed_roles))

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        data = await state.get_data()
        return data.get("role") in self.allowed
