import importlib
import os
from aiogram import Dispatcher


def include_routers(dp: Dispatcher):
    current_dir = os.path.dirname(__file__)
    for filename in os.listdir(current_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = f"{__name__}.{filename[:-3]}"
            mod = importlib.import_module(module_name)
            if hasattr(mod, 'router'):
                dp.include_router(mod.router)
