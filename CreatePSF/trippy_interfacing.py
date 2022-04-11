from HSCgetStars_func import HSCgetStars_main 

import os
import sys
import numpy as np
import matplotlib.pyplot as pyl
import pickle

import keras
import matplotlib as mpl
import math 

from trippy import psf, psfStarChooser

from astropy.visualization import interval, ZScaleInterval
from astropy.io import fits
import matplotlib.pyplot as plt

zscale = ZScaleInterval()

# not actually sure about inputs?
# not sure if this is actually useful?

def NN_PSF_star_chooser(cutouts, xs, ys, model_dir_name, min_num_stars=10, max_stars=25, SNR_proxy_cutoff=10.0, conf_cutoff=0.95):
    '''
    Final product of NN-PSF project

    Requirements: provided on backend from trippy

        folder NN_PSF which contains: FILES IN SAME directory?
            NN_PSF_model: 
            regularization_data:


    Parameters: provided by user   

        cutouts (arr): 3D array conisting of 2D image data for each cutout

        xs (arr): 1D array containing central x position of cutout 

        ys (arr): 1D array containing central y position of cutout 

        + optional other parameters for fine tunning

    Returns:
        
        None
    
    '''

    def regularize(cutouts, mean, std):
        '''
        Helper function to regularize cutouts

        Parameters:

            cutouts (arr): cutouts to be regularized

            mean (float): mean used in training data regularization  

            std (float): std used in training data regularization

        Returns:

            regularized_cutout (arr): regularized cutout
        
        '''
        cutouts = np.asarray(cutouts).astype('float32')
        cutouts -= mean
        cutouts /= std
        w_bad = np.where(np.isnan(cutouts))
        cutouts[w_bad] = 0.0
        regularized_cutout = cutouts

        return regularized_cutout

    def crop_center(img, cropx, cropy):
        '''
        Helper function to crop img around center to desired (cropx, cropx) size
        
        Taken from stack overflow: 
        https://stackoverflow.com/questions/39382412/crop-center-portion-of-a-numpy-image

        Parameters:    

            img (arr): image to be cropped

            cropx (int): full width of desired cutout

            cropy (int): full height of desired cutout

        Returns:
            
            xs_best (arr): x coordinates of best stars in image
            
            ys_best (arr): y coordinates of best stars in image

        '''
        x,y = img.shape 
        startx = x//2 - (cropx//2)
        starty = y//2 - (cropy//2)
        cropped_img = img[int(startx):int(startx+cropx), int(starty):int(starty+cropy)]

        return cropped_img

    # load previously trained Neural Network 
    model_found = False 
    for file in os.listdir(model_dir_name):
        if file.startswith('model_'):
            model = keras.models.load_model(model_dir_name + file)
            model_found = True
            break
    if model_found == False: 
        print('ERROR: no model file in', model_dir_name)
        sys.exit()

    # load training set std and mean
    with open(model_dir_name + 'regularization_data.pickle', 'rb') as han:
        [std, mean] = pickle.load(han)

    # use std and mean to regularize cutout
    cutouts = regularize(cutouts, mean, std)

    # algorithm to find best stars in image
    xs_best = []
    ys_best = []
    cn_prob = []
    output = model.predict(cutouts)
    for i in range(len(cutouts)):
        good_probability = output[i][1]
        cn_prob.append(good_probability) 

    cn_prob, xs, ys, cutouts = zip(*sorted(zip(cn_prob, xs, ys, cutouts), reverse = True))

    saved_stars = 0
    for i in range(len(cutouts)): 
        if saved_stars < max_stars:
            good_probability = cn_prob[i]
            center = crop_center(cutouts[i],5,5)
            sum_c = center.sum()
            SNR_proxy = math.sqrt(sum_c)
            if SNR_proxy > SNR_proxy_cutoff and good_probability > conf_cutoff:       
                xs_best.append(xs[i])
                ys_best.append(ys[i])
                saved_stars += 1 

    if saved_stars < min_num_stars: 
        print('You requested a minimum of', min_num_stars)
        print('However there are only', saved_stars, 'with confidence >', \
            conf_cutoff, 'and SNR proxy >', SNR_proxy_cutoff)
        print('Please lower one of these numbers and try again to use NN_PSF')
        sys.exit()

    xs_best = np.array(xs_best)
    ys_best = np.array(ys_best)

    return xs_best, ys_best