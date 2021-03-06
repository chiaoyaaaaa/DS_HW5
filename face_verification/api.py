#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" API for face detection and verification """

import cv2 as cv
import numpy as np
from .utils import read_image, BGR2RGB, BGR2Gray, crop_face
from .facenet import triplet_loss
import tensorflow as tf
from keras import backend as K
from keras.models import load_model
from keras.preprocessing.image import img_to_array

xml = './xmls/haarcascade_frontalface_default.xml'  # Haar Cascade detector
# xml = './xmls/lbpcascade_frontalface_improved.xml'  # LBP Cascade detector

def cascade_detector(image, xml=xml, scale_factor=1.3, min_neighbors=5):
    """ implement Haar or LBP Feature-based Cascade Classifiers from OpenCV
        change the xml to specify Haar or LBP Cascade detector
        note: the image format should be BGR, instead of RGB
    """
    face_detector = cv.CascadeClassifier(xml)
    gray_img = BGR2Gray(image)
    faces = face_detector.detectMultiScale(gray_img, scaleFactor=scale_factor,
                                           minNeighbors=min_neighbors)

    if len(faces) == 0:
        raise ValueError('Error, there is no faces.')
    elif len(faces) > 1:
        raise ValueError('Error, multiple faces are found.')

    return faces


class face_verify(object):
    """ class for face verification """
    def __init__(self, 
                 path='./models/facenet-margin-03-final.h5', 
                 xml='./xmls/haarcascade_frontalface_default.xml'):
        """ initialize the face verification api """
        self.path = path
        self.xml = xml
        self.model = None
        
    def get_distance(self, path1, path2):
        """ get the distance between two images from path1 and path2 """
        if self.model is None:
            self._load_model()
            
        # pre-process the images
        img1 = self._process_image(path1)
        img2 = self._process_image(path2)
        
        # make predictions
        imgs = np.array([img1, img2])
        predictions = self.model.predict(imgs)
        
        pred1 = predictions[0]
        pred2 = predictions[1]
        
        # calculate the Euclidean distance
        distance = np.sqrt(np.sum(np.square(pred1 - pred2)))
        
        return img1, img2, distance
    
    def verify(self, path1, path2, threshold=0.2):
        """ verify whether or not images from path1 and path2 are same person """
        img1, img2, distance = self.get_distance(path1, path2)
        
        if distance < threshold:
            return img1, img2, True
        
        return img1, img2, False
    
    def _load_model(self):
        """ load the pre-defined cnn model for face verification """
#         self.model = load_model(self.path, custom_objects={'tf': tf})
        self.model = load_model(self.path)
        
        return
    
    def _process_image(self, path):
        """ read and pre-process the images """
        image = read_image(path)
        
        # frontal face detection
        faces = cascade_detector(image, xml=self.xml, scale_factor=1.5, min_neighbors=5)
        
        # crop frontal face areas
        crop = crop_face(image, faces, scale_factor=1.5, target_size=(96, 96))
        crop_rgb = BGR2RGB(crop)
        crop_array = np.array(crop_rgb, dtype=K.floatx()) / 255.0
        
        return crop_rgb

