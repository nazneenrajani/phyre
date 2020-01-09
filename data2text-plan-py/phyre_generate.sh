BASE=phyre-data
EXP_NAME=phyre_lr_0.15_epoch_100
EXP_TYPE=initial_state_description
DATA_TYPE=train

IDENTIFIER=$EXP_TYPE
MODEL_DIR=$BASE/gen_model/${EXP_TYPE}/${EXP_NAME}
VOCAB_PATH=$BASE/${EXP_TYPE}/${EXP_TYPE}.vocab.pt

# # phyre_lr_0.15
# MODEL_PATH=phyre_lr_0.15_ppl_1.53_acc_86.13_e50.pt

# # phyre_lr_0.13
# MODEL_PATH=phyre_lr_0.13_ppl_1.68_acc_83.26_e50.pt

# phyre_lr_0.15_epoch_100
MODEL_PATH=phyre_lr_0.15_epoch_100_ppl_1.14_acc_95.58_e99.pt

mkdir -p $BASE/gen/${EXP_TYPE}/${EXP_NAME}

GPUID=0
python translate.py \
    -model ${MODEL_DIR}/${MODEL_PATH} \
    -src $BASE/phyre/${EXP_TYPE}/src_${DATA_TYPE}.txt \
    -output $BASE/gen/${EXP_TYPE}/${EXP_NAME}/${DATA_TYPE}_${MODEL_PATH}-beam5_gens.txt \
    -batch_size 1 \
    -max_length 850 \
    -min_length 150 \
    -gpu $GPUID
