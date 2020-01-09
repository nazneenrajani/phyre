BASE=phyre-data
EXP_NAME=phyre_lr_0.15_epoch_100_brnn
EXP_TYPE=initial_state_description
# EXP_TYPE=simulation_description
IDENTIFIER=$EXP_TYPE
MODEL_PATH=$BASE/gen_model/cc/roto/roto_acc_57.59_ppl_7.63_e25.pt
VOCAB_PATH=$BASE/${EXP_TYPE}/${EXP_TYPE}.vocab.pt

mkdir -p $BASE/gen_model/${EXP_TYPE}/${EXP_NAME}

GPUID=7
python train.py \
    -data $BASE/${EXP_TYPE}/${EXP_TYPE} \
    -save_model $BASE/gen_model/${EXP_TYPE}/${EXP_NAME}/${EXP_NAME} \
    -encoder_type brnn \
    -input_feed 1 \
    -layers 2 \
    -batch_size 5 \
    -feat_merge mlp \
    -seed 1234 \
    -report_every 100 \
    -gpuid $GPUID \
    -start_checkpoint_at 4 \
    -epochs 125 \
    -copy_attn \
    -truncated_decoder 100 \
    -feat_vec_size 600 \
    -word_vec_size 600 \
    -rnn_size 600 \
    -optim adagrad \
    -learning_rate 0.15 \
    -adagrad_accumulator_init 0.1 \
    -reuse_copy_attn \
    -start_decay_at 4 \
    -learning_rate_decay 0.97 \
    -entity_memory_size 300 \
    -valid_batch_size 1 \
    -train_from $MODEL_PATH \
    -override_vocab_path $VOCAB_PATH \
    -load_checkpoint_optim 0
