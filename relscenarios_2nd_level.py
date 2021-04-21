#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 12:10:40 2020

Relationship Scenarios: 2nd Level Analysis

@author: tuk12127
"""

import os
from glob import glob
import pandas as pd
import numpy as np
from nltools.stats import zscore
from nltools.data import Brain_Data, Design_Matrix


bids_dir = '/data/projects/relationship_knowledge/'
os.chdir(bids_dir)

all_runs_dir = bids_dir + 'derivatives/relscenarios_all/'
odd_runs_dir = bids_dir + 'derivatives/relscenarios_odd/'
evn_runs_dir = bids_dir + 'derivatives/relscenarios_evn/'


#subjs_list = ['sub-301', 'sub-651', 'sub-693', 'sub-695', 'sub-697', 'sub-699',
#              'sub-706', 'sub-715', 'sub-720', 'sub-721', 'sub-722', 'sub-724',
#              'sub-726', 'sub-727', 'sub-738', 'sub-739', 'sub-740', 'sub-743',
#              'sub-745', 'sub-747', 'sub-749', 'sub-753', 'sub-754', 'sub-759',
#              'sub-762', 'sub-763', 'sub-764', 'sub-765', 'sub-766', 'sub-767']

subjs_scan_info = pd.read_csv(bids_dir+'derivatives/mriqc/mriqc_summary_poor.csv')
subjs_list = list(subjs_scan_info['subject'].unique())


# Group Analysis

if not os.path.exists(all_runs_dir+'group'):
    os.makedirs(all_runs_dir+'group')
if not os.path.exists(odd_runs_dir+'group'):
    os.makedirs(odd_runs_dir+'group')
if not os.path.exists(evn_runs_dir+'group'):
    os.makedirs(evn_runs_dir+'group')


## 2nd-level random-effects GLM for all conditions
for cond in range(0,76):
    print('Performing 2nd-level GLM for condition '+str(cond+1)+' for all runs...')
    ### Find the 1st-level data for each subject
    beta_list_all = glob(os.path.join(all_runs_dir, 'sub-*', 'beta_'+"{0:03}".format(cond+1)+'.nii'))
    beta_list_all.sort()
    beta_dat_all = Brain_Data(beta_list_all, mask="derivatives/fmriprep/sub-301/ses-001/func/sub-301_ses-001_task-relscenarios_run-001_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz")
    
    ### Calculate the mean activation in each voxel across participants
    #f_mean = beta_dat.mean().plot()
    #beta_dat.mean().write(os.path.join(all_runs_dir,'group','beta_'+"{0:03}".format(cond+1)+'.nii.gz'))
    
    ### Perform one-sample t-test across all voxels
    t_stats_all = beta_dat_all.ttest()
    t_stats_all['t'].write(os.path.join(all_runs_dir,'group','cond_'+"{0:03}".format(cond+1)+'_tmap.nii'))
    
    
    ### Repeat for odd and even runs
    print('...odd runs...')
    beta_list_odd = glob(os.path.join(odd_runs_dir, 'sub-*', 'beta_'+"{0:03}".format(cond+1)+'.nii'))
    beta_list_odd.sort()
    beta_dat_odd = Brain_Data(beta_list_odd, mask="derivatives/fmriprep/sub-301/ses-001/func/sub-301_ses-001_task-relscenarios_run-001_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz")
    
    t_stats_odd = beta_dat_odd.ttest()
    t_stats_odd['t'].write(os.path.join(odd_runs_dir,'group','cond_'+"{0:03}".format(cond+1)+'_tmap.nii'))
    
    
    print('...even runs...')
    beta_list_evn = glob(os.path.join(evn_runs_dir, 'sub-*', 'beta_'+"{0:03}".format(cond+1)+'.nii'))
    beta_list_evn.sort()
    beta_dat_evn = Brain_Data(beta_list_evn, mask="derivatives/fmriprep/sub-301/ses-001/func/sub-301_ses-001_task-relscenarios_run-001_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz")
    
    t_stats_evn = beta_dat_evn.ttest()
    t_stats_evn['t'].write(os.path.join(evn_runs_dir,'group','cond_'+"{0:03}".format(cond+1)+'_tmap.nii'))



## 2nd-level t-teest for all conditions vs rest (fixation)
cont_list_all = glob(os.path.join(all_runs_dir, 'sub-*', 'tmap_relVfix.nii'))
cont_list_all.sort()
cont_dat_all = Brain_Data(cont_list_all, mask="derivatives/fmriprep/sub-301/ses-001/func/sub-301_ses-001_task-relscenarios_run-001_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz")

t_stats_all = cont_dat_all.ttest()
t_stats_all['t'].write(os.path.join(all_runs_dir,'group','tmap_relVfix.nii'))


