"""
Файл с различными основными функциями
"""



# ипортирует всякие библиотеки и файлы
import os


# очищает логи
def dell_logs():
    try:
        os.remove('logs.log')

    except FileNotFoundError:
        pass

    try:
        os.remove('logs_main.log')
    except FileNotFoundError:
        pass



