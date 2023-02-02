from torch.utils.data import Dataset
import cv2
import os
from collections import namedtuple


label = namedtuple(
    "label",
    ["image", "class_id", "bbox", "shd_len", "height", "lat", "long", "time"],
)


class BuildingDataset(Dataset):
    """Custom dataset class for building height detection model

    The class takes in a dataframe and image directory and returns a dataset
    The columns of the dataframe should be:
        [image, image_id, class_id, cx, cy, w, h, shadow_length, lat, long, height, time]


    The output is a named tuple with the following fields:
        ["image", "class_id", "bbox", "shd_len", "height", "lat", "long", "time"]

    Args:
        Dataset (_type_): _description_
    """

    def __init__(self, df, image_dir, image_transforms=None):
        super(BuildingDataset, self).__init__()
        self.df = df
        self.image_dir = image_dir
        self.image_transforms = image_transforms

        self.image_idx_to_image_id = {
            i: image_id for i, image_id in enumerate(self.df.image_id.unique())
        }
        self.image_id_to_image_idx = {
            v: k for k, v in self.image_idx_to_image_id.items()
        }

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        image_id = self.image_idx_to_image_id[idx]

        df = self.df[self.df.image_id == image_id]
        image_name = df.image.unique()

        if len(image_name) > 1:
            raise ValueError(
                f"Image path is not unique. \n\t image_path = {image_name}"
            )

        image_name = image_name[0]
        image = cv2.imread(os.path.join(self.image_dir, image_name))

        if self.image_transforms is not None:
            image = self.image_transforms(image)

        shd_len = df.shadow_length.values
        bbox = df[["cx", "cy", "w", "h"]].values
        height = df.height.values
        time = df.time.values
        lat = df.lat.values
        long = df.long.values
        class_id = df.class_id.values

        return label(image, class_id, bbox, shd_len, height, lat, long, time)
