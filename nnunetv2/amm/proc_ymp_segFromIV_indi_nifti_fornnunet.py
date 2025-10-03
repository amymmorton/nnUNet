# %%
import slicer 
import os
import glob
from os.path import join

from AutoscoperMLib import IO



def exportSegmentationAsBinaryLabelmap(segmentationNode, outputFilePath):
    """
    Exports a segmentation node as a binary labelmap volume.

    Args:
        segmentationNode (slicer.vtkMRMLSegmentationNode): The segmentation node to export.
        outputFilePath (str): The full path and filename for the exported labelmap (e.g., "C:/temp/labelmap.nrrd").
    """
    if not segmentationNode:
        print("Error: No segmentation node provided.")
        return

    # Create a new labelmap volume node
    labelmapNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")

    # Export the segmentation to the labelmap volume
    slicer.modules.segmentations.logic().ExportAllSegmentsToLabelmapNode(segmentationNode, labelmapNode)

    # Save the labelmap volume to a file
    slicer.util.saveNode(labelmapNode, outputFilePath)

    #print(f"Segmentation '{segmentationNode.GetName()}' exported as binary labelmap to '{outputFilePath}'")

    # Clean up the temporary labelmap node
    slicer.mrmlScene.RemoveNode(labelmapNode)





# %%
# pre-existing datset on P drive, to be parsed local into
ymp_source = r'P:\Carpal Animal Model\Animal_CT_DATA_Files\MaturedSpecimens'
ymp_spec = glob.glob(join(ymp_source,'Y*'))

#of the ymp_spec, gather the subset that has the 'SEG' subfolder
ymp_spec_seg = [i for i in ymp_spec if os.path.exists(os.path.join(i,'SEG'))]

spec_ids = [os.path.basename(s) for s in ymp_spec_seg] #Spec name



for ymp_root_this, spec_this in zip(ymp_spec_seg, spec_ids):
# %%
    #ymp_root_this = ymp_spec_seg[0]
    #spec_this = spec_ids[0]

    #print(join(ymp_root_this,'SEG',f'{spec_this}.nii.gz'))

    #remove the multilabel nii.gz
    if os.path.exists(join(ymp_root_this,'SEG')):
        iv_ni = glob.glob(join(ymp_root_this,'SEG','*iv.nii.gz'))
        for i in iv_ni:
            os.remove(i)



    #print(ymp_root_this)
    #print(spec_this)

    seg_files = glob.glob(join(ymp_root_this,'IV.files','*iv'))
    #remove any names that include _ics
    seg_files = [s for s in seg_files if '_ics' not in s]
    #print(seg_files)

    # Currently, nrrd in  root \ specid \ NRRD\ {specid}.nrrd
    # 
    # and ivs in root \ specid \ IV.files\ {boneName}.nrrd

    # 1) Import the nrrd,
    # 2) Import each iv as segmentaion (openinventoeremsh)

    # Probably best, in this loop to alos convert to binary label map and export...
    slicer.util.loadVolume(join(ymp_root_this,'NRRD','CT.nii.gz'))

    for sf in seg_files:
        sfo = os.path.basename(sf)[:-3]
        outputFile = join(ymp_root_this,'SEG',f'{sfo}.nii.gz')

        segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
        segmentationNode.CreateDefaultDisplayNodes()
        # Example usage:
        # Assuming you have a segmentation node named "MySegmentation" in your scene
        IO.loadSegmentation(segmentationNode, sf)
        exportSegmentationAsBinaryLabelmap(segmentationNode, outputFile)

        slicer.mrmlScene.RemoveNode(segmentationNode)

    slicer.mrmlScene.Clear(0)
