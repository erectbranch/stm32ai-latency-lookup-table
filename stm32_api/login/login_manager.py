# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE
#  * file in the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

from stm32_api.login.login_service import LoginService
from stm32_api.utils.errors import LoginFailureException

class LoginManager:
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self.login_service = LoginService()

        if username is None or password is None:
            raise LoginFailureException(
                username,
                password,
                details='Empty login or stored token invalid.')
        else:
            self.auth_token = self.login_service.login(username=username, password=password)

        if self.auth_token is None:
            raise LoginFailureException(
                username,
                password,
                details='Please check your credentials')
        
    def get_token(self):
        return self.auth_token
    
    def __repr__(self):
        return f'STM32Cube.AI Developer Cloud Backend. Username: {self.username}'