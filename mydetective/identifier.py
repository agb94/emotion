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
import time
import argparse
import cv2
import itertools
import os
import openface
import numpy as np
import scipy as sp
import scipy.cluster.vq
import scipy.spatial.distance
from collections import Counter
from shutil import copyfile
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from util import *

IMG_DIM = 96
np.set_printoptions(precision=2)

fileDir = os.path.dirname(os.path.realpath(__file__))
modelDir = os.path.join(fileDir, 'models')
dlibModelDir = os.path.join(modelDir, 'dlib')
openfaceModelDir = os.path.join(modelDir, 'openface')
align = openface.AlignDlib(os.path.join(dlibModelDir, "shape_predictor_68_face_landmarks.dat"))
net = openface.TorchNeuralNet(os.path.join(openfaceModelDir, 'nn4.small2.v1.t7'), IMG_DIM)

def get_rep(img_path):
    bgrImg = cv2.imread(img_path)
    if bgrImg is None:
        # print("Unable to load image: {}".format(img_path))
        return None
    rgbImg = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2RGB)
    bb = align.getLargestFaceBoundingBox(rgbImg)
    if bb is None:
        # print("Unable to find a face: {}".format(img_path))
        return None
    aligned_face = align.align(IMG_DIM, rgbImg, bb,
                              landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
    if aligned_face is None:
        # print("Unable to align image: {}".format(img_path))
        return None
    rep = net.forward(aligned_face)
    return rep

def gap(reps, nrefs=100, ks=range(1, 11)):
    # Input
    # rep: list of representations
    # label: list of labels for each representation
    shape = reps.shape
    tops = reps.max(axis=0)
    bots = reps.min(axis=0)
    dst = scipy.spatial.distance.euclidean
    dists = sp.matrix(sp.diag(tops-bots))
    rands = sp.random.random_sample(size=(shape[0],shape[1],nrefs))
    for i in range(nrefs):
        rands[:,:,i] = rands[:,:,i]*dists+bots
    gaps = sp.zeros((len(ks),))
    for (i,k) in enumerate(ks):
        (kmc,kml) = sp.cluster.vq.kmeans2(reps, k)
        disp = sum([dst(reps[m,:],kmc[kml[m],:]) for m in range(shape[0])])
        refdisps = sp.zeros((rands.shape[2],))
        for j in range(rands.shape[2]):
            (kmc,kml) = sp.cluster.vq.kmeans2(rands[:,:,j], k)
            refdisps[j] = sum([dst(rands[m,:,j],kmc[kml[m],:]) for m in range(shape[0])])
        gaps[i] = scipy.mean(scipy.log(refdisps))-scipy.log(disp)

    return np.around(gaps, decimals=2)

def firstmax_index(l, threshold=0.01):
    prev = None
    for i, now in enumerate(l):
        if prev is None or now > prev + threshold:
            prev = now
            continue
        return i - 1
    return i

def cluster(metadata_file_path, start=None, end=None, K=None, debugging=False):
    metadata = parse_metadata_file_to_dict(metadata_file_path)
    img_paths = list()
    X = None
    for img in metadata:
        if start is not None and end is not None and metadata[img]['frame_number'] not in range(start, end):
            continue
        if debugging:
            print ("processing {}".format(img))
        rep = get_rep(img)
        if rep is not None:
            img_paths.append(img)
            if X is None:
                X = rep
            else:
                X = np.vstack((X, rep))
    if K is None:
        gap_statistics = gap(X)
        if debugging:
            print (gap_statistics)
        K = firstmax_index(gap_statistics) + 1
            
    if debugging:
        print ("K: {}".format(K))

    (kmc,kml) = sp.cluster.vq.kmeans2(X, K)
    # kmeans = KMeans(n_clusters=K, random_state=0).fit(X)
    # Debugging
    if debugging:
        cluster_dirs = dict()
        for k in range(int(K)):
            cluster_dir = os.path.join(os.path.dirname(img_paths[0]), str(k))
            if not os.path.exists(cluster_dir):
                os.mkdir(cluster_dir)
            cluster_dirs[k] = cluster_dir

        for i in range(len(img_paths)):
            img_path = img_paths[i]
            c = kml[i]
            metadata[img_paths[i]]['character_id'] = c
            copyfile(img_path, os.path.join(cluster_dirs[c], os.path.basename(img_path)))

    write_metadata_file(metadata_file_path, metadata)
    return K

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('metadata', type=str, help="Metadata file path.")
    parser.add_argument('-K', type=int)
    parser.add_argument('--start', type=int)
    parser.add_argument('--end', type=int)
    args = parser.parse_args()
    cluster(args.metadata, start=args.start, end=args.end, K=args.K, debugging=True)
