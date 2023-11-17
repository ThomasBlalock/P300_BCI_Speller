import pickle
import os
import torch


def load_data(directory):
  """Loads all files in a directory into a list.

  Args:
    directory: The directory to load files from.

  Returns:
    A list of all the loaded files.
  """

  files = []
  for filename in os.listdir(directory):
    with open(os.path.join(directory, filename), "rb") as f:
      files.append(pickle.load(f))

  return files


def train(dataloader, model, loss_fn, optimizer, print_batch=False):
    size = len(dataloader.dataset)
    iter_num = len(dataloader)
    model.train()
    for batch, (X, y) in enumerate(dataloader):
        pred = model(X)
        loss = loss_fn(pred, y)

        # backpropagation
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if batch % 100 == 0 and print_batch:
            loss, current = loss.item(), (batch+1) * len(X)
            accuracy = (pred.argmax(1) == y).type(torch.float).sum().item() / len(y)
            print(f'Batch {batch+1} / {iter_num} ~ loss: {loss:>7f} ~  accuracy: {accuracy:>7f}')
    if print_batch:
        loss, current = loss.item(), (batch+1) * len(X)
        accuracy = (pred.argmax(1) == y).type(torch.float).sum().item() / len(y)
        print(f'Batch {batch+1} / {iter_num} ~ loss: {loss:>7f} ~  accuracy: {accuracy:>7f}')