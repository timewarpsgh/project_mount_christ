import torch
import torch.nn as nn
import numpy as np

# Hyperparameters
BATCH_SIZE = 32
BLOCK_SIZE = 8
LEARNING_RATE = 1e-3
N_EMBD = 32
N_EPOCHS = 1000


class TinyLM(nn.Module):
    def __init__(self, vocab_size):
        super().__init__()
        self.token_embedding = nn.Embedding(vocab_size, N_EMBD)
        self.position_embedding = nn.Embedding(BLOCK_SIZE, N_EMBD)
        self.lm_head = nn.Linear(N_EMBD, vocab_size)

    def forward(self, idx):
        B, T = idx.shape
        tok_emb = self.token_embedding(idx)  # (B,T,n_embd)
        pos_emb = self.position_embedding(torch.arange(T))  # (T,n_embd)
        x = tok_emb + pos_emb
        logits = self.lm_head(x)
        return logits

    def generate(self, idx, max_new_tokens):
        # idx is (B, T) array of indices in the current context
        for _ in range(max_new_tokens):
            # crop idx to the last block_size tokens
            idx_cond = idx[:, -BLOCK_SIZE:]
            # get the predictions
            logits = self(idx_cond)
            # focus only on the last time step
            logits = logits[:, -1, :]  # becomes (B, C)
            # apply softmax to get probabilities
            probs = nn.functional.softmax(logits, dim=-1)  # (B, C)
            # sample from the distribution
            idx_next = torch.multinomial(probs, num_samples=1)  # (B, 1)
            # append sampled index to the running sequence
            idx = torch.cat((idx, idx_next), dim=1)  # (B, T+1)
        return idx


def get_batch(split, train_data, val_data):
    data = train_data if split == 'train' else val_data
    ix = torch.randint(len(data) - BLOCK_SIZE, (BATCH_SIZE,))
    x = torch.stack([data[i:i + BLOCK_SIZE] for i in ix])
    y = torch.stack([data[i + 1:i + BLOCK_SIZE + 1] for i in ix])
    return x, y


def train_model(vocab_size, train_data, val_data):
    model = TinyLM(vocab_size)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)

    # Training loop
    for epoch in range(N_EPOCHS):
        # Get batch
        xb, yb = get_batch('train', train_data, val_data)

        # Forward pass
        logits = model(xb)
        loss = nn.functional.cross_entropy(logits.view(-1, vocab_size), yb.view(-1))

        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if epoch % 100 == 0:
            print(f'Epoch {epoch}, loss: {loss.item():.4f}')

    return model


def prompt_model(prompt, max_response_tokens, model, encode, decode):
    prompt_encoded = torch.tensor([encode(prompt)], dtype=torch.long)
    generated = model.generate(prompt_encoded, max_new_tokens=max_response_tokens)[0].tolist()
    print("\nGenerated text:")
    print(decode(generated))


def prepare_training_data(training_text):
    # Create vocabulary
    chars = sorted(list(set(training_text)))
    vocab_size = len(chars)
    stoi = {ch: i for i, ch in enumerate(chars)}
    itos = {i: ch for i, ch in enumerate(chars)}

    # Encode and decode functions
    encode = lambda s: [stoi[c] for c in s]
    decode = lambda l: ''.join([itos[i] for i in l])

    # Create training data
    data = torch.tensor(encode(training_text), dtype=torch.long)
    n = int(0.9 * len(data))
    train_data = data[:n]
    val_data = data[n:]

    return train_data, val_data, vocab_size, encode, decode


def main():
    # prepare data
    training_text = "Hello world! This is a tiny language model."
    train_data, val_data, vocab_size, encode, decode = \
        prepare_training_data(training_text)

    # train
    model = train_model(vocab_size, train_data, val_data)

    # prompt
    prompt = "Hello "
    max_response_tokens = 10
    prompt_model(prompt, max_response_tokens, model, encode, decode)


if __name__ == '__main__':
    main()