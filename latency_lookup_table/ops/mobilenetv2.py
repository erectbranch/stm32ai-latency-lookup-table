from typing import List, Dict

STM_OP_DICT = {
    "Conv": ["Conv2D", "Pad"],  
    "block0": ["Conv2D", "Conv2D"],
    "expanded_conv-stride:1-idskip:0": ["Conv2D", "Conv2D", "Conv2D"],
    "expanded_conv-stride:2-idskip:0": ["Conv2D", "Conv2D", "Conv2D"],
    "expanded_conv-stride:1-idskip:1": ["Conv2D", "Conv2D", "Conv2D", "Eltwise"],
    "Conv_1": ["Conv2D"],   
    "AvgPool2D": ["Pool"],
    "Logits": ["Conv2D"],
}

# layer name -> MCU operator name
def get_opcode(layer_infos: List[str]) -> Dict[str, List[str]]:
    ops_dict = STM_OP_DICT

    layer_to_ops = {}
    block_idx = 0

    for layer_info in layer_infos:
        layer_type = layer_info.split("-")[0]       # "Conv", "block0", "expanded_conv-idskip:0-se:0", ...

        if "expanded_conv" in layer_type:
            if block_idx == 0:    # block0
                layer_to_ops[layer_info] = ops_dict["block0"]
                block_idx += 1
                continue
            stride = layer_info.split("-")[-2]
            idskip = layer_info.split("-")[-1]
            layer_type = f'{layer_type}-{stride}-{idskip}'

        layer_to_ops[layer_info] = ops_dict[layer_type]
    return layer_to_ops