# -*- coding: utf-8 -*-
"""
Spyder Editor

First and Second Level Analysis with nltools
"""

from nltools.data import Brain_Data
import glob
import os
from nilearn import plotting as niplt
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np


bids_dir = '/data/projects/relationship_knowledge/'
os.chdir(bids_dir)

all_runs_dir = bids_dir + 'derivatives/relscenarios_all/'
odd_runs_dir = bids_dir + 'derivatives/relscenarios_odd/'
evn_runs_dir = bids_dir + 'derivatives/relscenarios_evn/'


subjs_scan_info = pd.read_csv(bids_dir+'derivatives/mriqc/mriqc_summary_poor.csv')

subjs_list = list(subjs_scan_info['subject'].unique())
subjs_list = [subjs_list[-1]]

## Find preprocessed functional runs
#subj = 'sub-'+str(693)

mni_template = "derivatives/fmriprep/sub-301/ses-001/func/sub-301_ses-001_task-relscenarios_run-001_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz"

for subj in subjs_list:
    print('Starting 1st-level analysis for '+subj)
    #subj = 'sub-'+str(693)
    if not os.path.exists(all_runs_dir+subj):
        os.makedirs(all_runs_dir+subj)
    if not os.path.exists(odd_runs_dir+subj):
        os.makedirs(odd_runs_dir+subj)
    if not os.path.exists(evn_runs_dir+subj):
        os.makedirs(evn_runs_dir+subj)
    
    
    #func_runs = [f for f in glob.glob(bids_dir + '/derivatives/fmriprep/'+subj+'/ses-001/func/*preproc_bold.nii.gz', recursive=True)]
    func_runs = list('derivatives/fmriprep/'+subj+'/ses-001/func/'+subjs_scan_info[subjs_scan_info['subject']==subj]['run'].str[:-5]+'_space-T1w_desc-preproc_bold.nii.gz')
    func_runs.sort()
    #func_runs = func_runs[1:] + [func_runs[0]]
    func_run_nums =  [s.lstrip('0') for s in subjs_scan_info[subjs_scan_info['subject']==subj]['run'].str[-8:-5]]
    func_run_nums = [int(i) for i in func_run_nums]
    print('Number of functional runs for '+subj+': '+str(len(func_runs)))
    
    
    # Load the brain data
    ## Takes about 10 mins for all four datasets
    
    # Grab subject's T1 as a mask to keep analysis in subject space
    subj_t1 = "derivatives/fmriprep/"+subj+"/ses-001/func/"+subj+"_ses-001_task-relscenarios_run-001_space-T1w_desc-brain_mask.nii.gz"
    
    print("Loading brain data...")
    all_cat_run_data = Brain_Data(func_runs, mask=subj_t1)
    
    
    #odd_run_data = Brain_Data(func_runs[::2])
    #even_run_data = Brain_Data(func_runs[1::2])
    
    
    # Design Matrix
    
    ## Add design matrices to brain data objects
    all_cat_run_data.X = pd.read_csv(bids_dir+'/derivatives/fmriprep/'+subj+'/ses-001/func/'+subj+'_ses-001_task-relscenarios_run-all_cat_desc-design_matrix.csv')
    plt.figure(figsize=(30,15))
    plt.title(subj+" design matrix for all runs", fontsize =20)
    sns.heatmap(data=all_cat_run_data.X,vmin=-1,vmax=1, cmap=sns.color_palette("Greys"))
    plt.savefig(all_runs_dir+subj+'/design_matrix.png')
    plt.close()
    
    
    ### Create odd and even run brain data objects by splitting the all_cat_run_data accordingly
    # Runs are split by index, not by actual run number
    evn_run_nums = []
    odd_run_nums = []
    
    # Remove runs that did not pass qc
    #ex_run_nums = np.setdiff1d(range(1,11), func_run_nums)
    
    
    # Split odd and even runs from all run data
    odd_cat_run_data = Brain_Data(mask=subj_t1)
    odd_cat_run_data.X = pd.DataFrame()
    evn_cat_run_data = Brain_Data(mask=subj_t1)
    evn_cat_run_data.X = pd.DataFrame()
    
    evn_drop_list = []
    odd_drop_list = []
    
    for i in range(len(func_run_nums)):
        if (i % 2) == 0:
            odd_run_nums.append(func_run_nums[i])
            temp_data = all_cat_run_data[206*i:206*(i+1)]
            odd_cat_run_data = odd_cat_run_data.append(temp_data)
            evn_drop_list.append(i)
        else:
            evn_run_nums.append(func_run_nums[i])
            temp_data = all_cat_run_data[206*i:206*(i+1)]
            evn_cat_run_data = evn_cat_run_data.append(temp_data)
            odd_drop_list.append(i)
    
    
    # These run regressors are 0-indexed so subtract one
    #odd_drop_list = evn_run_nums #list(ex_run_nums) + evn_run_nums
    #evn_drop_list = odd_run_nums #list(ex_run_nums) + odd_run_nums
    odd_drop_list = [str(n) + '_poly_0' for n in odd_drop_list] + [str(n) + '_poly_1' for n in odd_drop_list]
    evn_drop_list = [str(n) + '_poly_0' for n in evn_drop_list] + [str(n) + '_poly_1' for n in evn_drop_list]
          
    odd_cat_run_data.X = odd_cat_run_data.X.drop(odd_drop_list, axis=1, errors='ignore')
    evn_cat_run_data.X = evn_cat_run_data.X.drop(evn_drop_list, axis=1, errors='ignore')
    
    
    plt.figure(figsize=(30,15))
    plt.title(subj+" design matrix for odd runs", fontsize =20)
    sns.heatmap(data=odd_cat_run_data.X,vmin=-1,vmax=1, cmap=sns.color_palette("Greys"))
    plt.savefig(odd_runs_dir+subj+'/design_matrix.png')
    plt.close()
        
    plt.figure(figsize=(30,15))
    plt.title(subj+" design matrix for even runs", fontsize =20)
    sns.heatmap(data=evn_cat_run_data.X,vmin=-1,vmax=1, cmap=sns.color_palette("Greys"))
    plt.savefig(evn_runs_dir+subj+'/design_matrix.png')
    plt.close()
    
    
    ## Estimate model for all voxels
    stats_all_runs = all_cat_run_data.regress()
    stats_odd_runs = odd_cat_run_data.regress()
    stats_evn_runs = evn_cat_run_data.regress()
    
    ## Visualize data in jupyter notebook
    #stats['beta'][77].iplot()
    
    # Save the betas maps for each condition for all, odd, and even runs
    for cond in range(0,78):
        stats_all_runs['beta'][cond].write(os.path.join(all_runs_dir,subj,'beta_'+"{0:03}".format(cond+1)+'.nii.gz'))
        stats_odd_runs['beta'][cond].write(os.path.join(odd_runs_dir,subj,'beta_'+"{0:03}".format(cond+1)+'.nii.gz'))
        stats_evn_runs['beta'][cond].write(os.path.join(evn_runs_dir,subj,'beta_'+"{0:03}".format(cond+1)+'.nii.gz'))
        
        temp_subj_mni_beta = Brain_Data(os.path.join(all_runs_dir,subj,'beta_'+"{0:03}".format(cond+1)+'.nii.gz'), 
                                        mask="derivatives/fmriprep/"+subj+"/ses-001/func/"+subj+"_ses-001_task-relscenarios_run-001_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz")
        temp_subj_mni_beta.write(os.path.join(all_runs_dir,subj,'beta_'+"{0:03}".format(cond+1)+'_space-MNI152NLin2009cAsym.nii.gz'))
    
    #niplt.plot_roi(all_runs_dir+subj+'/beta_'+"{0:03}".format(cond+1)+'.nii.gz',
    #              display_mode='x', cut_coords=range(-50, 52, 2), draw_cross=False)
    
    
    # Create contrast for all vs rest (fixation)
    c_relVfix = np.zeros(len(stats_all_runs['beta']))
    c_relVfix[list(range(0,76))] = 1/76
    c_relVfix[76] = -1
    #print(c_relVfix)
    
    allVfix_tmap = stats_all_runs['beta'] * c_relVfix
    
    allVfix_tmap.write(os.path.join(all_runs_dir,subj,'tmap_relVfix.nii'))













