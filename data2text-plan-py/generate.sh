BASE=boxscore-data
IDENTIFIER=cc
MODEL_PATH=$BASE/gen_model/${IDENTIFIER}/roto/roto_stage1_acc_73.0939_ppl_3.0744_e14.pt
MODEL_PATH2=$BASE/gen_model/${IDENTIFIER}/roto/roto_stage2_acc_58.7370_ppl_7.5918_e23.pt

mkdir -p $BASE/gen
mkdir -p $BASE/transform_gen
GPUID=1

# generate content plan
python translate.py \
  -model $MODEL_PATH \
  -src1 $BASE/rotowire/inf_src_valid.txt \
  -output $BASE/gen/roto_stage1_${IDENTIFIER}-beam5_gens.txt \
  -batch_size 10 \
  -max_length 80 \
  -gpu $GPUID \
  -min_length 35 \
  -stage1

# generates the content plan with records from input of content plan with indices
python scripts/create_content_plan_from_index.py \
    $BASE/rotowire/inf_src_valid.txt \
    $BASE/gen/roto_stage1_${IDENTIFIER}-beam5_gens.txt \
    $BASE/transform_gen/roto_stage1_${IDENTIFIER}-beam5_gens.h5-tuples.txt  \
    $BASE/gen/roto_stage1_inter_${IDENTIFIER}-beam5_gens.txt

# # accuracy of content plan in first stage can be evaluated (optional)
# python non_rg_metrics.py \
#   $BASE/transform_gen/roto-gold-val.h5-tuples.txt \
#   $BASE/transform_gen/roto_stage1_${IDENTIFIER}-beam5_gens.h5-tuples.txt

# generate output summary
python translate.py \
  -model $MODEL_PATH \
  -model2 $MODEL_PATH2 \
  -src1 $BASE/rotowire/inf_src_valid.txt \
  -tgt1 $BASE/gen/roto_stage1_${IDENTIFIER}-beam5_gens.txt \
  -src2 $BASE/gen/roto_stage1_inter_${IDENTIFIER}-beam5_gens.txt \
  -output $BASE/gen/roto_stage2_${IDENTIFIER}-beam5_gens.txt \
  -batch_size 10 \
  -max_length 850 \
  -min_length 150 \
  -gpu $GPUID
