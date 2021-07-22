import numpy as np
import torch
import torch.nn as nn
from matplotlib import pyplot as plt
from scipy.linalg import lstsq
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE" #I have some lib duplicates, this is to ignore this


class UnfoldPlainFit(nn.Module):
    """
    thx to https://gist.github.com/amroamroamro/1db8d69b4b65e8bc66a6
    """
    def __init__(self, kernel_size=3, stride=1, padding=1):
        super(UnfoldPlainFit, self).__init__()
        self.padding = padding
        self.stride = stride
        self.kernel_size = kernel_size

    def forward(self, x):
        x = torch.FloatTensor(x)
        data = x.reshape(1, 1, x.shape[0], x.shape[1])
        padded = nn.ReplicationPad2d(self.padding)(data)
        unf = padded.unfold(2, self.kernel_size, self.stride).unfold(3, self.kernel_size, self.stride)
        kernel_view = unf.contiguous().view(data.numel(), self.kernel_size * self.kernel_size)
        half_kernel_size = (self.kernel_size - 1) / 2
        space = np.arange(-half_kernel_size, half_kernel_size + 1, 1)
        X, Y = np.meshgrid(space, space)
        XX = X.flatten()
        YY = Y.flatten()
        cs = []
        for i, v in enumerate(kernel_view.contiguous()): # we can use multiprocessing here if needed
            A = np.c_[XX, YY, np.ones(v.numel())]
            C, _, _, _ = lstsq(A, v)
            cs.extend(C)
        cs = torch.FloatTensor(cs)
        out = cs.reshape(x.shape[0], x.shape[1], 3)
        return out


if __name__ == "__main__":
    # example
    data = [[2, 3, 4],
            [1, 2, 3],
            [0, 1, 2]]
    X, Y = np.meshgrid(np.arange(-1, 2, 1), np.arange(-1, 2, 1))
    XX = X.flatten()
    YY = Y.flatten()
    layer = UnfoldPlainFit()
    out = layer(data)

    C = out[1][1] # take the one not padded
    Z = C[0] * X + C[1] * Y + C[2]
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    surf = ax.plot_surface(X, Y, Z.detach().cpu().numpy(), rstride=1, cstride=1, alpha=0.2,
                    label='Fitted Plane')
    ax.scatter(X, Y, data, c='r', s=50,
                    label='data')
    surf._facecolors2d = ax._facecolor
    surf._edgecolors2d = ax._facecolor
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend()
    ax.set_zlabel('Z')
    ax.axis('tight')
    plt.show()
