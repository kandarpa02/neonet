from neo._src.autograd import Policy
from ..math import neolib

class sum_op(Policy):
    def forward(self, x, dim=None, keepdim=False):
        self.ctx.save(x, dim, keepdim)
        return neolib.sum(x, dim=dim, keepdim=keepdim)

    def backward(self, grad):
        x, dim, keepdim = self.ctx.release
        if dim is None:
            dx = grad.expand(x.shape)
        else:
            if not keepdim:
                grad = neolib.unsqueeze(grad, dim=dim)
            dx = neolib.ones_like(x)
            dx *= grad 
        del self.ctx, x, dim, keepdim, grad
        return dx


class mean_op(Policy):
    def forward(self, x, dim=None, keepdim=False):
        self.ctx.save(x, dim, keepdim)
        return neolib.mean(x, dim=dim, keepdim=keepdim)

    def backward(self, grad):
        x, dim, keepdim = self.ctx.release
        size = neolib.prod(neolib.tensor(x.shape if dim is None else neolib.tensor(x.shape)[dim]))
        if dim is not None and not keepdim:
            grad = neolib.unsqueeze(grad, dim=dim)
        dx = neolib.ones_like(x)
        dx *= grad / size  
        del self.ctx, x, dim, keepdim, grad, size
        return dx


class max_op(Policy):
    def forward(self, x, dim=None, keepdim=False):
        out = neolib.max(x, dim=dim, keepdim=keepdim)
        self.ctx.save(x, out, dim, keepdim)
        return out
    def backward(self, grad):
        x, out, dim, keepdim = self.ctx.release
        if not keepdim and dim is not None:
            out = neolib.unsqueeze(out, dim=dim)
            grad = neolib.unsqueeze(grad, dim=dim)
        mask = x == out
        return grad * mask
