import os
import glob
import string
import pydicom as dicom
import torch
from torch.utils.data.dataset import Dataset
import csv
import pydicom as dicom
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Any 
import random


class DDSMDataset(Dataset):
    def __init__(self, data_transforms: Any=None, data_dir: string=None, imagedata_dir: string=None, metadata_path: string=None, mode: string=None):

        # copy arguments into DDSMDataset object
        self.data_dir = data_dir
        self.imagedata_dir = imagedata_dir
        self.metadata_path = metadata_path
        self.transforms = data_transforms
        if mode == 'train':
            self.mode_equivalent = 0    # train samples are marked with '0' in metadata_table
        elif mode == 'val':
            self.mode_equivalent = 1    # val samples are marked with '1' in metadata_table
        else:
            # throw error!
            pass

        # get metadata
        self.metadata = []
        with open(metadata_path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if int(float(row[-1])) == self.mode_equivalent:
                    self.metadata.append(row)

        # get image data fnames
        all_imagedata_fnames = glob.glob(os.path.join(self.imagedata_dir, '**/*.dcm'), recursive=True)
        # iterate over all_imagedata_fnames
        metadata_t = list(map(list, zip(*self.metadata)))   # transpose list out of lists
        self.imagedata_fnames = []
        for i in range(len(all_imagedata_fnames)):
            # extract unique imagedata_fname
            dcm_f = dicom.dcmread(all_imagedata_fnames[i])
            unique_dcm_name = os.path.join(dcm_f.PatientID.split('.')[0], dcm_f.StudyInstanceUID, dcm_f.SeriesInstanceUID, '000000.dcm')
            # if unique imagedata_fname in metadata table -> add to list of self.imagedata_fnames
            index_in_metadata = [i for i, s in enumerate(metadata_t[11]) if unique_dcm_name in s][0] if len([i for i, s in enumerate(metadata_t[11]) if unique_dcm_name in s])!=0 else None
            index_in_metadata = [i for i, s in enumerate(metadata_t[12]) if unique_dcm_name in s][0] if len([i for i, s in enumerate(metadata_t[12]) if unique_dcm_name in s])!=0 else index_in_metadata
            index_in_metadata = [i for i, s in enumerate(metadata_t[13]) if unique_dcm_name in s][0] if len([i for i, s in enumerate(metadata_t[13]) if unique_dcm_name in s])!=0 else index_in_metadata
            if index_in_metadata is None:
                pass
            else:
                self.imagedata_fnames.append(all_imagedata_fnames[i])

        print("Finished data set preparation. Train and test datasets are stored in ddsm_data dir.")

    def __len__(self):
        return len(self.imagedata_fnames)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
        # get fname of current .dcm-file and load it
        curr_img_fname = self.imagedata_fnames[idx]
        dcm_f = dicom.dcmread(curr_img_fname)

        # get the image data and apply transformations
        dcm_image = dcm_f.pixel_array
        # additional filter which chaches images which do not fulfill all requirements to apply the tranforms on -> if not, choose random new data sample
        if dcm_image.shape[0] < int(os.environ["CROP_SIZE"]) or dcm_image.shape[1] < int(os.environ["CROP_SIZE"]):
            print("Current image too small for crop_size --> select a new one!")
            valid_sample = self.__getitem__(random.randint(0, (self.__len__()-1)))
            return valid_sample
        # apply transformations to valid samples
        dcm_image = self.transforms(dcm_image.astype(np.float))

        # compose a unique name for the dcm-file, search for it in metadata and get it's label
        unique_dcm_name = os.path.join(dcm_f.PatientID.split('.')[0], dcm_f.StudyInstanceUID, dcm_f.SeriesInstanceUID, '000000.dcm')
        # metadata_t = np.array(self.metadata).T.tolist()   # weirdly not working anymore ...
        metadata_t = list(map(list, zip(*self.metadata)))   # transpose list out of lists
        index_in_metadata = [i for i, s in enumerate(metadata_t[11]) if unique_dcm_name in s][0] if len([i for i, s in enumerate(metadata_t[11]) if unique_dcm_name in s])!=0 else None
        index_in_metadata = [i for i, s in enumerate(metadata_t[12]) if unique_dcm_name in s][0] if len([i for i, s in enumerate(metadata_t[12]) if unique_dcm_name in s])!=0 else index_in_metadata
        index_in_metadata = [i for i, s in enumerate(metadata_t[13]) if unique_dcm_name in s][0] if len([i for i, s in enumerate(metadata_t[13]) if unique_dcm_name in s])!=0 else index_in_metadata
        label = int(self.metadata[index_in_metadata][1])-1  # -1 because labels should be between 0 and 3

        if label < 0:   # label is wrong -> select randomly another datasample
            valid_sample = self.__getitem__(random.randint(0, (self.__len__()-1)))
            return valid_sample
        
        # combine to a valid data sample
        sample = {'index': idx, 'image': dcm_image, 'label': label}

        return sample


if __name__ == "__main__":
    data = DDSMDataset(data_dir='/home/m391k/Desktop/BreastDensityData/',
                        train_metadata_fnames=['mass_case_description_train_set.csv', 'calc_case_description_train_set.csv'],
                        test_metadata_fnames=['mass_case_description_test_set.csv', 'calc_case_description_test_set.csv'],
                        )
    print(f"Length of train dataset: {data.__len__(dataset_type='train')}")
    print(f"Length of test dataset: {data.__len__(dataset_type='test')}")
    print(f"Length of train dataset: {data.__len__(dataset_type='val')}")

    data_sample = data.__getitem__(idx=158, dataset_type="train")

    plt.imshow(data_sample['image'])
    # plt.imshow(torch.tensor(data_sample.get('image')))
    plt.show()
    print(f"Label: {data_sample.get('label')}")

    print(0)
