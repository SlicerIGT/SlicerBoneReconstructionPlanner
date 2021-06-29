# Bone Reconstruction Planner

![](BoneReconstructionPlanner.jpg)

A 3D Slicer extension for virtual surgical planning of mandibular reconstruction with vascularized fibula free flap and generation of patient-specific surgical guides. 

# Introduction

Patient-specific guides dramatically improve the success rate and efficiency. 3D printing is revolutionizing reconstructive surgery by making it possible to construct patient-specific guides that are anatomically customized for each patient's need. Unfortunately, this technology is out of reach of most surgeons across the world due to the complexity and costs of existing solutions. The added cost of this technology, per case, is estimated to be around USD 3000 to USD 5000. Our ambition is to disrupt this market by providing an all-in-one cost-efficient and easy-to-use, open-source, and customizable software solution based on 3D Slicer, a free and open-source software package for image analysis and scientific visualization. The successful creation of this technology will enable the development of “patient and site-specific surgical guides”, manufactured through a combination of 3D planning and CAD/CAM. This solution will have the capacity to meet the complex needs of craniofacial reconstruction in a controlled manner. The outcome of the project will be an open-source solution that can make a 3D digital surgical plan that is transferred to the operating room via 3D-printed, patient-specific models, guides, and plates.

# Screenshots

- Virtual Surgery Planning:

![](BoneReconstructionPlanner/Resources/Screenshots/screenshotPlanning.png)

- Patient-specific Surgical Guides:

![](BoneReconstructionPlanner/Resources/Screenshots/screenshotPatientSpecificSurgicalGuides.png)


# Video

 <a href="https://youtu.be/wsr_g_1E_pw" target="_blanck"><img src="https://raw.githubusercontent.com/SlicerIGT/SlicerBoneReconstructionPlanner/main/BoneReconstructionPlanner/Resources/Screenshots/videoThumbnail.png" /></a>
# Documentation

- [High-level design overview](https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/raw/main/Docs/Design.pptx)

# Use Cases
[First clinical use](https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/discussions/40)

# Sample Data
- <a href="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/releases/download/TestingData/Fibula.nrrd" >Fibula Scalar Volume</a>
- <a href="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/releases/download/TestingData/ResectedMandible.nrrd" >Mandible Scalar Volume</a>

# Instructions

## Installing BoneReconstructionPlanner

1. Download Slicer Stable Release from here: https://download.slicer.org/ It's version is 4.11.20210226
2. Install Slicer
3. Open Slicer
4. Press Ctrl+4 to open the extension manager. Or click the upper-right icon with the letter 'E'
5. Go to 'Install Extensions' tab
6. On the upper-right search box write "BoneReconstructionPlanner"
7. Click install and give okay to install other extensions if asked.
8. Tell me if there are some errors till here.


## Segmentation (Preparation for Virtual Surgical Planning)

Make a mandible segmentation and a fibula segmentation.

Example:
0. CTs should have a recommended slice thickness of 0.65mm (or a maximum slice thickness of 1mm)
1. Go to the segment editor. Create a new segmentation. Create a new segment, name it 'fibula'.
2. Use threshold effect to select bone but not connecting tissue (like ligaments). Check if your selected threshold value is okay if there is no connection of the segmented bones near the joint. Threshold value should not be too low to not lose detail. Suggested value: 200
3. Use Islands effect, select 'keep selected island' and click over the fibula to keep it.
4. If successful continue. If not start over and use a higher threshold value or use scissors to isolate the fibula
5. Go to Wrap Solidify effect and click apply. (This is needed because it is recommended that bone segmentations have no holes inside so the assisted miterBox positioning algorithms work well)
6. Correct errors on segmentations with scissors if needed.
7. The bone segment (fibula or mandible) should be the first of the segment-list of the segmentation. In other words the bone segment should be in position zero of the list.

## Virtual Surgical Planning

1. Click the search icon on the left of the module selector and write 'BoneReconstructionPlanner'. Click switch to module.
2. Select the mandibular segmentation and the fibula segmentation.
3. Click "Create bone models from segmentations"
4. Click "Add mandibular curve" and create a curve along the mandible. This will help giving the cut planes their initial position.
5. Click "Add cut plane" and click where you want plane. Add as many planes as needed. There will be a bone piece between every two adjacent planes. So the number of mandible planes should be the desired number of bone pieces for the reconstruction plus one. The first and the last mandible planes will be the mandible resection cuts.
6. Click "Add fibula line". Draw a line over the fibula on the 3D view. First point distal, last point proximal.
7. Click "Center fibula line using fibula model" to make the line be similar to the anatomical axis of the fibula.
8. Tick these options: "Automatic mandibular planes positioning for maximum bones contact area", "Make all mandible planes rotate together"
9. Click "Update fibula planes over fibula line; update fibula bone pieces and transform them to mandible" to make the reconstruction and create the fibula cut planes.
10. Move the mandible planes as desired to change the position/orientation of the cuts.
11. Click "Update fibula planes over fibula line; update fibula bone pieces and transform them to mandible" again. And repeat as many times as needed.


# License
- <a href="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/blob/main/LICENSE" >Read license</a>
