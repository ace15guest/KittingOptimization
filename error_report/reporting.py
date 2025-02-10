import os
import traceback
import sys
from datetime import datetime
from pathlib import Path
def error_report(error):
    """
    This reports errors to the log file in the <Output Directory>
    :param error:
    :return:
    """
    ex_type, ex_value, ex_traceback = sys.exc_info()
    # Extract un-formatter stack traces as tuples
    trace_back = traceback.extract_tb(ex_traceback)
    # Format stacktrace
    stack_trace = list()

    for trace in trace_back:
        stack_trace.append("File : %s ,\nLine : %d,\nFunc.Name : %s,\nMessage : %s\n" % (trace[0], trace[1], trace[2], trace[3]))
    path = f"{os.environ['TMP']}/KittingOptimization/logs/"
    Path(f"{path}").mkdir(exist_ok=True, parents=True)
    with open(f'{path}/errors.log', 'a', encoding='utf-8') as f:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        f.write(str(dt_string) + ":\n" + str(stack_trace[0]) + str(error) + "\n")
        f.close()
    return path + 'errors.log'