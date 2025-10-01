import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from configs.scripts import dell_logs
from configs.settings import TOKEN
from handlers.main import router_main

# базовая фигня,тупо копируется везде
storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)


# позволяет объеденить все предыдущие файлы в один и запустить
async def main():
        # удаляет старые логи
        dell_logs()
        # запускает логирование
        logging.basicConfig(level=logging.ERROR, filename='logs.log', filemode='w', format='[%(asctime)s] %(filename)s:%(lineno)d %(levelname)-8s %(message)s')
        dp.include_router(router_main)
        await dp.start_polling(bot)

# чтоб понять работает ли скрипт
print(1)

# запускает цикл, чтобы бот работал без остановок
if __name__ == "__main__":
    asyncio.run(main())