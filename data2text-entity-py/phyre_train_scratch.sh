BASE=phyre-data
IDENTIFIER=cc
MODEL_PATH=$BASE/gen_model/${IDENTIFIER}/roto/roto_acc_57.59_ppl_7.63_e25.pt
VOCAB_PATH=$BASE/entity_preprocess/phyre.vocab.pt
EXP_TYPE=phyre_scratch

mkdir -p $BASE/gen_model/${IDENTIFIER}/${EXP_TYPE}

GPUID=0
python train.py \
    -data $BASE/entity_preprocess/phyre \
    -save_model $BASE/gen_model/${IDENTIFIER}/${EXP_TYPE}/${EXP_TYPE} \
    -encoder_type mean \
    -input_feed 1 \
    -layers 2 \
    -batch_size 5 \
    -feat_merge mlp \
    -seed 1234 \
    -report_every 100 \
    -gpuid $GPUID \
    -start_checkpoint_at 4 \
    -epochs 25 \
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
    -valid_batch_size 5
