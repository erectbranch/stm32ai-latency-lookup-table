# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE
#  * file in the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import requests
import os
import urllib3

from requests.structures import CaseInsensitiveDict

def get_env_proxy():
    proxy_config = {}
    http_proxy = "http://user:passwd@ip_address:port"
    https_proxy = "https://user:passwd@ip_address:port"
    if http_proxy != None:
        proxy_config['http_proxy'] = http_proxy
    if https_proxy != None:
        proxy_config['https_proxy'] = https_proxy
    proxy_config = proxy_config if len(proxy_config) else None
    return proxy_config


def get_ssl_verify_status():
    if os.environ.get('NO_SSL_VERIFY'):
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        return False
    else:
        return True


def send_post(
        toUrl: str,
        withToken: str,
        usingData: dict = None,
        usingFile: dict = None,
        usingJson=None) -> requests.Response:
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = f"Bearer {withToken}"

    resp = requests.post(
        toUrl,
        headers=headers,
        verify=get_ssl_verify_status(),
        data=usingData,
        files=usingFile,
        json=usingJson,
        proxies=get_env_proxy())
    return resp


def send_delete(toUrl: str, withToken: str) -> requests.Response:
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = f"Bearer {withToken}"

    resp = requests.delete(
        toUrl,
        headers=headers,
        verify=get_ssl_verify_status(),
        proxies=get_env_proxy())
    return resp


def send_get(
        toUrl: str,
        withToken: str,
        usingParams: dict = None) -> requests.Response:
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = f"Bearer {withToken}"

    resp = requests.get(
        toUrl,
        headers=headers,
        verify=get_ssl_verify_status(),
        params=usingParams,
        proxies=get_env_proxy())

    if resp.status_code == 404:
        raise print(f"ServerRouteNotFound: Trying to reach: {toUrl}")
    return resp