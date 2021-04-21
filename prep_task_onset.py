# -*- coding: utf-8 -*-

import pandas as pd
from nltools.data import Design_Matrix
import numpy as np
import sys
sys.path.insert(0, '/data/projects/relationship_knowledge/code/')
import onsets_to_dm_relation

from nltools.utils import get_resource_path
from nltools.file_reader import onsets_to_dm
from nltools.data import Design_Matrix
import os


#subj = int(sys.argv[1])
#ses = int(sys.argv[2])


subj = 767
ses = 1
TR = 2.5
sampling_freq = 1/TR
all_runs = Design_Matrix(sampling_freq = sampling_freq)
all_runs_cat = Design_Matrix(sampling_freq = sampling_freq)
all_runs_cat_cov = Design_Matrix(sampling_freq = sampling_freq)
odd_runs = Design_Matrix(sampling_freq = sampling_freq)
even_runs = Design_Matrix(sampling_freq = sampling_freq)

bids_dir = '/data/projects/relationship_knowledge/'

fmri_run_data_dir = bids_dir+"derivatives/fmriprep/sub-"+str(subj)+"/ses-"+f'{ses:03}'+"/func/"
task_file = pd.read_csv(bids_dir+"archive/fMRI_task/task/data/relationships_scanner_"+str(subj)+".csv")
temp_event_dir = "~/Desktop/projects/relationship_knowledge/event_files/"
rel_idxs = pd.read_csv(bids_dir+"archive/fMRI_task/task/relationships_index.csv")

if task_file['SUBJECT_#'].iloc[0] == 'SUBJECT_#':
    task_file = task_file[1:]

task_file[[' TRIAL_START',' TRIAL_END']] = task_file[[' TRIAL_START',' TRIAL_END']].apply(pd.to_numeric)


# Load mriqc rating summaries
mriqc_summary = pd.read_csv(bids_dir+'derivatives/mriqc/mriqc_summary_poor.csv')

# Filter task runs for mriqc runs
mriqc_runs = list(mriqc_summary[mriqc_summary['subject'] == 'sub-'+str(subj)]['run'].str[-8:-5])



#for run in range(1,int(task_file[' RUN_#'].max())+1):        
for run in mriqc_runs:
    run = int(run.lstrip('0'))  
    #fmrip_task_file = pd.read_csv("/data/projects/relationship_knowledge/derivatives/fmriprep/sub-"+subj+"/ses-00"+ses+"/func/sub-"+subj+"_ses-00"+ses+"_task-relscenarios_run-00"+str(n)+"_space-MNI152NLin2009cAsym_desc-preproc_events.tsv", sep="\t")
    fmrip_task_file = pd.DataFrame(columns = ['onset', 'duration', 'trial_type', 'response_time'])
    fmrip_task_file['onset'] = task_file[task_file[' RUN_#']==run][' TRIAL_START']
    fmrip_task_file['duration'] = task_file[task_file[' RUN_#']==run][' TRIAL_END'] - task_file[task_file[' RUN_#']==run][' TRIAL_START']
    fmrip_task_file['trial_type'] = task_file[task_file[' RUN_#']==run][' STATE']
    fmrip_task_file['response_time'] = task_file[task_file[' RUN_#']==run][' RT']
    spm_onsets = pd.merge(rel_idxs, fmrip_task_file, on='trial_type') 
    
    # Make regressors for fixation
    #fmrip_task_file[['onset','duration','response_time']] = fmrip_task_file[['onset','duration','response_time']].apply(pd.to_numeric, errors='coerce')
    if fmrip_task_file['onset'].iloc[1] > fmrip_task_file['onset'].iloc[0] + fmrip_task_file['duration'].iloc[0]:
        fix_onset = fmrip_task_file['onset'].iloc[0] + fmrip_task_file['duration'].iloc[0]
        fix_duration = fmrip_task_file['onset'].iloc[1] - fix_onset
        if fix_duration > 1.0:
            new_row = {'onset':fix_onset, 'duration':fix_duration, 'trial_type':'fixation', 'response_time':0}
            fmrip_task_file = fmrip_task_file.append(new_row, ignore_index=True)
    fmrip_task_file = fmrip_task_file.sort_values(by=['onset'])
    fmrip_task_file = fmrip_task_file.reset_index(drop=True)
    for n in range(1,len(fmrip_task_file)):
        fix_onset = fmrip_task_file['onset'].iloc[n] + fmrip_task_file['duration'].iloc[n]
        fix_duration = fmrip_task_file['onset'].iloc[n+1] - fix_onset
        if fix_duration > 1.0:
            new_row = {'onset':fix_onset, 'duration':fix_duration, 'trial_type':'fixation', 'response_time':0}
            fmrip_task_file = fmrip_task_file.append(new_row, ignore_index=True)
    
    fix_dm = fmrip_task_file[fmrip_task_file['trial_type']=='fixation']
    if len(fmrip_task_file) < 106:
        if len(fix_dm[fix_dm['duration'] > 8]) < 2:
            fix_onset = fmrip_task_file['onset'].max() + 5
            new_row = {'onset':fix_onset, 'duration':10, 'trial_type':'fixation', 'response_time':0}
            fmrip_task_file = fmrip_task_file.append(new_row, ignore_index=True)
        elif len(fix_dm[fix_dm['duration'] > 6]) < 5:
            fix_onset = fmrip_task_file['onset'].max() + 5
            new_row = {'onset':fix_onset, 'duration':7.5, 'trial_type':'fixation', 'response_time':0}
            fmrip_task_file = fmrip_task_file.append(new_row, ignore_index=True)
        elif len(fix_dm[fix_dm['duration'] > 4]) < 12:
            fix_onset = fmrip_task_file['onset'].max() + 5
            new_row = {'onset':fix_onset, 'duration':5, 'trial_type':'fixation', 'response_time':0}
            fmrip_task_file = fmrip_task_file.append(new_row, ignore_index=True)
        elif len(fix_dm[fix_dm['duration'] > 2]) < 30:
            fix_onset = fmrip_task_file['onset'].max() + 5
            new_row = {'onset':fix_onset, 'duration':2.5, 'trial_type':'fixation', 'response_time':0}
            fmrip_task_file = fmrip_task_file.append(new_row, ignore_index=True)
    
    print('Prepping run '+str(run))
                   
    fmrip_task_file.to_csv(temp_event_dir+"sub-"+str(subj)+"_ses-"+str(f'{ses:03}')+"_task-relscenarios_run-"+str(f'{run:03}')+"_events.tsv", sep="\t", index=False)
    #spm_onsets.to_csv(temp_event_dir+"sub-"+str(subj)+"_ses-00"+str(ses)+"_task-relscenarios_run-00"+str(run)+"_events_spm.tsv", sep="\t", index=False)

    # 1) Load in onsets for this run
    onsetsFile = fmrip_task_file[['onset','duration','trial_type']]
    onsetsFile.columns = ['Onset', 'Duration', 'Stim']
    onsetsFile['Duration'] = 5
    dm = onsets_to_dm_relation.onsets_to_dm(onsetsFile, sampling_freq=sampling_freq, run_length=206, sort=True)
    dm['response_time'] = 0
    for col in dm.columns[:-3]:
        #print(fmrip_task_file[fmrip_task_file['trial_type'] == col]['response_time'])
        dm['response_time'].loc[dm[dm[col] != 0][col].index] = fmrip_task_file[fmrip_task_file['trial_type'] == col]['response_time'].iloc[0]
    #all_runs_cat = all_runs_cat.append(dm,axis=0)
    
    
    # 2) Convolve them with the hrf
    dm = dm.convolve()
    
    # 3) Load in covariates for this run
    add_regressors = pd.read_csv(fmri_run_data_dir+"sub-"+str(subj)+"_ses-"+str(f'{ses:03}')+"_task-relscenarios_run-"+str(f'{run:03}')+"_desc-confounds_regressors.tsv", sep="\t")
    
    mot_regressors = Design_Matrix(add_regressors[['trans_x','trans_y','trans_z','rot_x','rot_y','rot_z']], sampling_freq=sampling_freq)
    
    # 4) In the covariates, fill any NaNs with 0, add intercept and linear trends and dct basis functions
    cov = mot_regressors.fillna(0)
    
    # Retain a list of nuisance covariates (e.g. motion and spikes) which we'll also want to also keep separate for each run
    #cov_columns = cov.columns
    cov.columns = [e[2:] for e in cov.columns]
    cov = cov.add_poly(1)
    all_runs_cat_cov = all_runs_cat_cov.append(cov,axis=0)
    
    
    # 4) Join the onsets and covariates together
    full_dm = dm.append(cov, axis=1)
    #full_dm.to_csv(temp_event_dir+"sub-"+str(subj)+"_ses-00"+str(ses)+"_task-relscenarios_run-00"+str(run)+"_desc-design_matrix.tsv", sep="\t", index=False)
    full_dm_reidx = dm.append(cov, axis=1)
    full_dm_reidx.index = np.arange(len(dm)*run-1, len(dm) + len(dm)*run-1)
    
    
    # 5) Append it to the master Design Matrix keeping things separated by run
    all_runs = all_runs.append(full_dm_reidx,axis=0,unique_cols=full_dm.columns)
    all_runs_cat = all_runs_cat.append(full_dm)
    
    if (run % 2) == 0:
        even_runs = even_runs.append(full_dm_reidx,axis=0,unique_cols=full_dm.columns)
    else:
        odd_runs = odd_runs.append(full_dm_reidx,axis=0,unique_cols=full_dm.columns)
    
    
#all_runs.heatmap(vmin=-1,vmax=1)
#all_runs_cat = all_runs_cat.convolve()
#all_runs_cat = all_runs_cat.append(all_runs_cat_cov, axis=1)

even_runs.to_csv(temp_event_dir+"sub-"+str(subj)+"_ses-"+str(f'{ses:03}')+"_task-relscenarios_run-even_desc-design_matrix.csv", index=False)
odd_runs.to_csv(temp_event_dir+"sub-"+str(subj)+"_ses-"+str(f'{ses:03}')+"_task-relscenarios_run-odd_desc-design_matrix.csv", index=False)
all_runs.to_csv(temp_event_dir+"sub-"+str(subj)+"_ses-"+str(f'{ses:03}')+"_task-relscenarios_run-all_desc-design_matrix.csv", index=False)
all_runs_cat.to_csv(temp_event_dir+"sub-"+str(subj)+"_ses-"+str(f'{ses:03}')+"_task-relscenarios_run-all_cat_desc-design_matrix.csv", index=False)
print(temp_event_dir+"sub-"+str(subj)+"_ses-"+str(f'{ses:03}')+"_task-relscenarios_run-all_cat_desc-design_matrix.csv")

# All runs are clean, no need to remove any correlated regressors
#all_runs_cleaned = all_runs.clean(verbose=True)
#all_runs_cleaned.heatmap(vmin=-1,vmax=1)



# First Level Analysis
"""
from nistats.first_level_model import first_level_models_from_bids

data_dir = '/data/projects/relationship_knowledge/'
os.chdir(data_dir)

task_label = 'relscenarios'
space_label = 'MNI152nonlin2009aAsym'
derivatives_folder = 'derivatives/fmriprep'
models, models_run_imgs, models_events, models_confounds = \
    first_level_models_from_bids(
        data_dir, task_label, space_label,
        derivatives_folder=derivatives_folder,
        img_filters=[('desc', 'preproc')])"""





















