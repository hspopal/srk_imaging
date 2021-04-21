#!/bin/bash

cd /data/projects/relationship_knowledge/


# subjects: 301 651 653 693 695 697 699 700 701 706 715 716 719 720 721 722 723 724 726 727 730 738 739 740 743 745 747 749 751 753 754 759 761 762 763 764 765 766 767

# Read dicom headers and create heudiconv directory on linux machine (cla27562)
docker run --rm -it \
	-v /data/projects/relationship_knowledge:/base nipy/heudiconv:latest \
	-d /base/sourcedata/Olson-Relation_soc{subject}/*/DICOM/*.dcm \
	-o /base/ \
	-f reproin \
	-s 301 651 653 693 695 697 699 700 701 706 715 716 719 720 721 722 723 724 726 727 730 738 739 740 743 745 747 749 751 753 754 759 761 762 763 764 765 766 767 \
	-c none \
	--overwrite


#cp /data/projects/relationship_knowledge/nifti/.heudiconv/soc715/info/dicominfo.tsv /data/projects/relationship_knowledge/

# Unpack and create nifti files
docker run --rm -it \
	-v /data/projects/relationship_knowledge:/base nipy/heudiconv:latest \
	-d /base/sourcedata/Olson-Relation_soc{subject}/*/DICOM/*.dcm \
	-o /base/ \
	-f /base/code/heuristic.py \
	-s 301 651 653 693 695 697 699 700 701 706 715 716 719 720 721 722 723 724 726 727 730 738 739 740 743 745 747 749 751 753 754 759 761 762 763 764 765 766 767 \
	-ss 001 \
	-c dcm2niix -b \
	--overwrite

docker run --rm -it \
	-v /data/projects/relationship_knowledge:/base nipy/heudiconv:latest \
	-d /base/sourcedata/Olson-Relation_soc{subject}/*/DICOM/*.dcm \
	-o /base/ \
	-f /base/code/heuristic.py \
	-s 767 \
	-ss 001 \
	-c dcm2niix -b \
	--overwrite


# fmriprep
## Creating a singularity image https://fmriprep.readthedocs.io/en/stable/installation.html#singularity-container

#export SINGULARITYENV_TEMPLATEFLOW_HOME=~/work/relationship_knowledge/archive/templateflow

#for subj in ${subjects}; do
#    singularity run -B ${SINGULARITYENV_TEMPLATEFLOW_HOME:-$HOME/.cache/templateflow}:/home/tuk12127/work/relationship_knowledge/archive/templateflow \
#        --cleanenv archive/fmriprep.simg \
#        /home/tuk12127/work/relationship_knowledge /home/tuk12127/work/relationship_knowledge/derivatives \
#        participant \
#        --participant-label ${subj} \
#        --fs-license-file ~/work/license.txt \
#        --notrack
#done


## Command to run on owlsnest
#qsub code/fmriprep_hpc_v2.sh -v subj=651
for s in 754 759 761 762 763 764 765 766 767; do
	qsub code/fmriprep_qsiprep_mriqc_hpc.sh -v subj=$s
done


# qsiprep
singularity run -B ${SINGULARITYENV_TEMPLATEFLOW_HOME:-$HOME/.cache/templateflow}:/home/tuk12127/work/relationship_knowledge/archive/templateflow \
    --cleanenv archive/qsiprep-0.6.6.sif \
    /home/tuk12127/work/relationship_knowledge /home/tuk12127/work/relationship_knowledge/derivatives \
    participant \
	--participant-label 697 \
	--output-resolution 2.0 \
	--fs-license-file ~/work/license.txt \
	-w /home/tuk12127/work/relationship_knowledge/derivatives 


# Check fmriprep output
#wkhtmltopdf derivatives/fmriprep/sub-716.html /data/users/tuk12127/projects/sub-716.pdf
#rsync cla27562:/data/users/tuk12127/projects/sub-716.pdf ~/Desktop/datasets/relationship_knowledge/derivatives/fmriprep/


# mriqc on owlsnest
## Create singularity image https://bircibrain.github.io/computingguide/docs/fmri-preprocessing/mriqc.html#singularity
## This directory needs to be mapped since nodes do not have internet connection on Owlsnest
export SINGULARITYENV_TEMPLATEFLOW_HOME=~/work/relationship_knowledge/archive/templateflow

## Run mriqc
singularity run -B ${SINGULARITYENV_TEMPLATEFLOW_HOME:-$HOME/.cache/templateflow}:/home/tuk12127/work/relationship_knowledge/archive/templateflow \
    --cleanenv archive/mriqc_latest.sif \
	~/work/relationship_knowledge \
	~/work/relationship_knowledge/derivatives/mriqc participant \
	--participant_label 301 \
	--nprocs=10 \
	--verbose-reports

for s in 301 651 653 693 695 697 699 700 701 706 715 716 719 720 721 722 723 724 726 727 730 738 739 740 743 745 747 749; do
	qsub code/mriqc_hpc.sh -v subj=$s
done


# mriqc on linux for group

docker run -it --rm \
	-v /data/projects/relationship_knowledge/:/data:ro \
	-v /data/projects/relationship_knowledge/derivatives/mriqc:/out poldracklab/mriqc:latest /data /out group

### Check mriqc metrics: https://mriqc.readthedocs.io/en/stable/iqms/t1w.html#measures-based-on-information-theory

# Check FreeSurfer output
freeview -v  derivatives/freesurfer/sub-730/mri/T1.mgz  \
			 derivatives/freesurfer/sub-730/mri/brainmask.mgz  \
		 -f  derivatives/freesurfer/sub-730/surf/lh.white:edgecolor=yellow \
			 derivatives/freesurfer/sub-730/surf/lh.pial:edgecolor=red \
			 derivatives/freesurfer/sub-730/surf/rh.white:edgecolor=yellow \
			 derivatives/freesurfer/sub-730/surf/rh.pial:edgecolor=red



# Copy fmriprep qc output to local machine
for subj in 301 651 653 693 695 697 699 700 701 706 715 716 719 720 721 722 723 724 726 727 730 738 739 740 743 745 747 749 751 753 754 759 761 762 763 764 765 766 767; do
	mkdir sub-${subj}
	mkdir sub-${subj}/ses-001
	rsync -a cla27562:/data/projects/relationship_knowledge/derivatives/fmriprep/sub-${subj}.html ./
	rsync -a cla27562:/data/projects/relationship_knowledge/derivatives/fmriprep/sub-${subj}/figures sub-${subj}/
	rsync -a cla27562:/data/projects/relationship_knowledge/derivatives/fmriprep/sub-${subj}/ses-001/figures sub-${subj}/ses-001/
done

for subj in 767; do
	rsync -a cla27562:/data/projects/relationship_knowledge/derivatives/fmriprep/sub-${subj}.html ./
	rsync -a cla27562:/data/projects/relationship_knowledge/derivatives/fmriprep/sub-${subj}/figures sub-${subj}/
	rsync -a cla27562:/data/projects/relationship_knowledge/derivatives/fmriprep/sub-${subj}/ses-001/figures sub-${subj}/ses-001/
done


### Subjects to exclude
"719: serious artifacts in T1 and EPIs from retainer on bottom teeth"
"730: ghosting and large motion in some middle run (see mriqc output)"
"723: discontinued after 4 functional runs"



# Check to see if all subjects have preprocessed BOLD runs
for subj in 301 651 653 693 695 697 699 700 701 706 715 716 719 720 721 722 723 724 726 727 730 738 739 740 743 745 747 749; do
	echo ${subj}
	ls derivatives/fmriprep/sub-${subj}/ses-001/func/sub-${subj}_ses-001_task-relscenarios_run-00*preproc_bold.nii.gz | wc | awk '{print $1}'
done




# subjects: 301 651 693 695 697 699 706 715 720 721 722 724 726 727 738 739 740 743 745 747 749
# Subjects to add: 
# Subjects to possbily add:     
# Subjects that still have issues: 653 (missing scan), 700, 701 716














