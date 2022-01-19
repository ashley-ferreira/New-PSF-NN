import json
import matplotlib.pyplot as plt
from HSCgetStars_func import HSCgetStars_main 
from HSCpolishPSF_func import HSCpolishPSF_main
import os


for k in range(219580,219620,2): 
    print(k)
    
    file_dir = '/arc/home/ashley/HSC_May25-lsst/rerun/processCcdOutputs/03074/HSC-R2/corr' # can generalize $USER in future

    for i in range(0,103):

        try:
            if i == 9:
                print('chip 9 broken, not including')
                continue 
            elif i == 32:
                print('chip 32 half broken, not including')
                continue

            if i<10:
                num_str = '00' + str(i)
            elif i<100:
                num_str = '0' + str(i)
            elif i>100:
                num_str = str(i)

            file_in = 'CORR-0' + str(k) + '-' + num_str + '.fits'
            file_psf = 'psfStars/CORR-0' + str(k) + '-' + num_str + '.psf_cleaned.fits'

            fixed_cutout_len = 111
            outFile = file_dir + '/' + file_in.replace('.fits', '_metadata_cutouts_savedFits.pickle')
            #final_file = dir+'/NN_data_' + str(fixed_cutout_len) + '/'+file_in.replace('.fits', str(count) + '_metadata_cutoutData.pickle')
            
            #if os.path.isfile(finalFile):
            #    print('HSCpolishPSF already successfully run, skipping to next')
            #else:
            HSCpolishPSF_main(fixed_cutout_len = 111, dir = file_dir, inputFile = file_in, cutout_file = outFile)

        except Exception as e: 
            print('FAILURE')
            print(e)    