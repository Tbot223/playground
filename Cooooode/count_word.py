import os
from Core import AppCore
from Core import LogSys
from Core import Deco
from CoreV2.Exception import ExceptionTrackerDecorator

def count_word_in_file(file_path: str) -> int:
    count = 0
    with open(file_path, 'r', encoding='utf-8') as file:
        count = len(file.read().split())
    return count

@ExceptionTrackerDecorator()
@Deco.count_run_time(Deco)
def main():
    logger_manager = LogSys.LoggerManager(base_dir="./logs", second_log_dir="CountWordLogs")
    logger_manager.Make_logger("CountWord")
    log = LogSys.Log(logger=logger_manager.get_logger("CountWord").data)
    app_core = AppCore.AppCore(logger_manager=logger_manager)
    bp = os.path.dirname(os.path.abspath(__file__))
    file_paths = [f"{bp}/tmp.txt", f"{bp}/tmp2.txt", f"{bp}/tmp3.txt", f"{bp}/tmp4.txt"]

    tasks = [(count_word_in_file, {'file_path': path}) for path in file_paths]
    result = app_core.multi_process_executer(tasks, process=1)
    result = ", ".join(str(n) for n in result.data)
    log.log_msg("info", f"Word count results: {result}", False)

if __name__ == "__main__":
    main()
