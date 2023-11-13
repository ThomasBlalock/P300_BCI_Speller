# P300_BCI_Speller

This repo only contains polished/working code outside of the 'experiment' directory. All in-progress code is stored in 'experiments'.


TODO (model.ipynb): Figure out what's wrong with either the network or the data loading process.
Right before it passes through the network, a batch is size [batch_size, 8, 250] as expected, but then it throws
an error saying that its sized [1, batch_size, 8, 250], reading batch_size as the channels, which is wrong?