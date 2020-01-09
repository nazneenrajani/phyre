import torch

VOCAB_PATH = "entity_preprocess/phyre.vocab.pt"

vocabs = torch.load(VOCAB_PATH)

for vocab in vocabs:
    words = vocab[1].stoi.keys()
    print(vocab[0], words)
import pdb; pdb.set_trace()
