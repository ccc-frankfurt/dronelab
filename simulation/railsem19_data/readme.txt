  
  ###################################################
  #                   RailSem19:                    #
  # A Dataset for Semantic Rail Scene Understanding #
  #                                                 #
  # readme.txt for Validation Data Version 1.0a     #
  #                                                 #
  # Email:   dashcamdataset@gmail.com               #
  # Website: wilddash.cc/railsem19                  #
  #      or  vitro-testing.com/railsem19            #
  #                                                 #
  # Authors:                                        #
  # Oliver Zendel, Markus Murschitz,                #
  # Marcel Zeilinger, Daniel Steininger,            #
  # Sara Abbasi, and Csaba Beleznai                 #
  #                                                 #
  # from AIT Austrian Institute of Technology GmbH  #
  #                                                 #
  ###################################################

*) Dataset description:
=======================

RailSem19 is a dataset for training and validation of semantic scene understanding solutions. The dataset focuses on both the rail domain and the cross-section between rail and road vehicles (e.g. railway crossings and joined tram/car traffic). 
A total of 8500 diverse scenes are supplied each with a FullHD RGB image and two types of annotations:
-) Geometry-based data (manually annotated bounding boxes, polylines, and polygons)
-) Dense semantic label id maps (a mixture of rasterization of the geometry-based data and weakly supervised GT)
Python example files are provided to illustrate how to interpret both annotation files.
The dense maps contain considerably more label noise compared to the geometry-based data. Please see the accompanying scientific publication for more information: wilddash.cc/railsem19

*) Selection of frames into validation, training, testing:
==========================================================

We do not recommend specific frames for validation, training, testing. 
See the file distribution.tsv for the randomly created split which was used in the paper's experiment.


*) Registration, Data protection and intellectual property rights:
==================================================================

The frames from RailSem19 are all extracted from source material that has already been publicly available. Some parts are from sources that are already available as CC-BY content. For all other material, we gathered the explicit acknowledgment of the original material's authors for our publication. The specific terms for all frames can be found in the accompanying license.txt file. All authors are referenced in the authors.txt file packaged with each data release.
We offer the frames without anonymization of license plates or faces. This is done to allow realistic testing and training for road-safety-critical algorithms but requires strict access control to the material. Do not share the frames with other people. Each person should register individually using our website. If you use frames in publications, you have to make sure that they do not allow identification of cars or people.

By accepting the license terms you agree to use this dataset only for the purpose of improving and testing computer vision solutions for rail and road safety (and scientific publications, presentations, and conversations about these topics). Do not use it for other purposes. We specifically exclude tasks that result in the identification of real-world identities (people and cars) or general usage as digital assets (e.g. for advertisements, art projects).

If we encounter misuse, we will have to replace all frames with anonymized versions. Please respect the terms to ensure the continued access to unbiased/unaltered frames!

You can file data protection and property rights issues to: dashcamdataset@gmail.com
Valid claims will lead to the removal of the respective frames or sequence from the dataset. This will not change naming / ids of any other file.

*) Naming schema:
=================
Release-Type = val | bench
Release-Name = rs19_<Release-Type-Id>
Sequence-Id = rs<%05i_index>
Frame-Id = <Sequence-Id>_<%04i_timecode[ms]>

Geometry annotations: <Frame-Id>.json
8uC3 RGB intensity image: <Frame-Id>.jpg
8uC1 label maps: <Frame-Id>.png

Release v1 note: We plan on providing at least the preceding and the succeeding frame for future versions of RailSem. As many source video files use a variable framerate, we preserve the timing information by using milliseconds instead of frame indices. The absolute timestamps from the original source material get converted to a relative timestamp of 1 second. This allows us enough room for timestamps in future sequence expansions without needing negative time values.


*) Folder contents, data format, and evaluation code:
=====================================================

Each release is packed into one zip files call <Release-Name>.zip; 
Additional content (e.g. preceding/succeeding frames; publication frames) is distributed in a file called <Release-Name>_<addition_type>.zip

/readme.txt      : this file
/license.txt     : license file describing license terms for the release
/author.txt      : listing of all content suppliers
/example-vis.py  : example python file to interpret/visualize annotations
/jpgs/<Release-Name>/<Frame-Id>.jpg   : 8uC3 RGB intensity images
/uint8/<Release-Name>/<Frame-Id>.png  : 8uC1 label map images
/jsons/<Release-Name>/<Frame-Id>.json : geometry annotations

*) Release History:

2019-06-06 v1.0 : initial release
2019-10-03 v1.0a: license in license.txt corrected to satisfy CC BY-NC-SA 4.0 aspect of pre-trained InplaceABN model

*) Acknowledgment:
==================

This project received financial support from the Horizon 2020 program of the European Union under the grant of the AutoDrive project ‘Advancing fail-aware, fail-safe, and fail-operational electronic components, systems, and architectures for fully automated driving to make future mobility safer, affordable, and end-user acceptable’ (Grant No. 737469). Please visit www.autodrive-project.eu for more information.
In addition, we like to thank the Heidelberg Collaboratory for Image Processing (HCI) of the University of Heidelberg for their support.
Last but not least: Thanks to all authors who made this dataset possible by allowing the use of their material.
