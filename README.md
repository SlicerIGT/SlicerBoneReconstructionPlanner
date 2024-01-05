
<!--
![3DSlicerLogo-HorizontalF](https://user-images.githubusercontent.com/19158307/224816407-62cc7791-743c-4c4c-a1fe-32f753553ab1.svg)
![](BoneReconstructionPlanner.jpg)
-->
<table style="border:hidden">
<tr>
<td><img src="https://user-images.githubusercontent.com/19158307/224816407-62cc7791-743c-4c4c-a1fe-32f753553ab1.svg" width="500"/></td>
<td><img src="BoneReconstructionPlanner.jpg" width="500"/></td>
</tr>
</table>

# BoneReconstructionPlanner

[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

A [3D Slicer](https://www.slicer.org/) extension for virtual surgical planning of mandibular reconstruction with vascularized fibula free flap and generation of patient-specific surgical guides. 


<table>
<tr>
<td align ="center">Virtual Surgery Planning</td>
<td align ="center">Patient-specific Surgical Guides</td>
</tr>
<tr>
<td><img src="BoneReconstructionPlanner/Resources/Pictures/screenshotPlanning.png" width="500"/></td>
<td><img src="BoneReconstructionPlanner/Resources/Pictures/screenshotPatientSpecificSurgicalGuides.png" width="500"/></td>
</tr>
<tr>
<td align ="center">Custom Fibula Guide Use (link below)</td>
<td align ="center">Neo Mandible (link below)</td>
</tr>
<tr>
<td align ="center"><a href="BoneReconstructionPlanner/Resources/Pictures/photo3DPrintedFibulaGuideUse.png">GRAPHIC EXPLICIT PHOTO</a></td>
<td align ="center"><a href="BoneReconstructionPlanner/Resources/Pictures/photoNeoMandible.png">GRAPHIC EXPLICIT PHOTO</a></td>
</tr>
<tr>
<td align ="center" colspan="2">Pre Surgery Photo (left) and Post Surgery Photo (right) [*]</td>
</tr>
<tr>
<td align ="center" colspan="2"><img src="BoneReconstructionPlanner/Resources/Pictures/photoPreAndPostSurgery.jpg" width="800"/></td>
</tr>
<tr>
<td align ="center">Pre Surgery Orthopantomogram [*]</td>
<td align ="center">Post Surgery Orthopantomogram [*]</td>
</tr>
<tr>
<td><img src="BoneReconstructionPlanner/Resources/Pictures/preSurgeryOrthopantomogram.jpg" width="500"/></td>
<td><img src="BoneReconstructionPlanner/Resources/Pictures/postSurgeryOrthopantomogram.jpg" width="600"/></td>
</tr>
<td align ="right" colspan="2">[*]: marked pictures belong to the same surgery and patient</td>
</tr>
</table>

# Citations

If you use BoneReconstructionPlanner please cite our paper:
https://www.sciencedirect.com/science/article/pii/S2666964123000103

```bash
@article{MAISI2023100109,
   title = {In-house virtual surgical planning for mandibular reconstruction with fibula free flap: Case series and literature review},
   author = {Steve Maisi and Mauro Dominguez and Peta Charmaine Gilong and Chung Tze Kiong and Syarfa Hajam and Ahmad Fadhli Ahmad Badruddin and Han Fong Siew and Saravanan Gopalan and Kok Tuck Choon},
   journal = {Annals of 3D Printed Medicine},
   volume = {10},
   pages = {100109},
   year = {2023},
   issn = {2666-9641},
   doi = {https://doi.org/10.1016/j.stlm.2023.100109},
   url = {https://www.sciencedirect.com/science/article/pii/S2666964123000103},
   keywords = {Virtual surgical planning, In-house VSP, Fibula free flap, Mandibular reconstruction},
}
```

# Table of Contents
- [Overview](#bonereconstructionplanner)
- [Citations](#citations)
- [Description](#description)
  - [Benefits](#benefits)
  - [Cons](#cons)
  - [User Considerations](#user-considerations)
- [Interactive VSP Demo](#interactive-vsp-demo)
- [Teaser and Tutorial Videos](#teaser-and-tutorial-videos)
- [Documentation](#documentation)
- [Reported Use Cases](#reported-use-cases)
- [Sample Data](#sample-data)
- [Instructions](#instructions)
  - [Installing BoneReconstructionPlanner](#installing-bonereconstructionplanner)
  - [Segmentation (Preparation for Virtual Surgical Planning)](#segmentation-preparation-for-virtual-surgical-planning)
  - [Virtual Surgical Planning](#virtual-surgical-planning)
  - [Personalized Fibula Guide Generation](#personalized-fibula-guide-generation)
  - [Create the Fibula Guide Base](#create-the-fibula-guide-base)
  - [Finish the Fibula Surgical Guide](#finish-the-fibula-surgical-guide)
  - [Personalized Mandible Surgical Guide](#personalized-mandible-surgical-guide)
  - [Mandible Reconstruction Simulation](#mandible-reconstruction-simulation)
- [Contributing](#Contributing)
- [Community](#Community)
- [Additional Resources](#Additional-Resources)
- [License](#license)

# Description

From the engineering point of view this project attemps to be a What You See Is What You Get (WYSIWYG) editor. 

Historically, this project started as Mauro I. Dominguez (EIE, FCEIA, UNR) MScEng Final Project with PhD Andras Lasso (PerkLab, Queens) supervision and Dr Manjula Herath (Malmö University) clinical advice on 2021. After first semester of '21 the project is maintained and keeps growing from Mauro's ad-honorem work.

Its math is robust so you should be able to correctly modify the reconstruction digitally at submillimeter scales (i.e. at features-sizes your eyes will not be able to distinguish). 

Digital means ideal but real-world objects are not, and neither are our inputs (e.g. CT slice thickness, bone models triangle density, smoothing factor, fibula centerline, etc). In addition to that have in mind that other sources of errors (printer resolution, printing orientation, anatomic fit considerations, etc) will add up although most of the time they'll be negligible, that is assumed because complaints have not been [reported](#reported-use-cases).

As far as we know our BoneReconstructionPlanner custom surgical guides will be accurate and effective enough to be adequate tools. Although, you are invited to do a mock surgery to sawbones using BoneReconstructionPlanner designed instruments yourself and weight the results before attempting their use on a IRB-approved case.

## Benefits:
- less operation time
- less ischemic time
- less length of hospital stay after surgery
- better osteotomies accuracy
- better neomandible contour, more aesthetic

## Cons:
- VSP software license (free if using BoneReconstructionPlanner,
15k USD annual license if using commercial software)
- 3D printer, biocompatible material, sterilization (can be done
on an in-house 3D printing lab or outsourced)
- needs research-review-board or FDA approval
- half an hour preoperative plan (plenty net time is still saved)
- learning curve for new user or need of biomedical engineer or
qualified technician

## User Considerations:
- There are some parameters like the distance between faces of the closing-wedge osteotomies of fibula that can be increased if desired.
- Deviations from the Virtual Surgical Plan could come from big slice thickness CTs, suboptimal segmentation to 3D model convertions, big extrusion layers while 3D printing the guides, not accounting for tool fitting (e.g. periosteum remainings over bone, boneSurface2guideSurface fitting, etc) and other reasons.

# Interactive VSP demo

<table>
<tr>
<td align ="center">See a finished Virtual Surgical Plan of a Mandibular Reconstruction using Fibula Pieces.
</td>
</tr>
<tr>
<td align ="center">
Link: https://3dviewer.net/index.html#model=https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/blob/main/BoneReconstructionPlanner.gltf
</td>
</tr>
<tr>
<td align ="center"><img src="BoneReconstructionPlanner/Resources/Pictures/screenshot3DDemo.png" width="1000"/></td>
</tr>
</table>

# Teaser and Tutorial Videos

<table>
<tr>
<td align ="center">Teaser</td>
<td align ="center">Tutorial</td>
</tr>
<tr>
<td align ="center"><img src="https://img.youtube.com/vi/wsr_g_1E_pw/0.jpg" width="500"/></td>
<td align ="center"><img src="https://img.youtube.com/vi/g9Vql5h6uHM/0.jpg" width="500"/></td>
</tr>
<tr>
<td align ="center">https://www.youtube.com/watch?v=wsr_g_1E_pw</td>
<td align ="center">https://www.youtube.com/watch?v=g9Vql5h6uHM</td>
</tr>
</table>

# Documentation
- [White Paper (pdf)](https://raw.githubusercontent.com/SlicerIGT/SlicerBoneReconstructionPlanner/main/Docs/BoneReconstructionPlannerSlides.pdf)

# Reported Use Cases
See the results of other users:
- [More than 20 informally documented uses (Stonia)](https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/discussions/40)
- [One of the use cases by Dr. Manjula Herath (Sri Lanka)](https://discourse.slicer.org/t/bone-reconstruction-planner/19289)
- [One of the use cases by Dr. Steve Maisi (Malaysia)](https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/discussions/58). Link to the [corresponding paper](https://www.sciencedirect.com/science/article/pii/S2666964123000103).

# Sample Data

- Example of minimum data needed for making [segmentations](#segmentation-preparation-for-virtual-surgical-planning) of bones (i.e. mandible CT and fibula CT with 1mm or less axial slice thinkness):
  - <a href="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/releases/download/TestingData/CTFibula.nrrd" >Fibula Scalar Volume</a>
  - <a href="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/releases/download/TestingData/CTMandible.nrrd" >Mandible Scalar Volume</a>

- Example of minimum data needed for a [VSP](#virtual-surgical-planning) (mandible CT, fibula CT, mandible segmentation and fibula segmentation):
  - <a href="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/releases/download/TestingData/FibulaSegmentation.seg.nrrd" >Fibula Segmentation</a>
  - <a href="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/releases/download/TestingData/MandibleSegmentation.seg.nrrd" >Mandible Segmentation</a>

- Finished VSP and guides design using above data that can already be loaded to Slicer and modified further:
  - <a href="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/releases/download/TestingData/TestPlanBRP.mrb" >Example Virtual Surgical Plan with Patient-Specific Surgical Guides</a>

- Toy VSP using a rib because a user wondered if it could be possible:
  - <a href="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/releases/download/TestingData/TheoreticalPlanBRP_rib.mrb" >Theoretical Virtual Surgical Plan with a rib (Toy-example)</a>

# Instructions
([last validated 12/27/2023](https://discourse.slicer.org/t/new-3d-slicer-extension-for-planning-and-surgical-guide-generation-for-mandibular-bone-reconstruction/17638/17))

## Installing BoneReconstructionPlanner

1. You need Slicer 5.6.1 Stable. You have 2 options to download it:
   - Use a download link provided by Kitware: [Windows](https://slicer-packages.kitware.com/api/v1/item/65783bef83a3201b44d52468/download), [macOS](https://slicer-packages.kitware.com/api/v1/item/6578222c83a3201b44d4feda/download), [Linux](https://slicer-packages.kitware.com/api/v1/item/657813b183a3201b44d4e6f7/download)
   - You can shift back the Slicer download link some number of days to an older version, for example 20 days, with https://download.slicer.org/?offset=-20 (Increase the shift until you get version 5.6.1 on the Stable release row)
2. Install Slicer
3. Open Slicer
4. Press Ctrl+4 to open the extension manager. Or click the upper-right icon with the letter 'E'
5. Go to 'Install Extensions' tab
6. On the upper-right search box write "BoneReconstructionPlanner"
7. Click install and give okay to install other extensions if asked (wait till ALL dependencies are installed completely).


## Segmentation (Preparation for Virtual Surgical Planning)

Make a mandible segmentation and a fibula segmentation.

Example:

0. CTs should have a recommended slice thickness of 0.65mm (or a maximum slice thickness of 1mm)
1. Go to the segment editor. Create a new segmentation. Create a new segment, name it 'fibula'.
2. Use threshold effect to select bone but not connecting tissue (like ligaments). Check if your selected threshold value is okay if there is no connection of the segmented bones near the joint. Threshold value should not be too low to not lose detail. Suggested value: 200
3. Use Islands effect, select 'keep selected island' and click over the fibula to keep it.
4. If successful continue. If not start over and use a higher threshold value or use scissors to isolate the fibula
5. Go to Wrap Solidify effect, on Advanced button set the suggested configuration below (by @SteveMaisi) and click apply. (This is needed because it is recommended that bone segmentations have no holes inside so the assisted miterBox positioning algorithms work well)
![192679644-995cbed7-9732-4f87-a936-55e000179fc4](https://user-images.githubusercontent.com/19158307/193409717-40605b9b-e48f-4a51-8332-967a08a9e30c.png)
6. Restore the segmentation smoothing factor to 0.5
![4350535f4e0b0d5738701e8257e30728b26b0b96](https://user-images.githubusercontent.com/19158307/193409905-5479f1bb-5fe0-4954-83e7-932cc295bd02.png)
7. Correct errors on segmentations with scissors if needed.
8. The bone segment (fibula or mandible) should be the first of the segment-list of the segmentation. In other words the bone segment should be in position zero of the list.

## Virtual Surgical Planning

0. [Save](https://slicer.readthedocs.io/en/latest/user_guide/data_loading_and_saving.html#non-dicom-data) frequently as the surgical plan can be reopened from where you left it if there is a crash (software malfunction). We are trying to fix a bug that makes Slicer close unexpectedly ([more info here](https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/issues/63))
1. Click the search icon on the left of the module selector and write 'BoneReconstructionPlanner'. Click switch to module.
2. Select the mandibular segmentation and the fibula segmentation.
3. Click "Create bone models from segmentations"
4. Click "Add mandibular curve" and create a curve along the mandible. This will help giving the cut planes their initial position. It's a bit important to make it quite similar to the ideal mandible curve the patient would have if he was healthy because the plane positioning algorithms depend on it.
5. Click "Add cut plane" and click where you want plane. Add as many planes as needed. There will be a bone piece between every two adjacent planes. So the number of mandible planes should be the desired number of bone pieces for the reconstruction plus one. The first and the last mandible planes will be the mandible resection cuts.
6. Click "Add fibula line". Draw a line over the fibula on the 3D view. First point distal, last point proximal.
7. Click "Center fibula line using fibula model" to make the line be similar to the anatomical axis of the fibula.
8. Tick these options: "Automatic mandibular planes positioning for maximum bones contact area", "Make all mandible planes rotate together"
9. Click "Update fibula planes over fibula line; update fibula bone pieces and transform them to mandible" to make the reconstruction and create the fibula cut planes.
10. Move the mandible planes as desired to change the position/orientation of the cuts.
11. Click "Update fibula planes over fibula line; update fibula bone pieces and transform them to mandible" again. And repeat as many times as needed.
If you tick the button it will react on plane movements and update automatically.

## Personalized Fibula Guide Generation

1. Press shift over some fibula piece on the corresponding 3D view. The model should be visible on the 2D slice with the corresponding color as an edge. Create a line over the 2D slice of the fibula that will set the direction of the miterBoxes (with this you select, for example, lateral approach or posterior approach). The line should me drawn from the centerline of the fibula to a point that is distal from the first one on the 2D slice of the fibula.
2. Select the parameters of the miter boxes: lenght, width, height, wall thickness and tolerance (this last option is inside the Settings widget and it applies also to sawBoxes of the mandible). The combination of tolerance and the slot width suggested by most experienced user (@mrtig) is:

```
It's easy to find out what good fit for the saw blade is by printing a few pockets with different widths. It depends on the printing technology. There is a summary at the end.

The saw blade used on this example is 0.2mm. If I print using the SLA printer I make the pockets 0.3 mm. With the FDM printer the width needs to be 0.6 mm. And the default tolerance is 0.2mm

These are the equations:

Suggested sawBoxSlotWidths
If SLA is used:
sawBoxSlotWidth = sawBladeWidth + 0.1mm
else if FDM is used:
sawBoxSlotWidth = sawBladeWidth + 0.4mm

realSawBoxWidth = sawBoxSlotWidth+2*clearanceFitPrintingTolerance

So for this example we have:
If SLA is used:
realSawBoxWidth = sawBladeWidth + 0.1mm +2*clearanceFitPrintingTolerance = 0.2mm + 0.1mm + 2*0.2mm = 0.7mm
else if FDM is used:
realSawBoxWidth = sawBladeWidth + 0.4mm +2*clearanceFitPrintingTolerance = 0.2mm + 0.4mm + 2*0.2mm = 1.0mm

From these we can find the realClearanceFitPrintingTolerance (that should be used with the realSawBoxWidth) as:
If SLA is used:
realClearanceFitPrintingTolerance = (realSawBoxWidth - sawBladeWidth)/2 = (0.7mm - 0.2mm)/2 = 0.25mm
else if FDM is used:
realClearanceFitPrintingTolerance = (realSawBoxWidth - sawBladeWidth)/2 = (1.0mm - 0.2mm)/2 = 0.4mm

As a summary:
You should use these equations
- sawBoxWidth = sawBladeWidth
- If SLA is used:
clearanceFitPrintingTolerance = 0.25mm
else if FDM is used:
clearanceFitPrintingTolerance = 0.4mm

```


3. Click "Create miter boxes from fibula planes". The yellow miterBoxes will appear, each one with a long box that will create the slit for the saw to go through.

## Create the Fibula Guide Base
3. Go to the segment editor, add a new segment and create a copy (using the copy-logical-operator) of the fibula segment, rename it to "fibGuideBase".
4. Use Hollow tool with "inside surface" option and some "shell thickness" between 3 to 6mm. The number should be decision of the user. Usually more thickness makes the contact between the miterBoxes and the guideBase easier to achieve but sometimes the guideBase ends up too big wasting material or being uncomfortable. You can solve this, using a smaller shell if you do "masked painting" in the areas that need filling.
[Here is explained how to do it](https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/discussions/40#discussioncomment-1607995)
5. Go to the data module and leave only the fibGuideBase segment visible on its segmentation, right-click it and press "Export visible segments to models"

## Finish the Fibula Surgical Guide
6. On the "Fibula Surgical Guide Generation" layout of BRP click on the button "Create fiducial list" and position around one point per segment were you want the screw-hole to be (the fibGuideBase model should be visible).
7. Select the fibula guide base model that you exported on the corresponding model selector. Be sure the correct pointList is selected on the corresponding point selector. If you go by defaults it should work fine.
8. Click "Create cylinder from fiducial list and fibula surgical guide base". Some cylinders should appear over the fibula guide base.
9. Congratulations: You are ready to execute boolean operations to create the guide. Click on "Make boolean operations to surgical guide base with screwHolesCylinders and miterBoxes". The guide will be created, you can be sure by using the NodeControlBox that is above and hiding everything else by clicking each "eye icon" of the component objects. The name of the guide will end with the word "Prototype". If you execute this button again after you did some changes to the plan (e.g. changed miterBoxes position) a new prototype will be created.

## Personalized Mandible Surgical Guide

The workflow doesn't differ much from fibula guide creation.
Except that:
- The sawBoxes are movable and you should only move them inside the cut plane, to correct automatic mispositioning. After that hide the "biggerSawBoxes interaction handles" so you have a comfortable experience on later steps.
- You need to segment two guide bases, one for each planar cut, and copy them together to the same segment. Then export them as a unique model as explained on the earlier section.
- You may like to create a bridge between both mandibleGuides to make a rigid connection between them. This is done with the module "MarkupsToModel" and it's very easy to use.
- You need to put the correct models on the corresponding selectors on "Mandible Surgical Guide Generation" panel

## Mandible Reconstruction Simulation
1. Do a Virtual Surgical Plan
2. Click "Create 3D model of the reconstruction for 3D printing". This button maybe useful for users that want to prebent plates.

# User contributions and feedback

Fell free to open an [issue](https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/issues/new) (yes, you need a Github account) if you find the instructions or the videotutorial inaccurate, or if you need help finishing the workflow

# License
- <a href="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/blob/main/LICENSE" >Read license</a>
