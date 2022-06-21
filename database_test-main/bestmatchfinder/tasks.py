from celery import shared_task
from bestmatchfinder import submit_single_sequence


@shared_task
def run_needle(filename):
    try:
        # print("This is needle function", "align")
        align = submit_single_sequence.align.run_bug(filename)
        # print("This is task file", align)
        return align
    except IOError as e:
        print(e)
