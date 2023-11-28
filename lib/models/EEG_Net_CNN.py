import torch
import torch.nn as nn

# create p300Model
class EEG_Net_CNN(torch.nn.Module):
    """
    Pytorch implementation of EEGNet

    Expecting input of shape (batch_size, channels, readings)
    input = [32, 8, 250] = [batch_size, channels, readings]
    batch_size: number of samples in a batch
    channels: number of channels in a sample (8)
    readings: number of readings in a channel (len())
    """
    
    def __init__(self, num_channels=8, num_classes=2, input_length=250):
        super(EEG_Net_CNN, self).__init__()

        self.block1 = torch.nn.Sequential(
            # Conv1D
            nn.Conv1d(num_channels, 32, kernel_size=50, stride=1, padding=0, bias=False),
            
            # Batch norm
            nn.BatchNorm1d(32),

            # DepthwiseConv1D
            nn.Conv1d(32, 32, kernel_size=1, groups=32, bias=False),

            # Batch norm
            nn.BatchNorm1d(32),

            # ELU Activation
            nn.ELU(alpha=1.0)

            # Avg Pooling 1D
            # nn.AvgPool1d(kernel_size=4, stride=4, padding=0),

            # Dropout
            # nn.Dropout(p=0.15)
        )

        self.block2 = torch.nn.Sequential( 
            # Separable Conv1D
            nn.Conv1d(32, 32, kernel_size=15, stride=1, padding=0, bias=False),

            # Batch norm
            nn.BatchNorm1d(32),

            # ELU Activation
            nn.ELU(alpha=1.0)

            # Avg Pooling 1D
            # nn.AvgPool1d(kernel_size=8, stride=8, padding=0),

            # Dropout
            # nn.Dropout(p=0.15)
        )

        # Calculating the length of the signal after convolutions and pooling
        def conv_output_length(input_length, kernel_size, stride=1, padding=0):
            return (input_length - kernel_size + 2*padding) // stride + 1
        
        conv1_out_length = conv_output_length(input_length, 50, 1, 0)
        pool1_out_length = conv_output_length(conv1_out_length, 4, 4, 0)
        conv2_out_length = conv_output_length(pool1_out_length, 15, 1, 0)
        pool2_out_length = conv_output_length(conv2_out_length, 8, 8, 0)
        
        linear_input_features = pool2_out_length * 32  # 32 is the number of output channels after block1

        # Fully Connected Layer
        self.fc = nn.Linear(in_features=linear_input_features, out_features=num_classes, bias=True)

    def forward(self, x):
        # block 1
        x = self.block1(x)

        # block 2
        x = self.block2(x)

        # flatten
        x = x.view(x.size(0), -1)

        # fc
        x = self.fc(x)

        return x