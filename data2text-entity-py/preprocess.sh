BASE=boxscore-data

mkdir $BASE/entity_preprocess
python preprocess.py \
    -train_src $BASE/rotowire/src_train.txt \
    -train_tgt $BASE/rotowire/tgt_train.txt \
    -valid_src $BASE/rotowire/src_valid.txt \
    -valid_tgt $BASE/rotowire/tgt_valid.txt \
    -save_data $BASE/entity_preprocess/roto \
    -src_seq_length 1000 \
    -tgt_seq_length 1000 \
    -dynamic_dict
