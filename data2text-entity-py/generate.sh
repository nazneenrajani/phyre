BASE=boxscore-data
IDENTIFIER=cc
MODEL_PATH=$BASE/gen_model/${IDENTIFIER}/roto/roto_acc_57.59_ppl_7.63_e25.pt

mkdir -p $BASE/gen

GPUID=0
python translate.py \
    -model $MODEL_PATH \
    -src $BASE/rotowire/src_valid.txt \
    -output $BASE/gen/roto_${IDENTIFIER}-beam5_gens.txt \
    -batch_size 5 \
    -max_length 850 \
    -min_length 150 \
    -gpu $GPUID
