import os
from os import path
import time
from datetime import date 
import sys
import numpy as np
import matplotlib.pyplot as pyl
import pickle
import heapq

import tensorflow as tf
from tensorflow.keras.optimizers import Adam

import keras
from keras.models import Sequential
from keras.layers import Dense, BatchNormalization, Flatten, Conv2D, MaxPool2D
from keras.layers.core import Dropout
from keras.callbacks import EarlyStopping, ModelCheckpoint

from sklearn.metrics import confusion_matrix
from sklearn.utils.multiclass import unique_labels
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.utils import class_weight
from sklearn.utils.multiclass import unique_labels

from astropy.visualization import interval, ZScaleInterval

import matplotlib as mpl

# look in model for trained on and withheld imgs total 219580-219620
withheld_img = range(219580,) # RANDOM SELECT
#withheld_img = [219580, 219582, 219584, 219586, 219588] 
validation_size = 500 
size_of_data = validation_size//2
file_dir = '/arc/home/ashley/HSC_May25-lsst/rerun/processCcdOutputs/03074/HSC-R2/corr'
model_dir = '/arc/home/ashley/HSC_May25-lsst/rerun/processCcdOutputs/03074/HSC-R2/corr'
# need more specific model dir
model_dir_name = ''

zscale = ZScaleInterval()
batch_size = 16
good_cutouts = [] # label 1
bad_cutouts = [] # label 0
cutout_len = []
good_fwhm_lst = []
good_x_lst = []
good_y_lst = []
good_inputFile_lst = []
bad_fwhm_lst = []
bad_x_lst = []
bad_y_lst = []
bad_inputFile_lst = []
np.random.seed(432)
max_size = 111 

data_pull = 'saved'

# earlier, we set to train on selection from (219590,219620)
# here we validate on 219580 (and can also look at up to 88)

# load specific image (all CCDs) cutouts
files_counted = 0
try:
    if data_pull == 'scratch':
        for filename in os.listdir(file_dir+ '/NN_data_metadata_111'):
            if filename.endswith("metadata_cutoutData.pickle") and os.path.getsize(filename) > 0:
                #print(files_counted, size_of_data)
                if files_counted >= size_of_data:
                    break
                print(files_counted, size_of_data)
                #print('file being processed: ', filename)

                with open(file_dir + '/NN_data_metadata_111/' + filename, 'rb') as f:
                    [n, cutout, label, y, x, fwhm, inputFile] = pickle.load(f)

                imgFile = int(inputFile[6:12])
                if len(cutout) > 0 and imgFile in withheld_img:
                    if cutout.shape == (111,111):
                        if label == 1:
                            good_x_lst.append(x)
                            good_y_lst.append(y)
                            good_fwhm_lst.append(fwhm)
                            good_inputFile_lst.append(inputFile)
                            good_cutouts.append(cutout)
                            files_counted += 1
                        elif label == 0:
                            bad_x_lst.append(x)
                            bad_y_lst.append(y)
                            bad_fwhm_lst.append(fwhm)
                            bad_inputFile_lst.append(inputFile)
                            bad_cutouts.append(cutout)
                            #files_counted += 1

        num_good_cutouts = len(good_cutouts)
        good_x_arr = np.array(good_x_lst)
        good_y_arr = np.array(good_y_lst)
        good_fwhm_arr = np.array(good_fwhm_lst)
        good_inputFile_arr = np.array(good_inputFile_lst)
        bad_x_arr = np.array(bad_x_lst)
        bad_y_arr = np.array(bad_y_lst)
        bad_fwhm_arr = np.array(bad_fwhm_lst)
        bad_inputFile_arr = np.array(bad_inputFile_lst)

        good_cutouts = np.array(good_cutouts)
        print(good_cutouts.shape)
        good_cutouts = np.expand_dims(good_cutouts, axis=3)
        print(good_cutouts.shape)

        label_good = np.ones(num_good_cutouts)

        bad_cutouts = np.array(bad_cutouts, dtype=object) 

        if True:
            number_of_rows = bad_cutouts.shape[0]
            random_indices = np.random.choice(number_of_rows, size=num_good_cutouts, replace=False)
            random_bad_cutouts = bad_cutouts[random_indices, :]
            bad_cutouts = np.expand_dims(random_bad_cutouts, axis=3)
            
            random_bad_x_arr = bad_x_arr[random_indices]
            random_bad_y_arr = bad_y_arr[random_indices]
            random_bad_fwhm_arr = bad_fwhm_arr[random_indices]
            random_bad_inputFile_arr = bad_inputFile_arr[random_indices]

            # add label 0
            label_bad = np.zeros(num_good_cutouts)

        # combine arrays 
        cutouts = np.concatenate((good_cutouts, bad_cutouts))
        fwhms = np.concatenate((good_fwhm_arr, random_bad_fwhm_arr))
        files = np.concatenate((good_inputFile_arr, random_bad_fwhm_arr))
        xs = np.concatenate((good_x_arr, random_bad_x_arr))
        ys = np.concatenate((good_y_arr, random_bad_y_arr))

        # make label array for all
        labels = np.concatenate((label_good, label_bad))

    else: 
        with open(file_dir + '/WITHHELD_' + str(max_size) + '_presaved_data.pickle', 'rb') as f:
            [cutouts, labels, xs, ys, fwhms, files] = pickle.load(f)

except Exception as Argument:
    # creating/opening a file
    err_log = open(model_dir_name + 'error_log.txt', 'a')

    # writing in the file
    err_log.write('Star_NN_valid.py' + str(Argument))
    
    # closing the file
    err_log.close()  

with open(model_dir + '/regularization_data.pickle', 'rb') as han:
    [std, mean] = pickle.load(han)

cutouts = np.asarray(cutouts).astype('float32')
cutouts -= mean
cutouts /= std
w_bad = np.where(np.isnan(cutouts))
cutouts[w_bad] = 0.0

<<<<<<< HEAD
# load model       
cn_model = keras.models.load_model(model_dir + '/Saved_Model/model_jan27_25k_250epochs')#1642735464.135405')

# show stats analsys
=======
# load model                          
cn_model = keras.models.load_model(model_dir + '/Saved_Model/model_jan27_25k_250epochs')

>>>>>>> 4cebad8c6ffdc741f969fcf24045c394e3cf99af
X_test = cutouts
y_test = labels
y_test_binary = keras.utils.np_utils.to_categorical(y_test, 2) #unique_labels)

X_test = np.asarray(X_test).astype('float32')
preds_test = cn_model.predict(X_test, verbose=1)

test_good_p = []
for p in preds_test:
    test_good_p.append(p[1])
    
bins = np.linspace(0, 1, 100)
pyl.hist(test_good_p, label = 'validation set confidence', bins=bins, alpha=0.5, density=True)
pyl.xlabel('Good Star Confidence')
pyl.ylabel('Count')
pyl.legend(loc='best')
pyl.show()
pyl.close()
pyl.clf()

results = cn_model.evaluate(X_test, y_test_binary, batch_size=batch_size)
print("validation loss, validation acc:", results)

zscale = ZScaleInterval()

X_test = np.squeeze(X_test, axis=3)
print(X_test.shape) 


# plot confusion matrix
fig2 = pyl.figure()

y_test_binary = np.argmax(y_test_binary, axis = 1)
preds_test_binary = np.argmax(preds_test, axis = 1)

cm = confusion_matrix(y_test_binary, preds_test_binary)
pyl.matshow(cm, cmap=mpl.cm.cool)

for (i, j), z in np.ndenumerate(cm):
    pyl.text(j, i, '{:0.1f}'.format(z), ha='center', va='center')

pyl.title('Confusion matrix')
pyl.colorbar(cmap=mpl.cm.cool)
pyl.xlabel('Predicted labels')
pyl.ylabel('True labels')
pyl.show()
pyl.clf()

# CONCISE THESE FOR LOOPS
fwhms_test_misclass = []
for i in range(len(preds_test)):
    
    if y_test[i] == 1 and preds_test[i][0] > 0.5:
        fwhms_test_misclass.append(fwhms[i])
        '''
        (c1, c2) = zscale.get_limits(y_test[i])
        normer3 = interval.ManualInterval(c1,c2)
        pyl.title('labeled good star, predicted bad star at conf=' + str(preds_test[i][1]))
        pyl.imshow(normer3(X_test[i]))
        pyl.show()
        pyl.close()
        '''

    elif y_test[i] == 0 and preds_test[i][1] > 0.5:
        fwhms_test_misclass.append(fwhms[i])
        '''
        (c1, c2) = zscale.get_limits(X_test[i])
        normer5 = interval.ManualInterval(c1,c2)
        pyl.title('labeled bad star, predicted good star at conf=' + str(preds_test[i][1])) 
        pyl.imshow(normer5(X_test[i]))
        pyl.show()
        pyl.close()
        '''
     
pyl.hist(fwhms, label = 'FWHM of full validation set', bins='auto', alpha=0.5) 
pyl.hist(fwhms_test_misclass, label = 'FWHM of misclassed validation set', bins='auto', alpha=0.5, color='pink') 
pyl.xlabel('FWHM')
pyl.ylabel('Count')
pyl.legend(loc='best')
pyl.show()
pyl.close()
pyl.clf()


misclass_80p = 0
good_class_80p = 0

# likely automatic way to do this but i didn't easily find
confidence_step = 0.001
confidence_queries = np.arange(confidence_step, 1, confidence_step) 
good_star_acc = []
bad_star_acc = []
recall = []
precision = []
fp_rate = []

for c in confidence_queries:
    good_stars_correct = 0
    good_stars_incorrect = 0
    good_stars_above_c = 0
    bad_stars_correct = 0
    bad_stars_incorrect = 0
    bad_stars_above_c = 0

    for i in range(len(preds_test)):
        '''
        if y_test[i] == 0 and preds_test[i][1] > c:
            #(c1, c2) = zscale.get_limits(X_test[i])
            #normer5 = interval.ManualInterval(c1,c2)
            #pyl.title('labeled bad star, predicted good star at conf=' + str(preds_test[i][1])) # so great you already have this
            #pyl.imshow(normer5(X_test[i]))
            #pyl.show()
            #pyl.close()
            misclass_80p += 1
        elif y_test[i] == 1 and preds_test[i][1] > c:
            good_class_80p += 1
        '''
        '''
        if preds_test[i][0] > c:
            bad_stars_above_c +=1
            if y_test[i] == 0:
                bad_stars_correct +=1
            elif y_test[i] == 1:
                bad_stars_incorrect +=1
        elif preds_test[i][1] > c:
            good_stars_above_c +=1 # wrong way? out of all preds?
            if y_test[i] == 1:
                good_stars_correct +=1 
            elif y_test[i] == 0:
                good_stars_incorrect +=1      
        '''
        if preds_test[i][1] > c:
            good_stars_above_c +=1 
            if y_test[i] == 1:
                good_stars_correct +=1 
            elif y_test[i] == 0:
                good_stars_incorrect +=1
        else:
            bad_stars_above_c +=1
            if y_test[i] == 0:
                bad_stars_correct +=1
            elif y_test[i] == 1:
                bad_stars_incorrect +=1
                   

    print('good', good_stars_correct, good_stars_incorrect, good_stars_above_c)
    print('bad', bad_stars_correct, bad_stars_incorrect, bad_stars_above_c)
    good_star_acc.append(good_stars_correct/good_stars_above_c)
    bad_star_acc.append(bad_stars_correct/bad_stars_above_c)
    # double check recall and precision calculations, switch to fp..
    recall.append(good_stars_correct/(good_stars_correct+bad_stars_incorrect)) 
    fp_rate.append(bad_stars_incorrect/(bad_stars_incorrect+bad_stars_correct)) 
    precision.append(good_stars_correct/(good_stars_correct+good_stars_incorrect))

pyl.title('Accuracy Curve')
pyl.plot(confidence_queries, good_star_acc, label='good star classificantion')
pyl.plot(confidence_queries, bad_star_acc, label='bad star clasification')
pyl.legend()
pyl.xlabel('Confidence cutoff for good star classification')
pyl.ylabel('Accuracy')
pyl.show()
pyl.close()
pyl.clf()

xy = np.arange(0,1, confidence_step)
#perfect_ROC = np.concatenate(([0],np.ones(int(1/confidence_step)-1)))
perfect_ROC = np.ones(len(xy))
perfect_ROC[0] = 0

pyl.title('ROC Curve')
pyl.plot(xy, xy, '--', label='random chance refence line')
pyl.plot(xy, perfect_ROC, '--', label='perfect classifier')
pyl.plot(fp_rate, recall, label='trained CNN') # fp too big
pyl.legend()
pyl.xlabel('False Positive Rate')
pyl.ylabel('True Positive Rate (Recall)')
pyl.show()
pyl.close()
pyl.clf()

#perfect_PR = np.concatenate((np.ones(len(confidence_queries)-1), [0]))
perfect_PR = np.ones(len(xy))
perfect_PR[len(xy)-1] = 0

pyl.title('PR Curve')
pyl.plot(xy, perfect_PR, '--', label='perfect classifier')
pyl.plot(recall, precision, label='trained CNN')
pyl.legend()
pyl.xlabel('Recall')
pyl.ylabel('Precision')
pyl.show()
pyl.close()
pyl.clf()
