BASE=phyre-data
EXP_NAME=phyre_lr_0.15_epoch_100_brnn
EXP_TYPE=simulation_description
DATA_TYPE=train

IDENTIFIER=$EXP_TYPE
MODEL_DIR=$BASE/gen_model/${EXP_TYPE}/${EXP_NAME}
VOCAB_PATH=$BASE/${EXP_TYPE}/${EXP_TYPE}.vocab.pt

# # phyre_lr_0.15
# MODEL_PATH=phyre_lr_0.15_ppl_1.53_acc_86.13_e50.pt

# # phyre_lr_0.13
# MODEL_PATH=phyre_lr_0.13_ppl_1.68_acc_83.26_e50.pt

# # phyre_lr_0.15_epoch_100 (initial_state_description) - mean
# MODEL_PATH=phyre_lr_0.15_epoch_100_ppl_1.14_acc_95.61_e125.pt

# # phyre_lr_0.15_epoch_100 (simulation_description) - mean
# MODEL_PATH=phyre_lr_0.15_epoch_100_ppl_1.13_acc_96.13_e125.pt

# # phyre_lr_0.15_epoch_100_brnn (initial_state_description) - brnn
# MODEL_PATH=phyre_lr_0.15_epoch_100_brnn_ppl_1.14_acc_95.67_e125.pt

# phyre_lr_0.15_epoch_100_brnn (simulation_description) - brnn
MODEL_PATH=phyre_lr_0.15_epoch_100_brnn_ppl_1.14_acc_96.07_e125.pt

mkdir -p $BASE/gen/${EXP_TYPE}/${EXP_NAME}

GPUID=6
python translate.py \
    -model ${MODEL_DIR}/${MODEL_PATH} \
    -src $BASE/phyre/${EXP_TYPE}/src_${DATA_TYPE}.txt \
    -output $BASE/gen/${EXP_TYPE}/${EXP_NAME}/${DATA_TYPE}_${MODEL_PATH}-beam5_gens.txt \
    -batch_size 1 \
    -max_length 850 \
    -min_length 150 \
    -gpu $GPUID
