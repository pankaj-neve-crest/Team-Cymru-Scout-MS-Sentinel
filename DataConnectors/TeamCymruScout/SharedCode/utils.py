"""This file contains utility functions to be used by other modules."""
from . import consts
import inspect
import re
from .logger import applogger
from .teamcymruscout_exception import TeamCymruScoutException
from .state_manager import StateManager
from .get_logs_data import get_logs_data


class TeamCymruScoutUtility:
    """Class for performing various tasks."""

    def __init__(self, file_path) -> None:
        """
        Initialize the insatnce object of TeamCymruScoutUtility.

        Args:
            file_path (str): path of the file.
        """
        self.state = StateManager(
            connection_string=consts.CONN_STRING, file_path=file_path
        )
        self.logs_starts_with = "{} DomainDataCollector:".format(
            consts.LOGS_STARTS_WITH
        )
        self.constants = {"domain": consts.DOMAIN_VALUES, "ip": consts.IP_VALUES}
        self.query_constants = {"domain": consts.DOMAIN_QUERY, "ip": consts.IP_QUERY}

    def validate_params(self):
        """
        To validate the required parameters for the function.

        Raises:
            TeamCymruScoutException: If any required parameter is missing or empty.
        """
        __method_name = inspect.currentframe().f_code.co_name
        required_params = {
            "CymruScoutBaseURL": consts.CYMRU_SCOUT_BASE_URL,
            "AuthenticationType": consts.AUTHENTICATION_TYPE,
            "APIType": consts.API_TYPE,
            "AZURE_CLIENT_ID": consts.AZURE_CLIENT_ID,
            "AZURE_CLIENT_SECRET": consts.AZURE_CLIENT_SECRET,
            "AZURE_TENANT_ID": consts.AZURE_TENANT_ID,
            "WorkspaceID": consts.WORKSPACE_ID,
            "WorkspaceKey": consts.WORKSPACE_KEY,
            "IPTableName": consts.IP_TABLE_NAME,
            "DomainTableName": consts.DOMAIN_TABLE_NAME,
            "AccountUsageTableName": consts.ACCOUNT_USAGE_TABLE_NAME,
        }
        if consts.AUTHENTICATION_TYPE == "API Key":
            required_params.update({"APIKey": consts.API_KEY})
        else:
            required_params.update(
                {"Username": consts.USERNAME, "Password": consts.PASSWORD}
            )
        applogger.debug(
            "{}(method={}) : Checking if all the environment variables exist or not.".format(
                consts.LOGS_STARTS_WITH, __method_name
            )
        )
        missing_required_field = False
        for label, params in required_params.items():
            if not params or params == "":
                missing_required_field = True
                applogger.error(
                    '{}(method={}) : "{}" field is not set in the environment please set '
                    "the environment variable and run the app.".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        label,
                    )
                )
        if missing_required_field:
            raise TeamCymruScoutException(
                "Error Occurred while validating params. Required fields missing."
            )
        applogger.info(
            "{}(method={}) : All necessary variables are present in the Configuration.".format(
                consts.LOGS_STARTS_WITH, __method_name
            )
        )

    def validate_ip_domain(self, indicator, regex_pattern):
        """
        To validate if the given indicator is a valid IP or domain.

        Args:
            indicator (str): The indicator to be validated.
            regex_pattern (str): The regular expression pattern to match the indicator.

        Returns:
            bool: True if the indicator is a valid IP or domain, False otherwise.
        """
        __method_name = inspect.currentframe().f_code.co_name
        if re.search(regex_pattern, indicator):
            return True
        else:
            applogger.info(
                "{}(method={}) : {} is not a valid IP/Domain.".format(
                    consts.LOGS_STARTS_WITH, __method_name, indicator
                )
            )
            return False

    def get_checkpoint(self, indicator_type):
        """
        To retrieve the checkpoint for a given indicator type.

        Args:
            indicator_type (str): The type of the indicator.

        Returns:
            Any: The checkpoint value if it exists, otherwise None.

        Raises:
            TeamCymruScoutException: If an error occurs while retrieving the checkpoint.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            last_data_index = self.state.get()
            if last_data_index:
                return last_data_index
            else:
                applogger.debug(
                    "{} (method={}): Checkpoint is not available for {}.".format(
                        consts.LOGS_STARTS_WITH, __method_name, indicator_type
                    )
                )
                return None
        except Exception as err:
            applogger.exception(
                "{}: GET LAST DATA: {}".format(consts.LOGS_STARTS_WITH, err)
            )
            raise TeamCymruScoutException()

    def save_checkpoint(self, data, indicator_type):
        """
        Save the checkpoint for a given indicator type.

        Args:
            data (Any): The data to be saved as the checkpoint.
            indicator_type (str): The type of the indicator.

        Raises:
            TeamCymruScoutException: If an error occurs while saving the checkpoint.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            self.state.post(data)
            applogger.info(
                "{} (method={}) Checkpoint index={} saved for {}".format(
                    consts.LOGS_STARTS_WITH, __method_name, data, indicator_type
                )
            )
        except Exception as err:
            applogger.exception(
                "{} (method={}) {}".format(consts.LOGS_STARTS_WITH, __method_name, err)
            )
            raise TeamCymruScoutException()

    def get_data_from_input(self, indicator_type):
        """
        To retrieve data from the input based on the given indicator type.

        Args:
            indicator_type (str): The type of the indicator.

        Returns:
            list: A list of input values.

        Raises:
            TeamCymruScoutException: If an error occurs.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            if not self.constants.get(indicator_type):
                applogger.info(
                    "{} (method={}) : No {} values found in the input.".format(
                        self.logs_starts_with, indicator_type, __method_name
                    )
                )
            input_values = [
                data.strip() for data in self.constants.get(indicator_type).split(",")
            ]
            applogger.debug(
                "{} (method={}) : {} data to fetch for input data: {}".format(
                    self.logs_starts_with, __method_name, indicator_type, input_values
                )
            )
            return input_values
        except Exception as err:
            applogger.error(
                "{}(method={}) {}".format(self.logs_starts_with, __method_name, err)
            )
            raise TeamCymruScoutException()

    def get_data_from_watchlists(self, indicator_type):
        """
        To retrieve data from watchlists based on the given indicator type.

        Args:
            indicator_type (str): The type of the indicator.

        Returns:
            list or None: A list of values from the watchlist if the indicator type is found,
                          otherwise None.

        Raises:
            TeamCymruScoutException: If an error occurs while retrieving the data.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            logs_data, flag = get_logs_data(self.query_constants.get(indicator_type))
            if not flag:
                applogger.info(
                    "{} (method={}) : No {} values found in the watchlist.".format(
                        self.logs_starts_with, __method_name, indicator_type
                    )
                )
                return None
            watchlist_data = [data[indicator_type] for data in logs_data]
            last_checkpoint_data = self.get_checkpoint(indicator_type)
            applogger.debug("Last Checkpoint Data: {}".format(last_checkpoint_data))
            applogger.debug(
                "Last {} value from watchlist: {}".format(
                    indicator_type, watchlist_data[-1]
                )
            )
            if (
                last_checkpoint_data is not None
                and last_checkpoint_data != watchlist_data[-1]
            ):
                watchlist_values = watchlist_data[
                    watchlist_data.index(last_checkpoint_data) + 1: len(watchlist_data)
                ]
            else:
                watchlist_values = watchlist_data
            applogger.debug(
                "{} (method={}) : {} data to fetch for watchlist data: {}".format(
                    self.logs_starts_with,
                    __method_name,
                    indicator_type,
                    watchlist_values,
                )
            )
            return watchlist_values
        except Exception as err:
            applogger.error(
                "{}(method={}) {}".format(self.logs_starts_with, __method_name, err)
            )
            raise TeamCymruScoutException()