# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE
#  * file in the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import requests
import os

from datetime import datetime
from stm32_api.login import LoginManager
from stm32_api.utils import send_post, send_delete, send_get


class FileManager(LoginManager):
    def __init__(self, username: str, password: str):
        super().__init__(username, password)

        self.MODEL_FILE_URL = 'https://stm32ai-cs.st.com/api/file/files/models'
        self.headers = "'Authorization: Bearer " + self.auth_token + "'" + "Content-type: multipart/form-data"


    def upload_model(self, file_path: str, model_name: str):
        if file_path is None:
            raise Exception('Please specify the model file path')
        
        if model_name is None:
            raise Exception('Please specify the model file name')

        try:
            # with open(file_path, 'rb') as f:
            #     files = {"file": f}
            files = {'file': open(file_path, 'rb')}
            resp = send_post(
                toUrl = self.MODEL_FILE_URL,
                withToken = self.auth_token,
                usingFile = files
            )

            if resp.status_code == 200:
                print(f'Success: the model file({model_name}) is uploaded')
            else:
                print(f'Failed to upload the model file ({model_name})')
                print(resp.text)
        except Exception as e:
            print(e)


    def delete_model(self, model_name: str):
        DELETE_MODEL_URL = self.MODEL_FILE_URL + '/' + model_name

        try:
            resp = send_delete(
                toUrl = DELETE_MODEL_URL,
                withToken = self.auth_token,
            )

            if resp.status_code == 200:
                print(f'Success: the model file({model_name}) is deleted')
            else:
                print(f'Failed to delete model file {model_name}')
                print(resp.text)
        except Exception as e:
            print(e)


    def upload_model_list(self):
        resp = send_get(toUrl=self.MODEL_FILE_URL, withToken=self.auth_token)
        json_resp = resp.json()
        resp.close()

        if isinstance(json_resp, list):
            return json_resp
        else:
            return None


    def get_cloud_model_list(self, path):
        if path is None:
            path = "~/.cloud/"
            path = os.path.expanduser(path)

        timestamp_format = "%Y%m%d_%H%M%S_%f"
        stamp = datetime.now().strftime(timestamp_format)

        try:
            if not os.path.exists(path):
                os.makedirs(path)
            # curl을 이용해서 현재 스토리지에 있는 모델 리스트 응답을 받고 json 저장
            curl_command = "curl -X 'GET' " + "'" + self.MODEL_FILE_URL \
                + "' " + "-H 'accept: application/json' " \
                + "-H " + self.headers \
                + "'" + " | jq '.' > " + path + stamp + ".json"
            os.system(curl_command)

            print(f'Cloud model list is saved in {path}/{stamp}.json')
        except Exception as e:
            print(e)
