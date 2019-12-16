# Modified-Version-of-CycleGAN-Music-Style-Transfer
This repository contains modification of the code in Gino Brunner, Yuyi Wang, Roger Wattenhofer and Sumu Zhao's project CycleGAN-Music-Style-Transfer

The link to the original code repository is: https://github.com/sumuzhao/CycleGAN-Music-Style-Transfer

The code in this repository is modified so that data preprocessing can be done smoothly and all at once through the separate_files.py file in the home directory. In addition, setup.py in the home directory and the trainer/ directory are used to train the model on Google Cloud Platform. Certain functions are also modified so that os and other operations in an online environment on GCP AI Platform and GCS Storage.

To train the model on GCP, invoke:

gcloud ai-platform jobs submit training test_run_19 --job-dir $OUTPUT_PATH --runtime-version 1.14 --module-name trainer.task --package-path trainer/ --region us-west1 -- --dataset_A_dir $TRAIN_DATA_1 --dataset_B_dir $TRAIN_DATA_2  --type='cyclegan' --model='base' --phase='train' --log_dir $LOG_DIR --test_dir $TEST_PATH

--job-dir: online directory to store model checkpoint outputs

--region: configured region of your GCP project

--dataset_A_dir, --dataset_B_dir: online location of training datasets

--log_dir: directory to store training logs

--test_dir: directory to store test samples
