import pickle
import os


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