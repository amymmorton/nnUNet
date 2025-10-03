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
    
    sid = [os.path.basename(s) for s in ymp_spec_seg] #Spec name
    base = ymp_source


    # discover labels
    label_fnames = nifti_files(join(ymp_spec_seg[0],'SEG'),  join=False)
    label_dict = {i[:-7]: j + 1 for j, i in enumerate(label_fnames)}
    labelnames = list(label_dict.keys())
    label_dict['background'] = 0

    if not os.path.exists(join(nnUNet_raw, target_dataset_name, 'dataset.json')):
        generate_dataset_json(
            join(nnUNet_raw, target_dataset_name),
            {1: 'CT'},  # this was a mistake we did at the beginning and we keep it like that here for consistency
            label_dict,
            len(sid),
            '.nii.gz',
            None,
            target_dataset_name,
            overwrite_image_reader_writer='NibabelIOWithReorient',
            release='1.0.0',
            license='see reference',
            converted_by = 'Amy Morton'
        )

    
    for case in sid:
        img = nibabel.load(join(base, case,'NRRD', 'CT.nii.gz'))

        if not os.path.exists( join(imagesTr, case + '_0000.nii.gz')):
            nibabel.save(img, join(imagesTr, case + '_0000.nii.gz'))

        seg_nib = nibabel.load(join(base,case,'SEG', labelnames[0] + '.nii.gz'))
        init_seg_npy = np.asanyarray(seg_nib.dataobj)
        init_seg_npy[init_seg_npy > 0] = label_dict[labelnames[0]]
        for labelname in labelnames[1:]:
            seg = nibabel.load(join(base,case,'SEG', labelname + '.nii.gz'))
            seg = np.asanyarray(seg.dataobj)
            init_seg_npy[seg > 0] = label_dict[labelname]
        out = nibabel.Nifti1Image(init_seg_npy, affine=seg_nib.affine, header=seg_nib.header)
        if not os.path.exists(join(labelsTr, case + '.nii.gz')):
            nibabel.save(out, join(labelsTr, case + '.nii.gz'))

