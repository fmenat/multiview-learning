import numpy as np
import torch
from typing import List, Union, Dict

class Lambda(torch.nn.Module):
    "An easy way to create a pytorch layer for a simple `func`."
    def __init__(self, func):
        "create a layer that simply calls `func` with `x`"
        super().__init__()
        self.func=func
    def forward(self, x): return self.func(x)

def detach_all(z):
    if isinstance(z, dict):
        z_ = {}
        for k, v in z.items():
            z_[k] = detach_all(v)
        z = z_
    elif isinstance(z, list):
        z = [z_.detach().cpu().numpy() for z_ in z]
    else:
        z = z.detach().cpu().numpy()
    return z

def collate_all_list(z, z_):
    if isinstance(z_, dict):
        for k, v in z_.items():
            collate_all_list(z[k], v)
    elif isinstance(z_,list):
        for i, z_i in enumerate(z_):
            z[i].append( z_i )
    else:
        z.append(z_) 

def object_to_list(z):
    if isinstance(z, dict):
        for k, v in z.items():
            z[k] = object_to_list(v)
        return z
    elif isinstance(z,list):
        return [ [z_i] for z_i in z]
    else:
        return [z]

def stack_all(z_list, data_type = "numpy"):
    if isinstance(z_list, dict):
        for k, v in z_list.items():
            z_list[k] = stack_all(v, data_type=data_type)
    elif isinstance(z_list[0], list):
        for i, v in enumerate(z_list):
            z_list[i] = stack_all(v, data_type=data_type)
    elif isinstance(z_list, list):
        if data_type == "numpy":
            z_list = np.concatenate(z_list, axis = 0)
        elif data_type == "torch":
            z_list = torch.concat(z_list, axis = 0)
    else:
        print(type(z_list))
        pass
    return z_list

def get_dic_emb_dims(encoders: Dict[str,torch.nn.Module], emb_dims: Union[int, List[int], Dict[str,int]]=0) -> dict:
    return_emb_dims = {}
    for i,  view_name in enumerate(encoders):
        if hasattr(encoders[view_name], "get_output_size"):
            return_emb_dims[view_name] = encoders[view_name].get_output_size()
        else:
            if type(emb_dims) == int:
                return_emb_dims[view_name] = emb_dims
            elif type(emb_dims) == list:
                return_emb_dims[view_name] = emb_dims[i]
            elif type(emb_dims) == dict:
                return_emb_dims[view_name] = emb_dims[view_name]
            else: 
                raise Exception("if the encoders do not have the method 'get_output_size', please indicate it on the init of this class, as emb_dims=list or int")
    return return_emb_dims 