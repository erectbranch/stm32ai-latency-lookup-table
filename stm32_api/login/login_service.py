# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE
#  * file in the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

from json import JSONDecodeError, dump, load
import requests
from typing import Union
import html
import re
from urllib.parse import urlparse, parse_qs, urljoin
import os
import sys
import time
from pathlib import Path

from stm32_api.helper import *

class LoginService:
    def __init__(self) -> None:
        self.token_file = Path.joinpath(Path.home(), '.stmai_token')
        self.main_route = get_login_service_ep()

        self.authenticate_route = get_login_authenticate_ep()
        self.auth_token = None

    def read_token_from_storage(self) -> Union[dict, None]:
        if (os.path.exists(self.token_file) == False):
            return None
        f = open(self.token_file, 'r')
        token = load(f)
        return token
    
    def save_token_response(self, token) -> bool:
        with open(self.token_file, 'w') as f:
            dump(token, f)

    def login(self, username, password) -> str:
        for i in range(5):
            try:
                self._login(username, password)
                return self.auth_token
            except InvalidCrendetialsException as e:
                raise e
            except BlockedAccountException as e:
                raise e
            except Exception as e:
                print('Login issue, retry (' + str(i+1) + '/5)')
                time.sleep(5)

    def _login(self, username, password) -> str:
        # Starts a requests sesson
        s = requests.session()
        s.proxies = get_env_proxy()
        s.verify = get_ssl_verify_status()
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv59.0) Gecko/20100101',
        })

        provider = get_sso_url_ep()
        client_id = get_client_id_ep()
        redirect_uri = get_callback_url_ep()

        # Get connection initialization procedure
        resp = s.get(
            url=provider + "/as/authorization.oauth2",
            params={
                "response_type": "code",
                "client_id": client_id,
                "scope": "openid",
                "redirect_uri": redirect_uri,
                "response_mode": "query"
            },
            allow_redirects=True,
        )

        # Continue through my.st.com website
        # resp = s.get(
        #     url=resp.headers["Location"],
        #     allow_redirects=True,
        # )

        page = resp.text

        # Find POST URL
        form_action = html.unescape(
            re.search('<form\s+.*?\s+action="(.*?)"', page, re.DOTALL).group(1))

        # Find LT value. This is required by my.st.com in order to perform login
        lt_value = html.unescape(
            re.search('<input.*name="lt".*value="(.*)" />', page).group(1))

        parsed_url = urlparse(resp.url)
        # Construct Login URL = https://my.st.com/cas/login/......
        login_url = urljoin(parsed_url.scheme + "://" +
                            parsed_url.netloc, form_action)
        resp = s.post(
            url=login_url,
            data={
                "username": username,
                "password": password,
                "_eventId": "Login",
                "lt": lt_value
            },
            allow_redirects=False,
        )

        if (resp.status_code == 200):
            failure_regex = re.search(r'You have provided the wrong password. You have \d+ attempts left after which your account password will expire.', resp.text)
            if (failure_regex):
                raise InvalidCrendetialsException
            blocked_regex = re.search(r'You have exceeded 5 login attempts. Please click below on Forgot Password to set a new one.', resp.text)
            if (blocked_regex):
                raise BlockedAccountException

        redirect = resp.headers['Location']
        is_ready = False
        while is_ready == False:
            resp = s.get(
                url=redirect,
                allow_redirects=False,
            )
            status_code = resp.status_code
            # While redirection, follow redirect, until redirection starts with our needed URL (stm32ai-cs.st.com)
            if status_code == 302:
                redirect = resp.headers['Location']
                is_ready = redirect.startswith(redirect_uri)
            else:
                is_ready = True

        # Retrieve params from redirect URL
        query = urlparse(redirect).query
        redirect_params = parse_qs(query)

        # Expect to have a "code" value in this redirection. We won't follow the redirect but we will instead do manually thre request
        auth_code = redirect_params['code'][0]

        # Get tokens with POST endpoint

        resp = s.post(
            url='https://stm32ai-cs.st.com/api/user_service/login/callback',
            data={
                "redirect_url": redirect_uri,
                "code": auth_code
            },
            allow_redirects=False,
            verify=get_ssl_verify_status(),
            proxies=get_env_proxy(),
        )

        # Response should be 200
        assert (resp.status_code == 200)

        # Token is stored in response as JSON
        try:
            json_resp = resp.json()
            if json_resp['access_token']:
                # Connection has correctly been done, continue
                self.save_token_response(json_resp)
                self.auth_token = json_resp['access_token']
                return self.auth_token
            else:
                raise LoginFailureException(
                    self.username, self.password, details=f"Authentication server did not succeed: {resp}")
        except JSONDecodeError as e:
            raise LoginFailureException(
                self.username, self.password, 'Error while decoding server reply')
