"""This file contains TeamCymruScout class for interacting with TeamCymruScout APIs and posting data to Sentinel."""

import requests
import inspect
import json
from requests.auth import HTTPBasicAuth
from .logger import applogger
from .teamcymruscout_exception import TeamCymruScoutException
from .sentinel import MicrosoftSentinel
from . import consts


class TeamCymruScout:
    """Class for interacting with TeamCymruScout APIs and posting data to Sentinel."""

    def __init__(self) -> None:
        """Initialize the insatnce object of TeamCymruScout."""
        self.base_url = consts.CYMRU_SCOUT_BASE_URL
        self.session = requests.Session()
        self.session.headers["Content-Type"] = "application/json"
        self.auth = None
        self.set_authorization_header()
        self.ms_sentinel_obj = MicrosoftSentinel()
        self.error_logs = "{}(method={}) {}"

    def set_authorization_header(self):
        """Set the authorization header based on the authentication type."""
        if consts.AUTHENTICATION_TYPE == "API Key":
            applogger.debug("API Key based authentiction is selected.")
            self.session.headers["Authorization"] = "Token: {}".format(consts.API_KEY)
        else:
            self.auth = HTTPBasicAuth(
                username=consts.USERNAME, password=consts.PASSWORD
            )
            applogger.info("Username and password based authentiction is selected.")

    def make_rest_call(self, endpoint, params=None, body=None):
        """To call Team Cymru Scout API.

        Args:
            endpoint (str): endpoint to call.
            params (json, optional): query parameters to pass in API call. Defaults to None.
            body (json, optional): Request body to pass in API call. Defaults to None.

        Returns:
            json: returns json response if API call succeed.
        """
        try:
            __method_name = inspect.currentframe().f_code.co_name
            applogger.debug(
                "(method={}) Calling Team Cymru Scout API for endpoint={} with params={}".format(
                    __method_name, endpoint, params
                )
            )
            request_url = "{}{}".format(self.base_url, endpoint)
            response = self.session.get(
                url=request_url, params=params, data=body, auth=self.auth
            )
            response.raise_for_status()
            if response.status_code == 200:
                response_json = response.json()
                return response_json
            else:
                applogger.error(
                    "{}(method={}) Error while fetching data from url={}. Status code: {}, Error: {}".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        request_url,
                        response.status_code,
                        response.text,
                    )
                )
                raise TeamCymruScoutException()
        except requests.exceptions.HTTPError as err:
            status_code = err.response.status_code
            if status_code == 401:
                applogger.error(
                    "{}(method={}) Please verify the provided credentials.".format(
                        consts.LOGS_STARTS_WITH, __method_name
                    )
                )
                raise TeamCymruScoutException()

            elif status_code == 429:
                applogger.error(
                    "{}(method={}) Team Cymru Scout API Limit Exceeded.".format(
                        consts.LOGS_STARTS_WITH, __method_name
                    )
                )
                raise TeamCymruScoutException()

            else:
                applogger.error(
                    self.error_logs.format(consts.LOGS_STARTS_WITH, __method_name, err)
                )
                raise TeamCymruScoutException()
        except requests.exceptions.RequestException as err:
            applogger.error(
                self.error_logs.format(consts.LOGS_STARTS_WITH, __method_name, err)
            )
            raise TeamCymruScoutException(
                "Error while connecting to TeamCymruScout API: {}".format(err)
            )
        except Exception as err:
            applogger.error(
                self.error_logs.format(consts.LOGS_STARTS_WITH, __method_name, err)
            )
            raise TeamCymruScoutException()

    def send_data_to_sentinel(self, data, table_name):
        """
        To send the given data to the specified table in the Microsoft Sentinel.

        Args:
            data (Any): The data to be sent to the table.
            table_name (str): The name of the table in Microsoft Sentinel.
        """
        __method_name = inspect.currentframe().f_code.co_name
        applogger.debug(
            "{}(method={}) Sending data to Sentinel.".format(
                consts.LOGS_STARTS_WITH, __method_name
            )
        )
        body = json.dumps(data)
        self.ms_sentinel_obj.post_data(body, table_name)
        applogger.info(
            "{}(method={}) Posted {} records into {} of Log Analytics Workspace.".format(
                consts.LOGS_STARTS_WITH, __method_name, len(data), table_name
            )
        )
