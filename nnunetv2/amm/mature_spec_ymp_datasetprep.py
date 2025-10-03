import SimpleITK
import nibabel
import numpy as np
from batchgenerators.utilities.file_and_folder_operations import *
import shutil
from nnunetv2.dataset_conversion.generate_dataset_json import generate_dataset_json
from nnunetv2.paths import nnUNet_raw
import glob
import nibabel as nib



if __name__ == '__main__':

    #prep folders for new dataset in unet_raw dir
    target_dataset_id = 457
    target_dataset_name = f'Dataset{target_dataset_id:3.0f}_YMP'

    maybe_mkdir_p(join(nnUNet_raw, target_dataset_name))
    imagesTr = join(nnUNet_raw, target_dataset_name, 'imagesTr')
    labelsTr = join(nnUNet_raw, target_dataset_name, 'labelsTr')
    maybe_mkdir_p(imagesTr)
    maybe_mkdir_p(labelsTr)

    # pre-existing datset on P drive, to be parsed local into
    ymp_source = r'P:\Carpal Animal Model\Animal_CT_DATA_Files\MaturedSpecimens'
    ymp_spec = glob.glob(os.path.join(ymp_source,'Y*'))

    #of the ymp_spec, gather the subset that has the 'SEG' subfolder
    ymp_spec_seg = [i for i in ymp_spec if os.path.exists(os.path.join(i,'SEG'))]
    
    cases = [os.path.basename(s) for s in ymp_spec_seg] #Spec name
    base = ymp_source

    # in this dataset, we're first attempting to export the combined segmentation nifti from 3d slicer
    # so we no longer have individual label files, but a single multi-label file
    
    #based on online threads and searches, the labels aren't inherently saved in the nifti (great)
    # so we will have to hardcode them here based on what we know about the data
    # these are the labels Amy Morton/Quianna Vaughn used in 3D Slicer to create the segment
    label_dict = {
        'background': 0,
        'CB2': 1,
        'CB3': 2,
        'CB4': 3,
        'ICB': 4,
        'MC2': 5,
        'MC3': 6,
        'MC4': 7,
        'MC5': 8,
        'RAD': 9,
        'RCB': 10,
        'UCB': 11,
        'ULNA':12
    }

    labelnames = list(label_dict.keys())

    if not os.path.exists(join(nnUNet_raw, target_dataset_name, 'dataset.json')):
        generate_dataset_json(
            join(nnUNet_raw, target_dataset_name),
            {1: 'CT'},  # this was a mistake we did at the beginning and we keep it like that here for consistency
            label_dict,
            len(cases),
            '.nii.gz',
            None,
            target_dataset_name,
            overwrite_image_reader_writer='NibabelIOWithReorient',
            release='1.0.0',
            license='see reference',
            converted_by = 'Amy Morton'
        )

    for case in cases:
        img = nibabel.load(join(base, case,'NRRD', 'CT.nii.gz'))

        if not os.path.exists( join(imagesTr, case + '_0000.nii.gz')):
            nibabel.save(img, join(imagesTr, case + '_0000.nii.gz'))

        seg_labeled_img = nibabel.load(join(base,case, 'SEG',f'{case}.nii.gz'))

        if not os.path.exists(join(labelsTr, case + '.nii.gz')):
            nibabel.save(seg_labeled_img, join(labelsTr, case + '.nii.gz'))

