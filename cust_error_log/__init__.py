import traceback
import sys
import datetime

def error_report(error, use_test=False):
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

    if use_test:
        for trace in trace_back:
            stack_trace.append("Test File : %s ,\nLine : %d,\nFunc.Name : %s,\nMessage : %s\n" % (trace[0], trace[1], trace[2], trace[3]))
    else:
        for trace in trace_back:
            stack_trace.append("File : %s ,\nLine : %d,\nFunc.Name : %s,\nMessage : %s\n" % (trace[0], trace[1], trace[2], trace[3]))
    with open('Output/file_read_error.log', 'a') as f:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        f.write(str(dt_string) + ":\n" + str(stack_trace[0]) + str(error) + "\n")
        f.close()