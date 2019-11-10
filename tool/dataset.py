import numpy as np
import torch
import torch.utils.data as data
import os
from tool.SeqSampler import SeqBatchSampler

"""Dataset 和 Dataloader是torch中的一套工具，
继承并改造Dataset将数据进行必要的格式化，则Dataloader
才能用于从Dataset中load数据
"""


class PuncDataset(data.Dataset):
    """处理带标点的数据源

    superclass
    ----------
    data.Dataset :
        Dataset 是一个抽象类，用来表示数据集
    """
    def __init__(self, train_path, vocab_path, punc_path):
        # 检查文件是否存在
        print(train_path)
        assert os.path.exists(train_path), "train文件不存在"
        assert os.path.exists(vocab_path), "词典文件不存在"
        assert os.path.exists(punc_path), "标点文件不存在"

        self.word2id = load_vocab(
            vocab_path,
            extra_word_list=['<UNK>', '<END>']
        )
        self.id2word = {v: k for k, v in self.word2id.items()}
        self.punc2id = load_vocab(
            punc_path,
            extra_word_list=[" "]
        )
        self.id2punc = {k: v for (v, k) in self.punc2id.items()}

        tmp_seqs = open(train_path, encoding='utf-8').readlines()
        self.txt_seqs = [i for seq in tmp_seqs for i in seq.split()]
        # print(self.txt_seqs[:10])
        self.preprocess(self.txt_seqs)

    def __len__(self):
        """return txt文件中的句子数目
        """
        return self.in_len

    def __getitem__(self, index):
        """返回指定索引的张量对 (输入文本id的序列 , 其对应的标点id序列)

        Parameters
        ----------
        index : int
            索引
        """
        return self.in_id[index], self.label[index]

    def preprocess(self, txt_seqs: list):
        """将文本转为单词和应预测标点的id pair
        Parameters
        ----------
        txt : 文本
            文本每个单词跟随一个空格，符号也跟一个空格
        """
        in_id = []
        label = []
        punc = " "
        for token in txt_seqs:
            if token in self.punc2id:
                punc = token
            else:
                in_id.append(self.word2id.get(token, self.word2id["<UNK>"]))
                label.append(self.punc2id[punc])
                # 这个设计使得标点符号的下一个单词的label是标点符号，将符号两侧的知识加入到了网络中
                punc = " "
        in_id.append(self.word2id['<END>'])
        label.append(self.punc2id[punc])

        self.in_len = len(in_id) // 100
        len_tmp = self.in_len * 100
        in_id = in_id[:len_tmp]
        # dt = np.dtype('i8')
        self.in_id = torch.tensor(np.array(in_id, dtype='i8').reshape(-1, 100))
        label = label[:len_tmp]
        self.label = torch.tensor(np.array(label, dtype='i8').reshape(-1, 100))
        # print('last: ', self.in_id[-1])
        # print('len: ', self.in_len)


class NoPuncTextDataset(object):
    """parse text without punctuation
       - used by Inference.py
    Parameters
    ----------
    object : Inherited
        basic object.
    """

    def __init__(self, train_path, vocab_path, punc_path):



def collate_fn(data):
    input_seqs, label_seqs = zip(*data)


def load_vocab(vocab_path, extra_word_list=[], encoding='utf-8'):
    n = len(extra_word_list)
    with open(vocab_path, encoding='utf-8') as vf:
        vocab = {word.strip(): i+n for i, word in enumerate(vf)}
    for i, word in enumerate(extra_word_list):
        vocab[word] = i
    return vocab


def get_loader(train_path, vocab_path, punc_path, batch_size=1):
    """return the dataloader for loading data from own data file

    Parameters
    ----------
    train_path : str
        training data
    vocab_path : str
        vocab for all data
    punc_path : str
        punctuation set in data
    batch_size : int, optional
        batch_size for training, by default 1
    """
    print(train_path)
    dataset = PuncDataset(train_path, vocab_path, punc_path)
    SeqSampler = SeqBatchSampler(
        dataset.in_len,
        batch_size=batch_size
        )
    data_loader = data.DataLoader(
        dataset=dataset,
        shuffle=False,
        batch_sampler=SeqSampler
        )
    return data_loader