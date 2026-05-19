import os
import torch
from torch.utils.data import Dataset
from mypath_tensor import Path


class SimpleTensorSegmentation(Dataset):

    NUM_CLASSES = None

    def __init__(
        self,
        args,
        base_dir=Path.db_root_dir('simple'),
        split='train',
    ):

        super().__init__()

        self.args = args

        # tensor dataset 경로
        self._base_dir = base_dir

        if isinstance(split, str):
            self.split = [split]
        else:
            split.sort()
            self.split = split

        SimpleTensorSegmentation.NUM_CLASSES = args.num_classes

        self.files = []

        for splt in self.split:

            split_dir = os.path.join(self._base_dir, splt)

            file_list = os.listdir(split_dir)
            file_list.sort()

            for file_name in file_list:

                if file_name.endswith(".pt"):

                    full_path = os.path.join(split_dir, file_name)

                    self.files.append(full_path)

        print(f"[{split}] tensor 개수:", len(self.files))

    def __len__(self):
        return len(self.files)

    def __getitem__(self, index):

        file_path = self.files[index]

        data = torch.load(file_path)

        image = data["image"]
        label = data["label"]

        sample = {
            'image': image,
            'label': label,
            'imagename': data.get("filename", file_path),
            'imagesize': image.shape
        }

        return sample

    def __str__(self):
        return 'SimpleTensorSegmentation(split=' + str(self.split) + ')'