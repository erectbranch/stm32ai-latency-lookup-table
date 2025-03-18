# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE
#  * file in the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import json
import os
import typing
import time
import logging

from typing import Union

from stm32_api.file import FileManager
from stm32_api.helper import get_supported_versions

from stm32_api.utils import send_post, send_get
from stm32_api.utils import CliParameterVerbosity, CliParameters, AtonParametersSchema, CliParameterType, LOGGER_NAME

from stm32_api.utils import BenchmarkFailure, BenchmarkParameterError, ModelNotFoundError, WrongTypeError

logger = logging.getLogger(LOGGER_NAME)

class BenchmarkService:
    def __init__(self, file_manager: FileManager, version=None) -> None:
        self.file_manager = file_manager
        self.auth_token = file_manager.auth_token
        self.BENCHMARK_SERVICE_URL = 'https://stm32ai-cs.st.com/api/benchmark'
        self._use_stringify_args = False
        self.version = version

        # supported versions
        VERSIONS_URL = 'https://stm32ai-cs.st.com/assets/versions.json'
        self.supportedVersions = get_supported_versions(VERSIONS_URL)

    def trigger_benchmark(self, options: CliParameters, boardName: str, version: str = None):
        if type(options) != CliParameters:
            raise WrongTypeError('options should be an instance of CliParameters')

        def _build_arguments_dict(options: CliParameters):
            data = {}

            for field in options._fields:
                current_value = getattr(options, field)
                if field in ['model', 'output', 'atonnOptions'] or current_value is None:
                    continue
                if version:
                    data['version'] = version
                try: 
                    data[field] = current_value.value
                except Exception as _:
                    if current_value is not None:
                        data[field] = current_value
            if (hasattr(options, 'atonnOptions')):
                data['atonnOptions'] = AtonParametersSchema().dump(options.atonnOptions)
            return data
        
        model_name = options.model if options.model else None
        data = _build_arguments_dict(options)

        cloud_models_info = self.file_manager.upload_model_list()
        cloud_models = []
        for model in cloud_models_info:
            cloud_models.append(model['name'])
        
        if model_name not in cloud_models:
            raise ModelNotFoundError(f"model: {model_name} not found on cloud")

        if self._use_stringify_args:
            # Keeping "args" for compatilibity reason
            data_to_be_sent = {"args": json.dumps(data), "model": model_name}
        else:
            data_to_be_sent = data
            data_to_be_sent["model"] = model_name

        resp = send_post(
            f'{self.BENCHMARK_SERVICE_URL}/benchmark/{boardName.lower()}',    # TODO: 주소에 benchmark 두 번 중복
            withToken=self.auth_token,
            usingJson=data_to_be_sent)

        if resp.status_code == 200:
            json_resp = resp.json()
            resp.close()

            if 'benchmarkId' in json_resp:
                if 'model' not in json_resp:
                    logger.warning('No model confirmation in server response')
                if 'args' not in json_resp or \
                        not bool(resp.json().get('args')):
                    logger.warning('No args confirmation in server reponse')
                logger.debug(f'Triggering benchmark {json_resp}')
                return json_resp['benchmarkId']
            else:
                raise BenchmarkFailure("Error: server does not reply expected \
                    response")
        else:
            try:
                json_resp = resp.json()
                if 'errors' in json_resp:
                    raise BenchmarkParameterError(f"Wrong parameter: {json_resp.get('errors', None)}")
                else:
                    raise BenchmarkParameterError(f"Wrong parameter: {resp.text}")
            except json.JSONDecodeError:
                pass
            raise BenchmarkFailure(f"Error: server response code is {resp.status_code}")

    def _get_run(self, benchmarkId: str):
        resp = send_get(f"{self.BENCHMARK_SERVICE_URL}/benchmark/{benchmarkId}", 
                        self.auth_token)

        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 401:
            print("Error server reply: Unauthorized")
        else:
            print(f"Error server reply with non 200 HTTP code: \
                {resp.status_code}")
        return None

    def wait_for_run(self, benchmarkId: str, timeout=600, pooling_delay=2):
        """
            Wait for a benchmark run to be completed.
            If no result until timeoutit returns None
        """
        start_time = time.time()
        is_over = False
        self.benchmark_state = None
        while not is_over:
            if (time.time() - start_time) > timeout:
                is_over = True

            result = self._get_run(benchmarkId)
            if result:
                if isinstance(result, dict):
                    self.benchmark_state = result.get('state', '').lower()
                    if result.get('state', '').lower() == 'done':
                        return result
                    elif result.get('state', '').lower() == 'error':
                        logger.error(f'Benchmark return an error: {result}')
                        raise BenchmarkFailure(result.get('board', 'ND'),
                                               result.get('message', 'no info')
                                               )
                    elif result.get('state', '').lower() == 'waiting_for_build':
                        logger.debug(f'Benchmark({benchmarkId}) status: Project \
                            is waiting for build')
                    elif result.get('state', '').lower() == 'in_queue':
                        logger.debug(f'Benchmark({benchmarkId}) status: Model \
                            is in queue')
                    elif result.get('state', '').lower() == 'flashing':
                        logger.debug(f'Benchmark({benchmarkId}) status: \
                            Flashing remote board')
                    elif result.get('state', '').lower() == \
                            'generating_sources':
                        logger.debug(f'Benchmark({benchmarkId}) status: \
                            Generating sources')
                    elif result.get('state', '').lower() == \
                        'copying_sources':
                        logger.debug(f'Benchmark({benchmarkId}) status: \
                            Copying sources')
                    elif result.get('state', '').lower() == 'loading_sources':
                        logger.debug(f'Benchmark({benchmarkId}) status: \
                            Loading sources')
                    elif result.get('state', '').lower() == 'building':
                        logger.debug(f'Benchmark({benchmarkId}) status: \
                            Building sources')
                    elif result.get('state', '').lower() == 'validation':
                        logger.debug(f'Benchmark({benchmarkId}) status: \
                            Validating model')
                    else:
                        logger.warn(f"Unknown {result.get('state', '')} key \
                            received from server")
                else:
                    logger.error("Error: Message received from server is not \
                        an object: ", result)
                    return None

            time.sleep(pooling_delay)

    def list_boards(self) -> dict:
        resp = send_get(
            self.BENCHMARK_SERVICE_URL + '/boards',
            withToken=self.auth_token)

        if resp.status_code == 200:
            json_resp = resp.json()
            resp.close()
            return json_resp
        else:
            logger.error(f"Error: server response code is: {resp.status_code}")