import torch
from typing import Any, Callable
from torch.optim import (
    SGD as _SGD,
    Adam as _Adam,
    AdamW as _AdamW,
    Adadelta as _Adadelta,
    Adagrad as _Adagrad,
    Adamax as _Adamax,
    ASGD as _ASGD,
    LBFGS as _LBFGS,
    NAdam as _NAdam,
    RAdam as _RAdam,
    RMSprop as _RMSprop,
    Rprop as _Rprop
)

class NeoOptimizer:
    def __init__(self, params: dict[Any, Any], torch_opt_cls: Callable, **kwargs):
        self.params = params
        self.torch_params = [torch.nn.Parameter(p.data.detach().clone().requires_grad_()) for p in params.values()]

        self._param_map = dict(zip(params.keys(), self.torch_params))

        self.optimizer = torch_opt_cls(self.torch_params, **kwargs)

    def step(self, grads: list) -> dict[Any, Any]:
        grads_d = {}
        for key, value in zip(self._param_map.keys(), grads):
            grads_d[key] = value.data

        for key, torch_p in self._param_map.items():
            grad = grads_d.get(key, None)
            if grad is not None:
                if grad.shape != torch_p.shape:
                    grad = grad.expand_as(torch_p)
                torch_p.grad = grad

        self.optimizer.step()
        self.optimizer.zero_grad()

        for key, torch_p in self._param_map.items():
            self.params[key].data.copy_(torch_p.data)  

        return self.params



class SGD(NeoOptimizer):
    def __init__(self, params, **kwargs):
        super().__init__(params, _SGD, **kwargs)

class Adam(NeoOptimizer):
    def __init__(self, params, **kwargs):
        super().__init__(params, _Adam, **kwargs)

class AdamW(NeoOptimizer):
    def __init__(self, params, **kwargs):
        super().__init__(params, _AdamW, **kwargs)

class Adadelta(NeoOptimizer):
    def __init__(self, params, **kwargs):
        super().__init__(params, _Adadelta, **kwargs)

class Adagrad(NeoOptimizer):
    def __init__(self, params, **kwargs):
        super().__init__(params, _Adagrad, **kwargs)

class Adamax(NeoOptimizer):
    def __init__(self, params, **kwargs):
        super().__init__(params, _Adamax, **kwargs)

class ASGD(NeoOptimizer):
    def __init__(self, params, **kwargs):
        super().__init__(params, _ASGD, **kwargs)

class LBFGS(NeoOptimizer):
    def __init__(self, params, **kwargs):
        super().__init__(params, _LBFGS, **kwargs)

class NAdam(NeoOptimizer):
    def __init__(self, params, **kwargs):
        super().__init__(params, _NAdam, **kwargs)

class RAdam(NeoOptimizer):
    def __init__(self, params, **kwargs):
        super().__init__(params, _RAdam, **kwargs)

class RMSprop(NeoOptimizer):
    def __init__(self, params, **kwargs):
        super().__init__(params, _RMSprop, **kwargs)

class Rprop(NeoOptimizer):
    def __init__(self, params, **kwargs):
        super().__init__(params, _Rprop, **kwargs)
