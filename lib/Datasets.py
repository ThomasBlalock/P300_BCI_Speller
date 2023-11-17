import torch
import numpy as np
from torch.utils.data import WeightedRandomSampler

class EEGDataset(torch.utils.data.Dataset):

    def __init__(self, data):
        self.data, self.labels = self.parse_data(data)
        self.window_size = self.data.shape[2]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index], self.labels[index]
    
    def parse_data(self, data):
        """
        Data comes in the form of a list of tuples (data, label)
        data is a 2D tensor (channels, readings)
        label is a 1D tensor (1)

        return:
        data: 3D tensor (samples, channels, readings)
        label: 1D tensor (samples)
        """

        data_list = []
        label_list = []

        channels_idx = (1, 9)

        for sample in data:
            data_list.append(sample[0][channels_idx[0]:channels_idx[1]])
            label_list.append(sample[1])

        return torch.stack(data_list), torch.stack(label_list)
    
    def downsample(self):
        # Count the number of occurrences of each class
        label_counts = torch.bincount(self.labels)
        # Find the least represented class and its count
        min_count = torch.min(label_counts).item()

        downsampled_data = []
        downsampled_labels = []
        # Keep track of how many samples per class are added to the downsampled set
        samples_per_class = dict()

        # Iterate over data and add samples to the new downsampled dataset
        for i in range(len(self.data)):
            label = self.labels[i].item()
            # If the class is not in the dictionary, or the count for this class is less than the minimum count
            if samples_per_class.get(label, 0) < min_count:
                # Add the sample to the downsampled set
                downsampled_data.append(self.data[i])
                downsampled_labels.append(self.labels[i])
                # Increment the count for this class in the dictionary
                samples_per_class[label] = samples_per_class.get(label, 0) + 1

        # Replace the dataset with the downsampled set, stacked into tensors
        self.data = torch.stack(downsampled_data)
        self.labels = torch.stack(downsampled_labels)

    # Function to create a balanced sampler
    def make_balanced_sampler(labels):
        class_counts = torch.bincount(labels)
        class_weights = 1. / class_counts
        weights = class_weights[labels]
        sampler = WeightedRandomSampler(weights, len(weights), replacement=True)
        return sampler

    # Function to print class distribution per batch
    def print_class_distribution_per_batch(dataloader):
        for i, (_, labels) in enumerate(dataloader):
            class_counts = torch.bincount(labels)
            class_distribution = {f"class_{class_idx}": count.item() for class_idx, count in enumerate(class_counts)}
            print(f"Batch {i}: class distribution: {class_distribution}")