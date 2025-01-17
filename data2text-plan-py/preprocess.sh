BASE=boxscore-data

mkdir $BASE/preprocess
python preprocess.py \
  -train_src1 $BASE/rotowire/src_train.txt \
  -train_tgt1 $BASE/rotowire/train_content_plan.txt \
  -train_src2 $BASE/rotowire/inter/train_content_plan.txt \
  -train_tgt2 $BASE/rotowire/tgt_train.txt \
  -valid_src1 $BASE/rotowire/src_valid.txt \
  -valid_tgt1 $BASE/rotowire/valid_content_plan.txt \
  -valid_src2 $BASE/rotowire/inter/valid_content_plan.txt \
  -valid_tgt2 $BASE/rotowire/tgt_valid.txt \
  -save_data $BASE/preprocess/roto \
  -src_seq_length 1000 \
  -tgt_seq_length 1000 \
  -dynamic_dict \
  -train_ptr $BASE/rotowire/train-roto-ptrs.txt

python data_utils.py \
  -mode ptrs \
  -input_path $BASE/rotowire/train.json \
  -train_content_plan $BASE/rotowire/inter/train_content_plan.txt \
  -output_fi $BASE/rotowire/train-roto-ptrs.txt
