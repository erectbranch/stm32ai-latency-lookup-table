import statistics
from typing import List, Dict

from latency_lookup_table.tables import LatencyTable, MBV2LatencyTable

TABLE_CLASS_INFO = {
    "mobilenetv2": MBV2LatencyTable,
}

def get_lookup_table_class(table_name: str) -> LatencyTable:
    return TABLE_CLASS_INFO[table_name]


def get_stats(lookup_table_list: List[Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    stats = {}
    for model_latency_table in lookup_table_list:
        for layer_name, latency in model_latency_table.items():
            if layer_name not in stats:
                stats[layer_name] = []
            stats[layer_name].append(latency)

    final_table = {}
    for layer_name, latencies in stats.items():
        final_table[layer_name] = {
            "count": len(latencies),
            "mean": statistics.mean(latencies),
            "std": statistics.stdev(latencies) if len(latencies) > 1 else 0,
        }

    return final_table