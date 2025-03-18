# https://github.com/mit-han-lab/once-for-all/blob/master/ofa/nas/efficiency_predictor/latency_lookup_table.py

# Once for All: Train One Network and Specialize it for Efficient Deployment
# Han Cai, Chuang Gan, Tianzhe Wang, Zhekai Zhang, Song Han
# International Conference on Learning Representations (ICLR), 2020.

from typing import List, Tuple

class LatencyTable(object):
    def __init__(self, input_shape: Tuple[int, int]): 
        assert len(input_shape) == 2      # (H, W)  //  e.g., (224, 224)
        self.input_shape = input_shape

    @staticmethod
    def repr_shape(shape):
        if isinstance(shape, (list, tuple)):
            return "x".join(str(_) for _ in shape)
        elif isinstance(shape, str):
            return shape
        else:
            return TypeError

    def query(self):
        raise NotImplementedError

    def get_table_key_list(self):
        raise NotImplementedError