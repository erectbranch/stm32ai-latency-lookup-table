# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE
#  * file in the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

class BACKEND_ENDPOINTS:
    STM32AI_SERVICE_URL = 'https://stm32ai-cs.st.com/api/stm32ai'
    # USER_SERVICE_URL = 'https://stm32ai-cs.st.com/api/user_service'
    # FILE_SERVICE_URL = 'https://stm32ai-cs.st.com/api/file'
    # BENCHMARK_SERVICE_URL = 'https://stm32ai-cs.st.com/api/benchmark'

    BASE_URL = 'https://stm32ai-cs.st.com/'
    USER_SERVICE_URL = 'https://stm32ai-cs.st.com/api/user_service'
    FILE_SERVICE_URL = 'https://stm32ai-cs.st.com/api/file'
    GENERATE_NBG_SERVICE_URL = 'https://stm32ai-cs.st.com/api/generate_nbg'
    BENCHMARK_SERVICE_URL = 'https://stm32ai-cs.st.com/api/benchmark'
    VERSIONS_URL = 'https://stm32ai-cs.st.com/assets/versions.json'
    SSO_URL = 'https://sso.st.com'
    CLIENTID = 'oidc_prod_client_app_stm32ai'
    CALLBACK_URL = 'https://stm32ai-cs.st.com/callback'

class BACKEND_TEST_ENDPOINTS:
    STM32AI_SERVICE_URL = 'https://stm32ai-cs-qa.st.com/api/stm32ai'
    # USER_SERVICE_URL = 'https://stm32ai-cs-qa.st.com/api/user_service'
    # FILE_SERVICE_URL = 'https://stm32ai-cs-qa.st.com/api/file'
    # BENCHMARK_SERVICE_URL = 'https://stm32ai-cs-qa.st.com/api/benchmark'

    BASE_URL = 'https://stm32ai-cs-qa.st.com/'
    USER_SERVICE_URL = 'https://stm32ai-cs-qa.st.com/api/user_service'
    FILE_SERVICE_URL = 'https://stm32ai-cs-qa.st.com/api/file'
    GENERATE_NBG_SERVICE_URL = 'https://stm32ai-cs-qa.st.com/api/generate_nbg'
    BENCHMARK_SERVICE_URL = 'https://stm32ai-cs-qa.st.com/api/benchmark'
    VERSIONS_URL = 'https://stm32ai-cs-qa.st.com/assets/versions.json'
    SSO_URL = 'https://qa-sso.st.com'
    CLIENTID = 'oidc_pre_prod_client_app'
    CALLBACK_URL = 'https://stm32ai-cs-qa.st.com/callback'

class BACKEND_EV_NAME:
    BASE_URL = "BASE_URL"
    STM32AI_SERVICE_URL = "STM32AI_SERVICE_URL"
    LOGIN_SERVICE_URL = "LOGIN_SERVICE_URL"
    USER_SERVICE_URL = "USER_SERVICE_URL"
    FILE_SERVICE_URL = "FILE_SERVICE_URL"
    GENERATE_NBG_SERVICE_URL = "GENERATE_NBG_SERVICE_URL"
    BENCHMARK_SERVICE_URL = "BENCHMARK_SERVICE_URL"
    VERSIONS_URL = 'VERSIONS_URL'
    SSO_URL = 'SSO_URL'
    CLIENTID = 'CLIENTID'
    CALLBACK_URL = 'CALLBACK_URL'
