#!/usr/bin/env python2
#
# Example to compare the faces in two images.
# Brandon Amos
# 2015/09/29
#
# Copyright 2015-2016 Carnegie Mellon University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import util
import time
import argparse
import cv2
import itertools
import os
import openface
import numpy as np
import scipy as sp
from matplotlib import pyplot as plt
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster, cut_tree
IMG_DIM = 96
np.set_printoptions(precision=2)

fileDir = os.path.dirname(os.path.realpath(__file__))
modelDir = os.path.join(fileDir, 'models')
dlibModelDir = os.path.join(modelDir, 'dlib')
openfaceModelDir = os.path.join(modelDir, 'openface')

parser = argparse.ArgumentParser()
parser.add_argument('imgs', type=str, nargs='+', help="Input images.")
parser.add_argument('--metaData')

args = parser.parse_args()

align = openface.AlignDlib(os.path.join(dlibModelDir, "shape_predictor_68_face_landmarks.dat"))
net = openface.TorchNeuralNet(os.path.join(openfaceModelDir, 'nn4.small2.v1.t7'), IMG_DIM)

no_face = set()
def getRep(img_path):
    bgrImg = cv2.imread(img_path)
    if bgrImg is None:
        no_face.add(img_path)
        print("Unable to load image: {}".format(img_path))
        return None
    rgbImg = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2RGB)
    bb = align.getLargestFaceBoundingBox(rgbImg)
    if bb is None:
        no_face.add(img_path)
        print("Unable to find a face: {}".format(img_path))
        return None
    aligned_face = align.align(IMG_DIM, rgbImg, bb,
                              landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
    if aligned_face is None:
        no_face.add(img_path)
        print("Unable to align image: {}".format(img_path))
        return None
    rep = net.forward(aligned_face)
    return rep

if args.metaData:
    metadata = util.parse_metadata_file_to_dict(args.metaData)

img_paths = list()
X = None
for img in args.imgs:
    print ("processing {}".format(img))
    if args.metaData and img not in metadata:
        continue
    rep = getRep(img)
    if rep is not None:
        img_paths.append(img)
        if X is None:
            X = rep
        else:
            X = np.vstack((X, rep))

distances = pdist(X, lambda u, v: np.dot(u - v, u - v))
Z = linkage(distances, 'average')
clusters = dict()
for k in range(1, 10):
    clusters = dict()
    T = fcluster(Z, k, 'maxclust')
    print("K: " + str(k))
    for i in range(len(img_paths)):
        char_id = metadata[img_paths[i]]['character_id']
        clusters[T[i]] = clusters.get(T[i], dict())
        clusters[T[i]][char_id] = clusters[T[i]].get(char_id, 0) + 1
    for c in clusters:
        print (c, sorted(clusters[c].items(), key=lambda x: -1 * x[1]))

