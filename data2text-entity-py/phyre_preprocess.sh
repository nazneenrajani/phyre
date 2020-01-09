BASE=phyre-data
TYPE=phyre

# EXP_TYPE=initial_state_description
EXP_TYPE=simulation_description
rm -rf $BASE/$EXP_TYPE
mkdir -p $BASE/$EXP_TYPE
python preprocess.py \
    -train_src $BASE/${TYPE}/${EXP_TYPE}/src_train.txt \
    -train_tgt $BASE/${TYPE}/${EXP_TYPE}/tgt_train.txt \
    -valid_src $BASE/${TYPE}/${EXP_TYPE}/src_dev.txt \
    -valid_tgt $BASE/${TYPE}/${EXP_TYPE}/tgt_dev.txt \
    -save_data $BASE/${EXP_TYPE}/${EXP_TYPE} \
    -src_seq_length 1000 \
    -tgt_seq_length 1000 \
    -dynamic_dict
