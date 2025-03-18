# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE
#  * file in the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import json
import typing
import functools

from stm32_api.file import FileManager
from stm32_api.benchmark.benchmark_service import BenchmarkService

from stm32_api.utils.errors import BenchmarkServerError
from stm32_api.utils.types import CliParameters, ValidateResultMetrics, BenchmarkResult, BoardData


class BenchmarkManager:
    def __init__(
        self,
        net,
        file_manager,
        path,
        stm_version="1.0.0", 
    ):
        self.net = net
        self.file_manager = file_manager
        self.benchmark_service = BenchmarkService(file_manager, stm_version)
        self.model_name = None
        self.bid_list = []
        version = stm_version

        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except Exception as e:
            print(e)

        self.path = path

        self.BENCHMARK_SERVICE_URL = 'https://stm32ai-cs.st.com/api/benchmark/benchmark/'
        self.headers = "'Authorization: Bearer " + self.file_manager.auth_token + "'"

        # version check
        if version != None and version not in list(map(lambda x: x['version'], self.benchmark_service.supportedVersions)):
            print(
                f'[WARN] Version {version} is not supported by Developer Cloud.')
            for v in self.benchmark_service.supportedVersions:    # 240910 
                if (v.get('isLatest', False) == True):
                    latest = v
            if (latest):
                self.version = latest.get('version', None)
                print(
                    f"[WARN] It will use the latest version by default ({latest['version']})")
                
        self.version = version


    def delete_result_given_id(self, benchmark_id):
        curl_command = "curl -X 'DELETE' " + "'" \
            + self.BENCHMARK_SERVICE_URL + benchmark_id \
            + "' " + "-H 'accept: application/json' " \
            + "-H " + self.headers
        os.system(curl_command)

        print(f'\nBenchmark result {benchmark_id} is deleted')


    def get_result_given_id(self, benchmark_id):
        if self.model_name is None:
            fname = benchmark_id + ".json"
        else:
            if self.model_name.endswith('.tflite'):
                fname = f'{self.model_name.split(".tflite")[0]}.json'
            elif self.model_name.endswith('.onnx'):
                fname = f'{self.model_name.split(".onnx")[0]}.json'
            elif self.model_name.endswith('.h5'):
                fname = f'{self.model_name.split(".h5")[0]}.json'
            else:
                fname = f'{self.model_name.split(".")[0]}.json'

        curl_command = "curl -X 'GET' " + "'" + self.BENCHMARK_SERVICE_URL + benchmark_id \
            + "' " + "-H 'accept: application/json' " \
            + "-H " + self.headers \
            + " | jq '.' > " + self.path + fname
        os.system(curl_command)

        print(f'Benchmark result is saved: {self.path}{fname}')


    def get_all_result(self):
        from datetime import datetime
        timestamp_format = "%Y%m%d_%H%M%S_%f"
        stamp = datetime.now().strftime(timestamp_format)

        all_result_name = "total_result_" + stamp
        curl_command = "curl -X 'GET' " + "'" + self.BENCHMARK_SERVICE_URL \
            + "' " + "-H 'accept: application/json' " \
            + "-H " + self.headers \
            + " | jq '.' > " + self.path + all_result_name + ".json"
        os.system(curl_command)

        print(f'All benchmark results are saved in {self.path}{all_result_name}.json')

        all_result_fname = all_result_name + ".json"

        return all_result_fname


    def get_latest_result(self, deletion=False):
        all_result = self.get_all_result()  

        # if deletion == True:    
        with open(self.path + all_result, 'r') as f:
            all_bench = json.load(f)

            benchmark_id_list = []
            for i in range(len(all_bench)):
                benchmark_id_list.append(all_bench[i]["benchmarkId"])

            latest_benchmark_id = benchmark_id_list[-1]

            if len(benchmark_id_list) > 1:
                if deletion is True:
                    old_benchmark_id_list = benchmark_id_list[:-1]
                    for old_benchmark_id in old_benchmark_id_list:
                        self.delete_result_given_id(old_benchmark_id)
            
            if (os.path.isfile(self.path + latest_benchmark_id + ".json") == False):
                self.get_result_given_id(latest_benchmark_id)
            else:
                print("Already saved latest benchmark result.")

    
    def get_benchmark_boards(self):
        out: typing.List[BoardData] = []
        boards_data = self.benchmark_service.list_boards()
        for k in boards_data.keys():
            out.append(BoardData(
                name=k,
                boardCount=boards_data[k].get('boardCount', -1),
                flashSize=boards_data[k].get('flashSize', ''),
                deviceCpu=boards_data[k].get('deviceCpu', ''),
                deviceId=boards_data[k].get('deviceId', '')))
        return out


    def benchmark(self, options: CliParameters, board_name: str, timeout=600, analysis=True):
        if os.path.exists(options.model):
            raise print("options.model should be a file name that is \
                already uploaded on the cloud")
        bid = self.benchmark_service.trigger_benchmark(options, board_name, self.version)
        print(f'Benchmark triggered with id {bid}')
        
        self.bid_list.append(bid)
        result = self.benchmark_service.wait_for_run(bid, timeout=timeout)

        if result:
            if analysis:
                report = result['report']
                validate_result_metrics = []
                for valmetrics in report['val_metrics']:
                    validate_result_metrics.append(ValidateResultMetrics(
                        accuracy=valmetrics['acc'],
                        description=valmetrics['desc'],
                        l2r=valmetrics['l2r'],
                        mae=valmetrics['mae'],
                        mean=valmetrics['mae'],
                        rmse=valmetrics['rmse'],
                        std=valmetrics['std'],
                        ts_name=valmetrics['ts_name']
                    ))
                graph = result['graph']
                exec_time = graph['exec_time']
                benchmark_result = BenchmarkResult(
                    rom_size=report['rom_size'],
                    macc=report['rom_n_macc'],
                    ram_size=report['ram_size'][0],
                    total_ram_io_size=functools.reduce(
                        lambda a, b: a+b,
                        result.get('report', {}).get('ram_io_size', 0), 0),
                    validation_metrics=validate_result_metrics,
                    validation_error=report['val_error'],
                    validation_error_description=report['val_error_desc'],
                    rom_compression_factor=report['rom_cfact'],
                    report_version=report['report_version'],
                    date_time=report['date_time'],
                    cli_version_str=report['cli_version_str'],
                    cli_parameters=report['cli_parameters'],
                    report=report,
                    graph=graph,
                    cycles=exec_time.get('cycles', -1),
                    duration_ms=exec_time.get('duration_ms', -1),
                    device=exec_time.get('device', ""),
                    cycles_by_macc=exec_time.get('cycles_by_macc', -1)
                )
                return benchmark_result
            else:
                return result
        else:
            raise BenchmarkServerError("Benchmark service return wrong format")
