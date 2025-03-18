# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE
#  * file in the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import requests

from stm32_api.utils.http_requests import get_ssl_verify_status, get_env_proxy
from stm32_api.utils.endpoints import BACKEND_EV_NAME, BACKEND_ENDPOINTS, BACKEND_TEST_ENDPOINTS

USE_TEST_ROUTES_EV = 'USE_TEST_ROUTES'

def get_callback_url_ep():
    if os.environ.get(BACKEND_EV_NAME.CALLBACK_URL):
        return os.environ.get(BACKEND_EV_NAME.CALLBACK_URL)

    if os.environ.get(USE_TEST_ROUTES_EV):
        return BACKEND_TEST_ENDPOINTS.CALLBACK_URL
    else:
        return BACKEND_ENDPOINTS.CALLBACK_URL
        
def get_client_id_ep():
    if os.environ.get(BACKEND_EV_NAME.CLIENTID):
        return os.environ.get(BACKEND_EV_NAME.CLIENTID)

    if os.environ.get(USE_TEST_ROUTES_EV):
        return BACKEND_TEST_ENDPOINTS.CLIENTID
    else:
        return BACKEND_ENDPOINTS.CLIENTID

def get_sso_url_ep():
    if os.environ.get(BACKEND_EV_NAME.SSO_URL):
        return os.environ.get(BACKEND_EV_NAME.SSO_URL)

    if os.environ.get(USE_TEST_ROUTES_EV):
        return BACKEND_TEST_ENDPOINTS.SSO_URL
    else:
        return BACKEND_ENDPOINTS.SSO_URL
    
def get_supported_versions_ep():
    """
    Get supported versions on Dev. Cloud
    """
    if os.environ.get(BACKEND_EV_NAME.VERSIONS_URL):
        return os.environ.get(BACKEND_EV_NAME.VERSIONS_URL)

    if os.environ.get(USE_TEST_ROUTES_EV):
        return BACKEND_TEST_ENDPOINTS.VERSIONS_URL
    else:
        return BACKEND_ENDPOINTS.VERSIONS_URL

def get_login_service_ep():
    """
    Main route to access login features
    """

    if os.environ.get(BACKEND_EV_NAME.USER_SERVICE_URL):
        return os.environ.get(BACKEND_EV_NAME.USER_SERVICE_URL)

    if os.environ.get(USE_TEST_ROUTES_EV):
        return BACKEND_TEST_ENDPOINTS.USER_SERVICE_URL
    else:
        return BACKEND_ENDPOINTS.USER_SERVICE_URL

def get_login_authenticate_ep():
    """
    Route on which user check authentication status (GET)
    and authenticate (POST)
    """
    return get_login_service_ep() + '/authenticate'

def get_benchmark_service_ep():
    """
    Main route to access benchmark service
    """
    if os.environ.get(BACKEND_EV_NAME.BENCHMARK_SERVICE_URL):
        return os.environ.get(BACKEND_EV_NAME.BENCHMARK_SERVICE_URL)

    if os.environ.get(USE_TEST_ROUTES_EV):
        return BACKEND_TEST_ENDPOINTS.BENCHMARK_SERVICE_URL
    else:
        return BACKEND_ENDPOINTS.BENCHMARK_SERVICE_URL

####################################################################################################

def get_supported_versions(toUrl: str=None):
    resp = requests.get(
        get_supported_versions_ep(),
        verify=get_ssl_verify_status(),
        proxies=get_env_proxy())
    return resp.json()