import json
import inspect
from ..SharedCode import consts
from ..SharedCode.logger import applogger
from ..SharedCode.sentinel import MicrosoftSentinel
from ..SharedCode.utils import TeamCymruScoutUtility
from ..SharedCode.teamcymruscout_client import TeamCymruScout
from ..SharedCode.teamcymruscout_exception import TeamCymruScoutException


class AccountUsageData:
    def __init__(self) -> None:
        """Initialize the object of AccountUsageData."""
        self.logs_starts_with = consts.LOGS_STARTS_WITH + " AccountUsageData:"
        self.input_domain_values = []
        self.watchlist_domain_values = []
        self.rest_helper_obj = TeamCymruScout()
        self.utility_obj = TeamCymruScoutUtility(file_path="accountUsage")
        self.utility_obj.validate_params()


    def get_account_usage_data(self):
        """To retrieve account usage data, fetch details from 
           Team Cymru Scout and post it to Sentinel."""
        __method_name = inspect.currentframe().f_code.co_name
        try:

            applogger.debug(
                "{}(method={}) fetch account usages data from Cymru Scout.".format(
                    self.logs_starts_with, __method_name
                )
            )

            account_data = self.rest_helper_obj.make_rest_call(
                endpoint=consts.ACCOUNT_USAGE_ENDPOINT, params={}
            )
            ms_sentinel_obj = MicrosoftSentinel()
            body = json.dumps(account_data)
            response = ms_sentinel_obj.post_data(body, consts.ACCOUNT_USAGE_TABLE_NAME)        

            applogger.debug("{}(method={}) Sentinel response: {}".format(
                self.logs_starts_with, __method_name, response)
            )
        except Exception as err:
            applogger.error(
                "{}(method={}) {}".format(self.logs_starts_with, __method_name, err)
            )
            raise TeamCymruScoutException()