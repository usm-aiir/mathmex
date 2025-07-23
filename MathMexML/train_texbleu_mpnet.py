"""
train_texbleu_mpnet.py

This script trains a fresh MPNet model using the TeXBLEU tokenizer and ARQMath triplet data
for math-aware semantic search.

Pipeline context:
- Uses a custom tokenizer (tokenizer.json) from the TeXBLEU project, specialized for LaTeX-inclusive text.
- Loads triplets (question, positive answer, negative answer) extracted from ARQMath data.
- Trains a randomly initialized MPNet model (same architecture as 'all-mpnet-base-v2') using triplet margin loss.
- Saves the trained model and tokenizer for later use in a search backend.

Requirements:
- torch
- transformers
- lxml
- tqdm
- tokenizer.json (from TeXBLEU) in the same folder
- arqmath_triplets.pkl (from extract_arqmath_triplets.py) in ARQMathData/

Usage:
1. Run extract_arqmath_triplets.py to generate triplets.
2. Run this script to train the model:
   python train_texbleu_mpnet.py

Outputs:
- Trained model and tokenizer saved in ./texbleu-mpnet/
"""

from transformers import PreTrainedTokenizerFast, MPNetConfig, MPNetModel, Trainer, TrainingArguments
import torch
from torch.utils.data import Dataset
import torch.nn.functional as F
import pickle
import os

# Load the TeXBLEU tokenizer
tokenizer = PreTrainedTokenizerFast(tokenizer_file="tokenizer.json")

# Initialize a fresh MPNet model (same architecture as all-mpnet-base-v2)
config = MPNetConfig.from_pretrained("sentence-transformers/all-mpnet-base-v2")
model = MPNetModel(config)

# Load ARQMath triplets
with open(os.path.join("ARQMathData", "arqmath_triplets.pkl"), "rb") as f:
    pairs = pickle.load(f)

# Dataset for triplet training
class ContrastiveDataset(Dataset):
    def __init__(self, pairs, tokenizer, max_length=128):
        self.pairs = pairs
        self.tokenizer = tokenizer
        self.max_length = max_length
    def __len__(self):
        return len(self.pairs)
    def __getitem__(self, idx):
        anchor, positive, negative = self.pairs[idx]
        anchor_enc = self.tokenizer(anchor, truncation=True, padding='max_length', max_length=self.max_length, return_tensors='pt')
        positive_enc = self.tokenizer(positive, truncation=True, padding='max_length', max_length=self.max_length, return_tensors='pt')
        negative_enc = self.tokenizer(negative, truncation=True, padding='max_length', max_length=self.max_length, return_tensors='pt')
        return {
            "anchor_input_ids": anchor_enc["input_ids"].squeeze(),
            "anchor_attention_mask": anchor_enc["attention_mask"].squeeze(),
            "positive_input_ids": positive_enc["input_ids"].squeeze(),
            "positive_attention_mask": positive_enc["attention_mask"].squeeze(),
            "negative_input_ids": negative_enc["input_ids"].squeeze(),
            "negative_attention_mask": negative_enc["attention_mask"].squeeze(),
        }

dataset = ContrastiveDataset(pairs, tokenizer)

# Custom Trainer for triplet loss
class TripletTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False):
        anchor = model(input_ids=inputs["anchor_input_ids"], attention_mask=inputs["anchor_attention_mask"]).last_hidden_state[:, 0, :]
        positive = model(input_ids=inputs["positive_input_ids"], attention_mask=inputs["positive_attention_mask"]).last_hidden_state[:, 0, :]
        negative = model(input_ids=inputs["negative_input_ids"], attention_mask=inputs["negative_attention_mask"]).last_hidden_state[:, 0, :]
        loss = F.triplet_margin_loss(anchor, positive, negative, margin=1.0, p=2)
        return (loss, None) if return_outputs else loss

training_args = TrainingArguments(
    output_dir="./texbleu-mpnet",
    per_device_train_batch_size=2,
    num_train_epochs=1,
    logging_steps=1,
    save_steps=10,
    remove_unused_columns=False,
)

trainer = TripletTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
)

trainer.train()
trainer.save_model("./texbleu-mpnet")
tokenizer.save_pretrained("./texbleu-mpnet")