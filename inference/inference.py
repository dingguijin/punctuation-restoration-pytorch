import io
import sys

import numpy as np
import torch
from torch.autograd import Variable

from data.dataset import NoPuncTextDataset
from various_punctuator import LSTMPPunctuator
from utils import add_punc_to_txt

# Change the standard out encoding to utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def main(args):
    dataset = NoPuncTextDataset()


