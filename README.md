<!--
![3DSlicerLogo-HorizontalF](https://user-images.githubusercontent.com/19158307/224816407-62cc7791-743c-4c4c-a1fe-32f753553ab1.svg)
![](BoneReconstructionPlanner.jpg)
-->
<table style="border:hidden">
<tr>
<td><img src="https://raw.githubusercontent.com/Slicer/Slicer/master/Applications/SlicerApp/Resources/Images/Slicer-Logo.png" height="300"/></td>
<td><img src="BoneReconstructionPlanner.jpg" height="300"/></td>
</tr>
</table>

# BoneReconstructionPlanner

![GitHub Tag](https://img.shields.io/github/v/tag/Slicer/Slicer?sort=semver&label=Slicer)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause) 
[![DOI: 10.1016/j.stlm.2023.100109](https://img.shields.io/badge/DOI-10.1016/j.stlm.2023.100109-blue.svg)](https://www.sciencedirect.com/science/article/pii/S2666964123000103)
[![Citations on Semantic Scholar](https://img.shields.io/badge/dynamic/json?label=Citations&query=%24.citationCount&url=https%3A%2F%2Fapi.semanticscholar.org%2Fgraph%2Fv1%2Fpaper%2FDOI%3A10.1016%2Fj.stlm.2023.100109%3Ffields%3DcitationCount)](https://www.sciencedirect.com/science/article/pii/S2666964123000103#section-cited-by)
[![forks - badge-generator](https://img.shields.io/github/forks/SlicerIGT/SlicerBoneReconstructionPlanner?style=social)](https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/fork)
[![stars - badge-generator](https://img.shields.io/github/stars/SlicerIGT/SlicerBoneReconstructionPlanner?style=social)](https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/stargazers)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/SlicerIGT/SlicerBoneReconstructionPlanner/total)

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
<td align ="center">Custom Fibula Guide Use</br><img src="BoneReconstructionPlanner/Resources/Pictures/photo3DPrintedFibulaGuideUse_gray.png" width="500"/><a href="BoneReconstructionPlanner/Resources/Pictures/photo3DPrintedFibulaGuideUse.png"></br>SEE ORIGINAL PHOTO</a></td>
<td align ="center">Neo Mandible</br><img src="BoneReconstructionPlanner/Resources/Pictures/photoNeoMandible_gray.png" width="500"/><a href="BoneReconstructionPlanner/Resources/Pictures/photoNeoMandible.png"></br>SEE ORIGINAL PHOTO</a></td>
</tr>
<tr>
<td align ="center" colspan="2">Pre Surgery Photo (left) and Post Surgery Photo (right) [*]</br><img src="BoneReconstructionPlanner/Resources/Pictures/photoPreAndPostSurgery.jpg" width="800"/></td>
</tr>
<tr>
<td align ="center">Pre Surgery Orthopantomogram [*]</br><img src="BoneReconstructionPlanner/Resources/Pictures/preSurgeryOrthopantomogram.jpg" width="500"/></td>
<td align ="center">Post Surgery Orthopantomogram [*]</br><img src="BoneReconstructionPlanner/Resources/Pictures/postSurgeryOrthopantomogram.jpg" width="600"/></td>
</tr>
<td align ="right" colspan="2">[*]: marked pictures belong to the same surgery and patient</td>
</tr>
</table>

# Developer statement

As an open-source developer committed to quality, I am dedicated to ensuring that our "medical" software meets the highest standards, with the goal of achieving ISO 13485 compliance in the future. If you encounter any bugs or issues, please [report them](https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/issues/new), and I will work diligently to address and resolve them promptly. (This software is not FDA approved)

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
- [Developer statement](#developer-statement)
- [Citations](#citations)
- [Introduction to BoneReconstructionPlanner](#introduction-to-bonereconstructionplanner)
  - [Benefits of using personalized surgical guides](#benefits-of-using-personalized-surgical-guides)
  - [Cons of using personalized surgical guides](#cons-of-using-personalized-surgical-guides)
  - [User Considerations](#user-considerations)
- [Interactive VSP Demo](#interactive-vsp-demo)
- [Teaser and Tutorial Videos](#teaser-and-tutorial-videos)
- [Documentation](#documentation)
  - [Whitepaper](#whitepaper)
- [Reported Use Cases](#reported-use-cases)
- [Sample Data](#sample-data)
- [Instructions](#instructions)
  - [Installing BoneReconstructionPlanner](#installing-bonereconstructionplanner)
  - [Saving the scene](#saving-the-scene)
  - [Segmentation (Preparation for Virtual Surgical Planning)](#segmentation-preparation-for-virtual-surgical-planning)
  - [Virtual Surgical Planning](#virtual-surgical-planning)
  - [Personalized Fibula Guide Generation](#personalized-fibula-guide-generation)
  - [Create the Fibula Guide Base](#create-the-fibula-guide-base)
  - [Finish the Fibula Surgical Guide](#finish-the-fibula-surgical-guide)
  - [Personalized Mandible Surgical Guide](#personalized-mandible-surgical-guide)
  - [Mandible Reconstruction Simulation](#mandible-reconstruction-simulation)
  - [Export the planning outputs](#export-the-planning-outputs)
  - [Visualization options](#visualization-options)
- [User contact and feedback](#user-contact-and-feedback)
  - [Contact](#contact)
- [License](#license)

# Introduction to BoneReconstructionPlanner

From the engineering point of view this project attemps to be a What You See Is What You Get (WYSIWYG) editor. 

Historically, this project started as Mauro I. Dominguez (EIE, FCEIA, UNR) MScEng Final Project with PhD Andras Lasso (PerkLab, Queens) supervision and Dr Manjula Herath (Malmö University) clinical advice on 2021. After first semester of '21 the project is maintained and keeps growing from Mauro's ad-honorem work.

Its math is robust so you should be able to correctly modify the reconstruction digitally at submillimeter scales (i.e. at features-sizes your eyes will not be able to distinguish). 

Digital means ideal but real-world objects are not, and neither are our inputs (e.g. CT slice thickness, bone models triangle density, smoothing factor, fibula centerline, etc). In addition to that have in mind that other sources of errors (printer resolution, printing orientation, anatomic fit considerations, etc) will add up although most of the time they'll be negligible, that is assumed because complaints have not been [reported](#reported-use-cases).

As far as we know our BoneReconstructionPlanner custom surgical guides will be accurate and effective enough to be adequate tools. Although, you are invited to do a mock surgery to sawbones using BoneReconstructionPlanner designed instruments yourself and weight the results before attempting their use on a IRB-approved case.


## Benefits of using personalized surgical guides
- less total surgical time
- less ischemic time
- less length of hospital stay after surgery
- better osteotomies accuracy
- better neomandible contour, more aesthetic

## Cons of using personalized surgical guides
- VSP software license (free if using BoneReconstructionPlanner,
15k USD annual license if using commercial software)
- 3D printer, biocompatible material, sterilization (can be done
on an in-house 3D printing lab or outsourced)
- needs research-review-board or FDA approval
- half an hour preoperative plan (plenty net time is still saved)
- learning curve for new user or need of biomedical engineer or
qualified technician

## User Considerations
- There are some parameters like the distance between faces of the closing-wedge osteotomies of fibula that can be increased if desired.
- Deviations from the Virtual Surgical Plan could come from big slice thickness CTs, suboptimal segmentation to 3D model convertions, big extrusion layers while 3D printing the guides, not accounting for tool fitting (e.g. periosteum remainings over bone, boneSurface2guideSurface fitting, etc) and other reasons.

# Interactive VSP demo

<table>
<td align ="center">3D models of a finished Virtual Surgical Plan of a Mandibular Reconstruction using Fibula Pieces</br><img src="BoneReconstructionPlanner/Resources/Pictures/screenshot3DDemo.png" width="1000"/></br><a href="https://3dviewer.net/index.html#model=https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/blob/main/BoneReconstructionPlanner.gltf">Open on interactive viewer</a></td>
</tr>
</table>

# Teaser and Tutorial Videos

<table>
<tr>
<td align ="center">Teaser</td>
<td align ="center">Tutorial (will be soon redone)</td>
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
## Coding & Reimbursement Notes
[Read more...](/Docs/CPT-codes-related.md)

## Whitepaper
- [Google slides](https://docs.google.com/presentation/d/1fMJOwBm4-TStrGy0NT975880UG0wlHEA3KAITjMazuw/) 
- [PDF](https://raw.githubusercontent.com/SlicerIGT/SlicerBoneReconstructionPlanner/main/Docs/BoneReconstructionPlanner-whitepaper.pdf)

# Reported Use Cases
See more than 40 plans of other users:
- [Around 25 informally documented uses (Stonia)](https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/discussions/40)
- [One of the use cases by Dr. Manjula Herath (Sri Lanka)](https://discourse.slicer.org/t/bone-reconstruction-planner/19289)
- [One of the use cases by Dr. Steve Maisi (Malaysia)](https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/discussions/58). Link to the [corresponding paper](https://www.sciencedirect.com/science/article/pii/S2666964123000103).

# Sample Data

- Example of minimum data needed for making [segmentations](#segmentation-preparation-for-virtual-surgical-planning) of bones (i.e. mandible CT and fibula CT with 1mm or less axial slice thinkness):
  - <a href="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/releases/download/TestingData/CTFibula.nrrd" >Fibula Scalar Volume</a>
  - <a href="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/releases/download/TestingData/CTMandible.nrrd" >Mandible Scalar Volume</a>

- Example of minimum data needed for a [VSP](#virtual-surgical-planning) (mandible CT, fibula CT, mandible segmentation and fibula segmentation):
  - <a href="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/releases/download/TestingData/FibulaSegmentation.seg.nrrd" >Fibula Segmentation</a>
  - <a href="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/releases/download/TestingData/MandibleSegmentation.seg.nrrd" >Mandible Segmentation</a>

- Finished VSP and guides design (using data similar to the provided above) that can already be loaded to Slicer and modified further:
  - <a href="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/releases/download/TestingData/TestPlanBRP_5.6.2.mrb" >Example Virtual Surgical Plan with Patient-Specific Surgical Guides</a>

- Toy VSP using a rib because a user wondered if it could be possible:
  - <a href="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/releases/download/TestingData/TheoreticalPlanBRP_rib.mrb" >Theoretical Virtual Surgical Plan with a rib (Toy-example)</a>

- <a href="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/releases/download/TestingData/Unofficial_BRP_Videotutorial_5.6.2_Spanish.zip" >Unofficial Spanish videotutorial</a> (credits to @marf-slicer)

# Instructions
(last validated September 30th, 2026)

## Installing BoneReconstructionPlanner

1. You need Slicer 5.12.4 Stable. You have 2 options to download it:
   - Use a download link provided by Kitware: [Windows](https://slicer-packages.kitware.com/api/v1/item/6aa1db04ce9de556d30112bb/download), [Mac](https://slicer-packages.kitware.com/api/v1/item/6aa2063bce9de556d30132d8/download), [Linux](https://slicer-packages.kitware.com/api/v1/item/6aa1beb7ce9de556d3010204/download)
   - As time of the writing of this guide you are also able to go to: https://download.slicer.org/ and download the Stable release (i.e. 5.12.4) for your Operating System.
2. Install Slicer (if you need help, follow [this document section](https://slicer.readthedocs.io/en/latest/user_guide/getting_started.html#installing-3d-slicer)).
3. Open Slicer.
4. Press Ctrl+4 to open the [Extensions Manager](https://slicer.readthedocs.io/en/latest/user_guide/extensions_manager.html#extensions-manager). Or click the upper-right icon with the letter 'E'.
5. Go to 'Install Extensions' tab.
6. On the upper-right search box write "BoneReconstructionPlanner".
7. Click install and give okay to install other extensions if asked (wait till ALL dependencies are installed completely). Then click "Restart" on the bottom-right corner.

To have in mind: every once in a while, you can enter the Extensions Manager and [check for updates](https://slicer.readthedocs.io/en/latest/user_guide/extensions_manager.html#update-extensions-for-slicer-stable-releases) of this extension to get latest bug fixes and added features.


## Saving the scene
- [Save](https://slicer.readthedocs.io/en/latest/user_guide/data_loading_and_saving.html#save-data) the surgical plan when you make relevant progress such as finishing the virtual surgical planning or creating the fibula or mandible guide. We suggest using the "Save scene as single file (.mrb file format)", then you can save your progress with different names "example_plan_v01.mrb", "example_plan_v02.mrb", etc


## Segmentation (Preparation for Virtual Surgical Planning)

Make a mandible segmentation and a fibula segmentation.

Example of a fibula segmentation:

0. CTs should have a recommended slice thickness of 0.65mm (or a maximum slice thickness of 1mm). [Load the study to Slicer](https://slicer.readthedocs.io/en/latest/user_guide/modules/dicom.html#basic-usage).
1. Go to the [segment editor](https://slicer.readthedocs.io/en/latest/user_guide/modules/segmenteditor.html#segment-editor). Create a new segmentation. Create a new segment, name it 'fibula'.
2. Use threshold effect to select only bone. The lower threshold value should not be too high to lose detail (and the higher threshold value should be maximum). Check if your selected threshold value is okay if you can avoid [salt-and-pepper noise](https://en.wikipedia.org/wiki/Salt-and-pepper_noise) being added to the segmentation result. Suggested value: 200.
3. Use [scissors effect](https://slicer.readthedocs.io/en/latest/user_guide/modules/segmenteditor.html#scissors) to keep only the fibula bone.
4. Use [Islands effect](https://slicer.readthedocs.io/en/latest/user_guide/modules/segmenteditor.html#islands), select 'keep selected island' and click over the fibula to keep it. Click "Show 3D".
5. If successful, continue. If not, check out the [segmentation tutorials](https://slicer.readthedocs.io/en/latest/user_guide/modules/segmenteditor.html#tutorials) and start over.
6. Go to Wrap Solidify effect, on Advanced button set the suggested configuration below (by @SteveMaisi) and click apply. (This is needed because it is recommended that bone segmentations have no holes inside so the assisted miterBox positioning algorithms work well).
![192679644-995cbed7-9732-4f87-a936-55e000179fc4](https://user-images.githubusercontent.com/19158307/193409717-40605b9b-e48f-4a51-8332-967a08a9e30c.png)
7. Correct new inaccurate protrusions if needed.
8. The bone segment (fibula in this case) can be anywhere in the segment list of the segmentation, you will select it in the segment selector of BoneReconstructionPlanner.

You'll have to do the same for the mandible in another segmentation node.

## Virtual Surgical Planning

1. Click the search icon on the left of the module selector and write 'BoneReconstructionPlanner'. Click "Switch to module".
2. Select the mandibular segmentation and the mandible segment; and the fibula segmentation and the fibula segment. If you are doing your first plan you can use the test data by clicking "Load test case" (the scene is cleaned before loading the test data).
3. If you have a segmentation of the fibula's vessels also select the corresponding segmentation and segment. The virtual plan can show the ending position of the fibula vessels on the neck and their visibility is controlled by the "Show vessels next to fibula and over neck" checkbox.
4. Select the donor leg: Left or Right
5. If you did the earlier steps, you should be able to click "Create 3D models". 
The fibula line will be created automatically from the fibula 3D model but you may change it if needed erasing its points and creating new ones. Try to draw the points over the fibula diaphysis.
6. If needed, double left-click inside the mandibular 3D view to maximize it. And to return to the multi-view layout, also do double left-click inside the view.
7. Click the mandibular curve point placement button and create a curve along the mandible. This will help giving the cut planes their initial position.
8. Click on the plane icon next to "Mandibular planes" and click where you want a plane. Add as many planes as needed. There will be a bone piece between every two neighboring planes. So the number of mandible planes should be the desired number of bone pieces for the reconstruction plus one. The first and the last mandible planes will be the mandible resection cuts.
9. Explore changing parameters if desired, hover the mouse over them for a descriptive tooltip to appear. After modifying them you'll need to click the "Update virtual plan" button to see changes. 
10. Click "Update virtual plan" to make the reconstruction and create the fibula cut planes. If VSP visualization is not working correctly you can try a hard-update using the button with recycle arrows next to it.
11. Move the mandible planes as desired to change the position/orientation of the cuts.
12. Click "Update virtual plan" again. And repeat as many times as needed.
If the checkbox of the "Update virtual plan" button is ticked (default) the plan reacts to plane movements and updates automatically.
13. Check the available "Visualization Options" as sometimes you need to modify the which or how much data is visible at a given moment to ease the work. You'll get explicative tooltips by hovering the mouse over each widget.
14. When you are happy with the plan, lock it with the padlock button next to the update buttons so it is not changed by accident. While locked, you can play the animation of the plan or export it as a video.

## Personalized Fibula Guide Generation

0. Go to "Fibula Surgical Guide Generation" section of BoneReconstructionPlanner. If the VSP changes, please remind all steps in this section need to be carried over again, same goes for the [Mandible Surgical Guide](#personalized-mandible-surgical-guide).
1. If "Check security margin on miter box creation" is checked, each saw-cut (and the bone it eats) will be tested to not collide with others using the "Security margin (mm)".
2. Select the fibula CT on the "Scalar volume" selector of the "Visualization Options" and press shift over some fibula piece on the corresponding 3D view. The model should be visible on the 2D slice with the corresponding color as an edge.
3. Click the place button of the "Miter box direction line" and click two points over the 2D slice of the fibula. This line sets the direction of the miterBoxes (with this you select, for example, lateral approach or posterior approach). The line should be drawn from a point that belongs to the centerline of the fibula to a point that is distal from the first one on the 2D slice of the fibula.
![Screenshot from 2025-05-02 13-45-01](https://github.com/user-attachments/assets/8df9032c-8dc2-4203-a263-5554161265f9)
As soon as the line has its two points the yellow miterBoxes appear, each one with a slit for the saw to go through. Moving the line points updates the miterBoxes (do it also after updating the virtual plan, since the miterBoxes are not updated with it).
4. Select the parameters of the miter boxes: slot width, slot length, slot height, slot wall, bigger miter box distance to fibula and clearance (this last option is inside the Settings section and it applies also to sawBoxes of the mandible). The miterBoxes are updated automatically when a parameter changes. The combination of clearance and the slot width suggested by most experienced user (@mrtig) is summarized below (more info [here](/Docs/NOTES.md#tolerance-and-slot-width)):

```
  These equations:
  - sawBoxWidth = sawBladeWidth
  - If SLA is used:
  clearanceFitPrintingTolerance = 0.25mm
  else if FDM is used:
  clearanceFitPrintingTolerance = 0.4mm
```

5. Most distal miterBox will be labelled with a "D" and the most proximal miterBox will have a label that identifies laterality ("R" for right leg, "L" for left leg).

## Create the Fibula Guide Base
6. Set the "Guidebase thickness (mm)", "Guidebase angle" and "Guidebase margin" (hover the mouse over them for a descriptive tooltip) and click "Generate fibula guidebase". The guide base is created around the fibula segment you selected, spanning all the miterBoxes, and it is selected on the "Fibula surgical guide base" selector. Click the button again if you change these parameters or the miterBoxes.
7. Alternatively, you can make the guide base manually and select it on the "Fibula surgical guide base" selector:
   - Go to the segment editor, add a new segment and create a copy (using the copy-logical-operator) of the fibula segment, rename it to "fibGuideBase".
   - Use Hollow tool with "inside surface" option and some "shell thickness" between 3mm to 6mm. The number should be decision of the user. Usually more thickness makes the contact between the miterBoxes and the guideBase easier to achieve but sometimes the guideBase ends up too big, wasting material or being too bulky. You can solve this, using a smaller shell if you do "masked painting" in the areas that need filling. [Here is explained how to do it](https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/discussions/40#discussioncomment-1607995)
   - Shape the guidebase using scissors effect. The guidebase should still be in contact with all miterBoxes after finishing this step.
   - Go to the data module and leave only the "fibGuideBase" segment visible on its segmentation, right-click it and press "Export visible segments to models".

## Finish the Fibula Surgical Guide
8. Click the place button of the screw holes "Points" and click over the fibula guide base where you want the screw-holes to be (around one point per segment). A cylinder perpendicular to the guide base appears for each point, and they are updated when you move or delete points. "Radius (mm)" sets the radius of the cylinders.
9. Congratulations: You are ready to execute boolean operations to create the guide. Click on "Create fibula surgical guide". Use the "Guide elements visible" and "Guide visible" checkboxes to see the guide alone. The guide is named "FibulaSurgicalGuidePrototype". If you click this button again after you did some changes to the plan (e.g. changed miterBoxes position) a new prototype will be created ("FibulaSurgicalGuidePrototype_1", "FibulaSurgicalGuidePrototype_2", etc).
10. (Infrequently needed) If boolean operations fail or there is a software crash in the step above, then shift by 0.1mm the virtual plan (i.e. "Initial space"), update the virtual plan, update the miterBoxes (e.g. moving a point of the "Miter box direction line") and execute the boolean operations again.

## Personalized Mandible Surgical Guide

This part of the workflow has some similarities with the fibula guide creation. On the "Mandible Surgical Guide Generation" section:
- Set the parameters of the saw boxes (the clearance of the Settings section also applies to them) and click "Create mandible resection boxes". There will be one sawBox per resection cut: two with "Segmental Mandibulectomy" and one with "Hemimandibulectomy".
- One sawBox will have a label that indicates laterality (i.e. "R" or "L").
- The sawBoxes are movable and you should only move them inside the cut plane, to correct automatic mispositioning.
- By default ("Use guide bases from curves" checked) the guide bases are made from curves: click the place button of "Left side base" and "Right side base" and draw a closed curve over the mandible surface next to each resection cut. Each guidebase is the mandible surface enclosed by its curve extruded by the "Guidebase thickness (mm)". With "Hemimandibulectomy" you just need the guide base of the remaining side.
- Alternatively, uncheck "Use guide bases from curves" and select a segmented guide base model on the "Mandible surgical guide bases" selector. If you are doing a "Segmental Mandibulectomy", you need to segment two guide bases, one for each planar cut, and copy them together to the same segment. Then export them as a unique model as explained on the earlier section.
- Optionally, with "Segmental Mandibulectomy", you could create a bridge between both mandible guidebases to achieve a rigid connection between them when the mandible surgical guide is finished: click the place button of "Mandible bridge" and click the pass-by points of the bridge. "Radius (mm)" sets its thickness. If you created the VSP with "Hemimandibulectomy" mode the bridge is not needed nor allowed.
- Click the place button of the screw holes "Points" and click over the guide bases where you want the screw-holes to be. The cylinders appear automatically.
- Click "Create mandible surgical guide". The guide is named "MandibleSurgicalGuidePrototype" (and "MandibleSurgicalGuidePrototype_1", etc, if you click the button again).

## Mandible Reconstruction Simulation
This maybe useful for users that want to prebend plates with a 3D printed model.
1. Do a [Virtual Surgical Plan](#virtual-surgical-planning)
2. Optionally, you can add an inter-condylar beam to the reconstruction for more rigidity. Click the place button of "Create beam" and click over both condyles. Make the beam thicker or thinner with the "+" and "-" buttons, and show or hide it with the eye button.
3. Click the "Create neomandible" button. The beam is included if you created it. Show or hide the neomandible with the eye button next to it.
![Screenshot from 2025-05-02 16-01-49](https://github.com/user-attachments/assets/7e9416be-1df4-49b2-a118-b1ea95e50597)

## Export the planning outputs
- You may want to [export](https://slicer.readthedocs.io/en/latest/user_guide/data_loading_and_saving.html#export-data) the 3D models you created of mandible and fibula custom surgical guides, and the neomandible. Remember to select the ".stl" export format (which is the format used for 3D printers).

## Visualization options

On Virtual Surgical Planning, you can use the "Lights rendering" setting to make the 3D visualizations nicer. Try "MultiLamp and Shadows", if you don't like it, you can always go back to "Lamp" default setting.
<img src="BoneReconstructionPlanner/Resources/Pictures/screenshotNicerRendering.png"/>

# User contact and feedback

Fell free to open an [issue](https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/issues/new) (or [report here](https://discourse.slicer.org/t/how-to-design-3d-printed-surgical-guide-for-mandible-reconstruction/19754/11)) if you find the instructions or the videotutorial inaccurate, or if you need help finishing the workflow

## Contact
_bone (dot) reconstruction (dot) planner (at) gmail (dot) com_

# License
- <a href="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/" >BoneReconstructionPlanner</a> is licensed under the <a href="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/blob/main/LICENSE" >BSD 3-Clause license</a> (commercial-use friendly).
-  <a href="https://gitlab.kitware.com/vtk/meshing/SlicerVESPA/" >SlicerVESPA</a> extension binaries are derived from <a href="https://github.com/CGAL/cgal/blob/main/Installation/LICENSE.GPL" > CGAL code which is GPLv3-licensed</a> and not distributed by this extension itself. Use optionally.