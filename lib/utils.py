import pickle
import os
import torch
import matplotlib.pyplot as plt


import matplotlib.pyplot as plt

def train(train_dataloader, val_dataloader, model, loss_fn, optimizer, num_epochs, print_every=100):
    train_losses = []
    val_losses = []
    train_accuracies = []
    val_accuracies = []
    
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        for batch, (X, y) in enumerate(train_dataloader):
            optimizer.zero_grad()
            pred = model(X)
            loss = loss_fn(pred, y)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()
            total += y.size(0)

            if batch % print_every == 0 and print_every > 0:
                print(f'Epoch {epoch+1} - Batch {batch+1}/{len(train_dataloader)} - Loss: {loss.item():.4f}')

        avg_train_loss = running_loss / len(train_dataloader)
        avg_train_acc = correct / total
        
        train_losses.append(avg_train_loss)
        train_accuracies.append(avg_train_acc)
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        with torch.no_grad():
            for X, y in val_dataloader:
                pred = model(X)
                loss = loss_fn(pred, y)
                
                val_loss += loss.item()
                correct += (pred.argmax(1) == y).type(torch.float).sum().item()
                total += y.size(0)
        
        avg_val_loss = val_loss / len(val_dataloader)
        avg_val_acc = correct / total
        
        val_losses.append(avg_val_loss)
        val_accuracies.append(avg_val_acc)
        
        print(f'Epoch {epoch+1} - Train Loss: {avg_train_loss:.4f} - Train Accuracy: {avg_train_acc:.4f} - Val Loss: {avg_val_loss:.4f} - Val Accuracy: {avg_val_acc:.4f}')

    # Plotting
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.title("Loss")
    plt.plot(train_losses, label='Train')
    plt.plot(val_losses, label='Validation')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.title("Accuracy")
    plt.plot(train_accuracies, label='Train')
    plt.plot(val_accuracies, label='Validation')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()

    plt.show()

    return train_losses, val_losses, train_accuracies, val_accuracies



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


def test(dataloader, model, loss_fn):
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    model.eval()
    test_loss, correct = 0, 0
    with torch.no_grad():
        for X, y in dataloader:
            pred = model(X)
            test_loss += loss_fn(pred, y).item()
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()
    test_loss /= num_batches
    correct /= size
    print(f'Test Error: \n Accuracy: {(100*correct):>0.1f}%, Avg loss: {test_loss:>8f} \n')