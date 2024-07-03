import os
import time
import logging
import datetime
import azure.functions as func
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from .account_usage_data import AccountUsageData

def main(mytimer: func.TimerRequest) -> None:
    """
    This function is triggered by a timer schedule.

    Args:
        mytimer (func.TimerRequest): The timer object that triggered the function
    """
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    start_time = time.time()
    account_usage_obj = AccountUsageData()
    account_usage_obj.get_account_usage_data()
    end_time = time.time()

    applogger.info(
        "{} DomainDataCollector: Time taken to ingest domain data is {}".format(
            consts.LOGS_STARTS_WITH, end_time-start_time
        )
    )
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
