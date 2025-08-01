# Copyright (c) 2025 Kandarpa Sarkar
# This file is part of the NeoNet project and is licensed under the MIT License.
# See the LICENSE file in the root directory for more information.

from neo._src.autograd import Node, Tape, TapeContext
from typing import Callable, List, Any
from neo._torch import neolib
from neo._torch.lite_tensor import LiteTensor

def rectify_shapes(val):
    return val.reshape(1) if val.ndim < 1 else val

def unpack_tuple(tup):
    return {f'x{i+1}': value for i, value in enumerate(tup)}

def if_xnary(grads):
    def _fix(g):
        if g.ndim == 0:
            return g.reshape(1)
        elif g.ndim == 1:
            return g[None, :]
        return g

    if isinstance(grads, tuple):
        return tuple(_fix(g) for g in grads)
    else:
        return _fix(grads)

# value_and_grad is responsible to calculate value alongwith the gradients of a function
def value_and_grad(fn: Callable, safe=False):
    def wrapped_function(args:list):
        import torch
        torch.set_grad_enabled(False)

        tape = Tape()
        TapeContext.push(tape)
        out = fn(*args)
        if not hasattr(out, 'data'):
            print(out)
            raise TypeError(
                f"value_and_grad expected `fn` to return a scalar-like LiteTensor, "
                f"but got {type(out)}: {out}"
        )
        TapeContext.pop()

        out_grad = neolib.ones_like(out.data)
        grad_dict = {id(out): out_grad}

        any_cuda = out_grad.is_cuda  

        for node in reversed(tape):
            node_out_id = id(node.output)
            node_out_grad = grad_dict.pop(node_out_id, None)
            if node_out_grad is None:
                continue

            grads = node.bwd_fn(grad=node_out_grad)

            node.output = None
            node.bwd_fn = None

            if grads is None:
                node.parents = None
                continue

            if not isinstance(grads, tuple):
                grads = (grads,)
            if len(grads) < len(node.parents):
                grads = grads + (None,) * (len(node.parents) - len(grads))

            for parent, grad in zip(node.parents, grads):
                if grad is None:
                    continue

                if grad.is_cuda:
                    any_cuda = True

                pid = id(parent)
                if pid in grad_dict:
                    grad_dict[pid].add_(grad.clone() if safe else grad)
                else:
                    grad_dict[pid] = grad.clone() if safe else grad

                del grad  

            node.parents = None 
            del node  

        input_grads = {}
        for arg in args:
            grad = grad_dict.get(id(arg))
            if grad is not None:
                input_grads[arg] = LiteTensor(grad)

        if any_cuda:
            torch.cuda.empty_cache()

        grads_list = list(input_grads.values())
        grad_out = grads_list[0] if len(grads_list) == 1 else grads_list

        return out, grad_out

    return wrapped_function

