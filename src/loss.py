import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from torch.nn.modules.loss import _Loss, _WeightedLoss

    
class IOULoss(_WeightedLoss):
    """1 - jaccard index
    """

    def __init__(self, weight=None, size_average=True, reduce=True):
        weight = torch.tensor(weight).float()
        super(IOULoss, self).__init__(weight, size_average, reduce)

    def __call__(self, output, target):
        batch_size = output.size(0)
        channel = output.size(1)

        output = output.view(batch_size, channel, -1)
        target = (target == 1).float().view(batch_size, channel, -1)

        assert output.size() == target.size()
        assert (output <= 1).all() and (output >= 0).all()

        smooth = 1e-15

        intersection = (output * target).sum(dim=-1)
        union = output.sum(dim=-1) + target.sum(dim=-1)

        assert union.size()[0] == batch_size and intersection.size()[0] == batch_size

        union = union - intersection + smooth
        intersection = intersection + smooth

        loss = (1 - torch.div(intersection, union))

        if self.weight is not None:
            loss = loss * self.weight

        if not self.reduce:
            return loss.mean(dim=-1)
        elif self.size_average:
            return loss.mean()
        else:
            return loss.sum()

class DICELoss(_WeightedLoss):
    """ 1 - F1 score
    """

    def __init__(self, weight=None, size_average=True, reduce=True):
        if weight is not None:
            weight = torch.tensor(weight).float()
        super(DICELoss, self).__init__(weight, size_average, reduce)

    def __call__(self, output, target, reduce=True):
        batch_size = output.size(0)
        channel = output.size(1)

        output = output.view(batch_size, channel, -1)
        target = (target == 1).float().view(batch_size, channel, -1)

        assert output.size() == target.size()
        assert (output <= 1).all() and (output >= 0).all()

        smooth = 1e-15

        intersection = (output * target).sum(dim=-1)
        union = output.sum(dim=-1) + target.sum(dim=-1)

        assert union.size()[0] == batch_size and intersection.size()[0] == batch_size

        union = union + smooth
        intersection = intersection * 2 + smooth

        loss = (1 - torch.div(intersection, union))

        if self.weight is not None:
            loss = loss * self.weight
    
        if not self.reduce:
            return loss.mean(dim=-1)
        elif self.size_average:
            return loss.mean()
        else:
            return loss.sum()


class GANLoss(_WeightedLoss):
    
    def __init__(self, lsgan=False, weight=None, size_average=True, reduce=True):
        if weight is not None:
            weight = torch.tensor(weight).float()
        super(GANLoss, self).__init__(weight, size_average, reduce)
        self.lsgan = lsgan
        self.loss = nn.MSELoss(reduce=reduce) if lsgan else nn.BCEWithLogitsLoss(reduce=reduce)
    
    def __call__(self, output, target):
        if self.lsgan:
            output = F.sigmoid(output)
            return self.loss(output, target)
        else:
            return self.loss(output, target)