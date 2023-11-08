# P300_BCI_Speller

This repo only contains polished/working code outside of the 'experiment' directory. All in-progress code is stored in 'experiments'.


TODO: test / debug the new method of getting data in the dataObject object. 
Using the times to get the indexes caused some samples to have 1 more element than other samples
This was a rounding margin error.
I tried to just use the start time and add 250, passed in as an argument that defaults to 250. Test it in model.
I have not yet updated the lib packages with the new DataObject and utils. Do that first.