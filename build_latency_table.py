import argparse
import copy
import os
import json
import yaml

from typing import List, Dict

from latency_lookup_table.helper import get_lookup_table_class, get_stats

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=str, default="./.models/", help="model files already benchmarked")
    parser.add_argument("--result-dir", type=str, default="./.benchmark/", help="benchmark results on target MCU")

    parser.add_argument("--model-class", type=str, default="mobilenetv2", help="model file type")
    parser.add_argument("--model-type", type=str, default=".tflite", help="model file type")
    parser.add_argument("--input-shape", type=int, nargs=2, default=[160, 160], help="input shape of the model")

    parser.add_argument("--save-dir", type=str, default="./.lut/", help="save directory for latency table")
    return parser.parse_args()


def get_ops_from_benchmark(benchmark_file_path: str):
    with open(benchmark_file_path, "r") as f:
        benchmark = json.load(f)

    return benchmark['benchmark']['info']['graphs'][0]['nodes']


def main():
    args = parse_args()

    args.input_shape = tuple(args.input_shape)

    model_files   = [model_file for model_file in os.listdir(args.model_dir) if model_file.endswith(args.model_type)]
    model_configs = [model_file.replace(args.model_type, ".json") for model_file in model_files]
    benchmarked_results = [result_file for result_file in os.listdir(args.result_dir) if result_file.endswith(".json")]

    print(f"Found {len(model_configs)} model configs")
    print(f"Found {len(benchmarked_results)} benchmarked models")

    print(f'Warning: model config(.json) file name should be same as benchmarked result(.json) file name')

    lookup_table_class = get_lookup_table_class(args.model_class)
    table_builder = lookup_table_class(input_shape=args.input_shape)

    lookup_table_list = []

    for result_file in model_configs:
        print(f"{result_file} is being processed")

        with open(os.path.join(args.model_dir, result_file), "r") as f:
            config = json.load(f)
        
        table_key_list = table_builder.get_table_key_list(config)
        layer_to_ops = table_builder.get_opcode(table_key_list)

        ops_infos = get_ops_from_benchmark(os.path.join(args.result_dir, result_file))
        ops_infos.reverse()    # for pop() operation

        model_latency_table = {}

        for layer in table_key_list:
            layer_ops = copy.deepcopy(layer_to_ops[layer])
            layer_latency = 0.0

            while len(layer_ops) != 0:
                op_info = ops_infos.pop()
                op_name = op_info["description"]
                op_latency = op_info["exec_time"]["duration_ms"]

                layer_latency += op_latency
                if op_name == layer_ops[0]:
                    layer_ops.pop(0)

            model_latency_table[layer] = round(layer_latency, 4)

        lookup_table_list.append(model_latency_table)
    
    final_lookup_table = get_stats(lookup_table_list)

    with open(os.path.join(args.save_dir, "final_lookup_table.yaml"), "w") as f:
        yaml.dump(final_lookup_table, f, default_flow_style=False)
                

if __name__ == "__main__":
    main()