# https://github.com/mit-han-lab/once-for-all/blob/master/ofa/nas/efficiency_predictor/latency_lookup_table.py

# Once for All: Train One Network and Specialize it for Efficient Deployment
# Han Cai, Chuang Gan, Tianzhe Wang, Zhekai Zhang, Song Han
# International Conference on Learning Representations (ICLR), 2020.

from typing import List, Tuple

from latency_lookup_table.tables.base import LatencyTable
from latency_lookup_table.ops.mobilenetv2 import get_opcode

class MBV2LatencyTable(LatencyTable):
    def __init__(self, input_shape: Tuple[int, int]):
        super(MBV2LatencyTable, self).__init__(input_shape)

    def get_opcode(self, layer_infos: List[str]):
        return get_opcode(layer_infos)

    def query(
        self,
        l_type: str,
        input_shape,
        output_shape,
        expand=None,
        ks=None,
        stride=None,
        id_skip=None,
    ):
        infos = [
            l_type,
            "input:%s" % self.repr_shape(input_shape),
            "output:%s" % self.repr_shape(output_shape),
        ]

        if l_type in ("expanded_conv",):
            assert None not in (expand, ks, stride, id_skip)
            infos += [
                "expand:%d" % expand,
                "kernel:%d" % ks,
                "stride:%d" % stride,
                "idskip:%d" % id_skip,
            ]
        key = "-".join(infos)
        return key


    def get_table_key_list(self, cfg):   # config = subnet.config
        model_name = cfg["name"]
        key_list = []
        
        key_list.append(self.query(
            "Conv",
            [self.input_shape[0], self.input_shape[1], cfg["first_conv"]["in_channels"]],
            [(self.input_shape[0] + 1) // 2, (self.input_shape[1] + 1) // 2, cfg["first_conv"]["out_channels"]],
        ))
        # blocks
        fsize_1 = (self.input_shape[0] + 1) // 2
        fsize_2 = (self.input_shape[1] + 1) // 2
        for block in cfg["blocks"]:
            mb_conv = block["mobile_inverted_conv"]
            shortcut = block["shortcut"]

            if mb_conv is None:
                continue

            idskip = 0   if shortcut is None else 1

            out_fz_1 = int((fsize_1 - 1) / mb_conv["stride"] + 1)
            out_fz_2 = int((fsize_2 - 1) / mb_conv["stride"] + 1)

            if "mid_channels" in mb_conv:
                if mb_conv["mid_channels"] is None:
                    # _mid_channels = mb_conv["in_channels"] * mb_conv["expand_ratio"]
                    _mid_channels = mb_conv["out_channels"]
                else:
                    _mid_channels = mb_conv["mid_channels"]
                key_list.append(self.query(
                    "expanded_conv",
                    [fsize_1, fsize_2, mb_conv["in_channels"]],    
                    [out_fz_1, out_fz_2, mb_conv["out_channels"]],   
                    expand=_mid_channels,
                    ks=mb_conv["kernel_size"],
                    stride=mb_conv["stride"],
                    id_skip=idskip,
                ))
                _out_channels = mb_conv["out_channels"]
            else:
                raise NotImplementedError

            fsize_1 = out_fz_1
            fsize_2 = out_fz_2
            last_block_out_channels = _out_channels 

        avg_pool_channels = last_block_out_channels

        if cfg["feature_mix_layer"] is not None:
            key_list.append(self.query(
                "Conv_1",
                [fsize_1, fsize_2, cfg["feature_mix_layer"]["in_channels"]],
                [fsize_1, fsize_2, cfg["feature_mix_layer"]["out_channels"]],
            ))
            avg_pool_channels = cfg["feature_mix_layer"]["out_channels"]

        key_list.append(self.query(
            "AvgPool2D",
            [fsize_1, fsize_2, avg_pool_channels], 
            [1, 1, avg_pool_channels],
        ))
        
        # classifier
        key_list.append(self.query(
            "Logits", [1, 1, cfg["classifier"]["in_features"]], [cfg["classifier"]["out_features"]]
        ))
        return key_list