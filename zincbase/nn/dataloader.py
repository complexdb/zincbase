import dill
import numpy as np
import torch
from torch.utils.data import Dataset

class NegDataset(Dataset):
    """Zincbase sets this up automatically from the knowledge base.
    It's a generator used for negative examples.
    """
    def __init__(self, neg_triples):
        self.triples = neg_triples
        self.len = len(neg_triples)
    def __len__(self):
        return self.len
    def __getitem__(self, idx):
        t = self.triples[idx]
        return torch.LongTensor(t), torch.LongTensor([[0., 0., 0.]]), torch.FloatTensor([0.]), 'neg', False

class TrainDataset(Dataset):
    """Zincbase sets this up automatically from the knowledge base.
    It's the generator for the RotatE algorithm.
    """

    def __init__(self, triples, nrelation, negative_sample_size, mode):
        self.len = len(triples)
        self.triples = triples
        self.nrelation = nrelation
        self.negative_sample_size = negative_sample_size
        self.mode = mode
        self.count = self.count_frequency(triples)
        self.true_head, self.true_tail = self.get_true_head_and_tail(self.triples)
        self.true_attr = self.get_true_attr(self.triples)
        self.nentity = len(self.true_attr)

    def __len__(self):
        return self.len

    def __getitem__(self, idx):
        positive_sample = self.triples[idx]

        head, relation, tail, attr, true = positive_sample

        subsampling_weight = self.count[(head, relation)] + self.count[(tail, -relation - 1)]
        subsampling_weight = torch.sqrt(1 / torch.Tensor([subsampling_weight]))

        negative_sample_list = []
        negative_sample_size = 0
        # This is not really 'negative samples' but rather a list of head/tails that dont appear
        # with the other part of the tuple
        while negative_sample_size < self.negative_sample_size:
            negative_sample = np.random.randint(self.nentity, size=self.negative_sample_size*2)
            if self.mode == 'head-batch':
                mask = np.in1d(
                    negative_sample, 
                    self.true_head[(relation, tail)], 
                    assume_unique=True, 
                    invert=True
                )
            elif self.mode == 'tail-batch':
                mask = np.in1d(
                    negative_sample, 
                    self.true_tail[(head, relation)], 
                    assume_unique=True, 
                    invert=True
                )
            else:
                raise ValueError('Training batch mode %s not supported' % self.mode)
            negative_sample = negative_sample[mask]
            negative_sample_list.append(negative_sample)
            negative_sample_size += negative_sample.size
        
        negative_sample = np.concatenate(negative_sample_list)[:self.negative_sample_size]
        negative_sample = torch.from_numpy(negative_sample).float()

        tmp = [positive_sample[0], positive_sample[1], positive_sample[2]]
        for item in positive_sample[3:]:
            if isinstance(item, list) or isinstance(item, tuple):
                for subitem in item:
                    tmp.append(subitem)
            else:
                tmp.append(item)
        positive_sample = tmp
        positive_sample = torch.LongTensor(positive_sample) #TODO First 3 needs to be a longtensor, after that should be floats
        return positive_sample, negative_sample, subsampling_weight, self.mode, true

    @staticmethod
    def collate_fn(data):
        positive_sample = torch.stack([_[0] for _ in data], dim=0)
        negative_sample = torch.stack([_[1] for _ in data], dim=0)
        subsample_weight = torch.cat([_[2] for _ in data], dim=0)
        mode = data[0][3]
        true = data[0][4]
        return positive_sample, negative_sample, subsample_weight, mode, true

    @staticmethod
    def count_frequency(triples, start=4):
        count = {}
        for head, relation, tail, attr, true in triples:
            if (head, relation) not in count:
                count[(head, relation)] = start
            else:
                count[(head, relation)] += 1

            if (tail, -relation-1) not in count:
                count[(tail, -relation-1)] = start
            else:
                count[(tail, -relation-1)] += 1
        return count

    @staticmethod
    def get_true_attr(triples):
        true_attr = {}
        for head, relation, tail, attr, true in triples:
            true_attr[head] = attr
        return true_attr

    @staticmethod
    def get_true_head_and_tail(triples):

        true_head = {}
        true_tail = {}

        for head, relation, tail, attr, true in triples:
            if (head, relation) not in true_tail:
                true_tail[(head, relation)] = []
            true_tail[(head, relation)].append(tail)
            if (relation, tail) not in true_head:
                true_head[(relation, tail)] = []
            true_head[(relation, tail)].append(head)

        for relation, tail in true_head:
            true_head[(relation, tail)] = np.array(list(set(true_head[(relation, tail)])))
        for head, relation in true_tail:
            true_tail[(head, relation)] = np.array(list(set(true_tail[(head, relation)])))

        return true_head, true_tail

class BidirectionalIterator(object):
    """ZincBase uses this class automatically when you want to train a model from a KB.
    """
    def __init__(self, dataloader_head, dataloader_tail, dataloader_neg=None, neg_ratio=1):
        self.iterator_head = self.one_shot_iterator(dataloader_head)
        self.iterator_tail = self.one_shot_iterator(dataloader_tail)
        self.neg = False
        if dataloader_neg:
            self.neg = True
            self.neg_ratio = neg_ratio
            self.iterator_neg = self.one_shot_iterator(dataloader_neg)
        self.step = 0

    def __next__(self):
        if self.neg:
            return self.next_with_neg()
        return self.next_no_neg()

    def next_with_neg(self):
        self.step += 1
        if self.step % self.neg_ratio == 0:
            data = next(self.iterator_neg)
        elif self.step % 2 == 0:
            data = next(self.iterator_head)
        else:
            data = next(self.iterator_tail)
        return data

    def next_no_neg(self):
        self.step += 1
        if self.step % 2 == 0:
            data = next(self.iterator_head)
        else:
            data = next(self.iterator_tail)
        return data

    @staticmethod
    def one_shot_iterator(dataloader):
        while True:
            for data in dataloader:
                yield data

class RedisGraph(Dataset):
    def __init__(self, kb, mode, node_attributes=[], pred_attributes=[], negative_sample_size=2):
        self.kb = kb
        self.negative_sample_size = negative_sample_size
        self.it = self.kb.redis.scan_iter('*__edge')
        self.node_count = self.kb.redis.scard('node_set')
        self.relation_count = self.kb.redis.scard('edge_set')
        self.node_attributes = node_attributes
        self.pred_attributes = pred_attributes
        self.true_head, self.true_tail = {}, {}
        self.true_head_np, self.true_tail_np = {}, {}
        self.mode = mode
        
    def __getitem__(self, idx):
        return self.__next__()

    def __len__(self):
        return len(self.kb.redis.keys('*__edge'))

    def __next__(self):
        edge_key = next(self.it)
        edge = dill.loads(self.kb.redis.get(edge_key))
        if edge.pred not in self.kb._relation2id:
            self.kb._relation2id[edge.pred] = self.kb._seen_relations
            self.kb._seen_relations += 1
        sub, ob = edge.nodes
        if sub._name not in self.kb._entity2id: # todo use a set for this check instead.
            #self.kb._entity2id[sub._name] = self.kb._seen_nodes
            self.kb._add_entity(sub._name, self.kb._seen_nodes)
            self.kb._seen_nodes += 1
        if ob._name not in self.kb._entity2id:
            self.kb._add_entity(ob._name, self.kb._seen_nodes)
            #self.kb._entity2id[ob._name] = self.kb._seen_nodes
            self.kb._seen_nodes += 1
        truthiness = edge.get('truthiness', False)
        is_neg = truthiness and truthiness < 0
        attrs = []
        for attribute in self.node_attributes:
            attr_sub = float(sub.attrs.get(attribute, 0.0))
            attr_ob = float(ob.attrs.get(attribute, 0.0)) # wasnt there before! should be!
            attrs += [attr_sub, attr_ob]
        for pred_attr in self.pred_attributes:
            if pred_attr == 'truthiness':
                default_value = 1.
            else:
                default_value = 0.
            attr = float(edge.attrs.get(pred_attr, default_value))
            attrs.append(attr)

        triple = (self.kb._entity2id[sub._name], self.kb._relation2id[edge.pred],
                  self.kb._entity2id[ob._name], attrs, is_neg)
        
        #print(len(self.count))
        start = 4 # magic
        # The below subsampling ratio will get more accurate
        # over time.
        oh_one = str(triple[0]) + '___' + str(triple[1]) + '___count'
        if not self.kb.redis.get(oh_one): #(triple[0], triple[1]) not in self.count:
            #self.count[(triple[0], triple[1])] = start
            self.kb.redis.set(oh_one, start)
        else:
            self.kb.redis.incr(oh_one, amount=1)
            # self.count[(triple[0], triple[1])] += 1

        two_one = str(triple[2]) + '___' + str(-triple[1]-1) + '___count'
        if not self.kb.redis.get(two_one): #two_one not in self.count:
            #self.count[(triple[2], -triple[1]-1)] = start
            self.kb.redis.set(two_one, start)
        else:
            self.kb.redis.incr(two_one, amount=1)
            #self.count[(triple[2], -triple[1]-1)] += 1

        #subsampling_weight = self.count[(triple[0], triple[1])] + self.count[(triple[2], -triple[1]-1)]
        subsampling_weight = int(self.kb.redis.get(oh_one)) + int(self.kb.redis.get(two_one))
        subsampling_weight = torch.sqrt(1 / torch.Tensor([subsampling_weight]))

        negative_sample_list = []

        # The accuracy of these will get better over time.
        # TODO init these as defaultdict(list)
        head, relation, tail = triple[:3]
        if (head, relation) not in self.true_tail:
            self.true_tail[(head, relation)] = []
        self.true_tail[(head, relation)].append(tail)
        if (relation, tail) not in self.true_head:
            self.true_head[(relation, tail)] = []
        # TODO this seems suboptimal, true_head/tail should be a set
        self.true_head[(relation, tail)].append(head)

        # TODO only recalculate these if something changed above.
        for relation, tail in self.true_head:
            self.true_head_np[(relation, tail)] = np.array(list(set(self.true_head[(relation, tail)])))
        for head, relation in self.true_tail:
            self.true_tail_np[(head, relation)] = np.array(list(set(self.true_tail[(head, relation)])))

        negative_sample_size = 0
        while negative_sample_size < self.negative_sample_size:
            negative_sample = np.random.randint(len(self.kb._entity2id), size=self.negative_sample_size*2)
            if self.mode == 'head-batch':
                if (relation, tail) not in self.true_head_np:
                    list_true = []
                else:
                    list_true = self.true_head_np[(relation, tail)]
                mask = np.in1d(
                    negative_sample, 
                    list_true, 
                    assume_unique=True, 
                    invert=True
                )
            elif self.mode == 'tail-batch':
                if (head, relation) not in self.true_head_np:
                    list_true = []
                else:
                    list_true = self.true_head_np[(head, relation)]
                mask = np.in1d(
                    negative_sample, 
                    list_true, 
                    assume_unique=True, 
                    invert=True
                )
            else:
                raise ValueError('Training batch mode %s not supported' % self.mode)
            negative_sample = negative_sample[mask]
            negative_sample_list.append(negative_sample)
            negative_sample_size += negative_sample.size
        
        negative_sample = np.concatenate(negative_sample_list)[:self.negative_sample_size]
        negative_sample = torch.from_numpy(negative_sample).float()

        tmp = [head, relation, tail]
        for item in triple[3:]:
            if isinstance(item, list) or isinstance(item, tuple):
                for subitem in item:
                    tmp.append(subitem)
            else:
                tmp.append(item)
        positive_sample = tmp
        positive_sample = torch.LongTensor(positive_sample) #TODO First 3 needs to be a longtensor, after that should be floats
        return positive_sample, negative_sample, subsampling_weight, self.mode, is_neg
    
    @staticmethod
    def collate_fn(data):
        positive_sample = torch.stack([_[0] for _ in data], dim=0)
        negative_sample = torch.stack([_[1] for _ in data], dim=0)
        subsample_weight = torch.cat([_[2] for _ in data], dim=0)
        mode = data[0][3]
        true = data[0][4]
        return positive_sample, negative_sample, subsample_weight, mode, true