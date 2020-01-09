DESCRIPTION_TYPE=initial_state_description
mkdir -p phyre/${DESCRIPTION_TYPE}
python create.py \
  --mode "train" \
  --description_type ${DESCRIPTION_TYPE}
python create.py \
  --mode "dev" \
  --description_type ${DESCRIPTION_TYPE}
python create.py \
  --mode "test" \
  --description_type ${DESCRIPTION_TYPE}
cat phyre/${DESCRIPTION_TYPE}/src_dev.txt > phyre/${DESCRIPTION_TYPE}/src_dev_test.txt
cat phyre/${DESCRIPTION_TYPE}/src_test.txt >> phyre/${DESCRIPTION_TYPE}/src_dev_test.txt

DESCRIPTION_TYPE=simulation_description
mkdir -p phyre/${DESCRIPTION_TYPE}
python create.py \
  --mode "train" \
  --description_type ${DESCRIPTION_TYPE}
python create.py \
  --mode "dev" \
  --description_type ${DESCRIPTION_TYPE}
python create.py \
  --mode "test" \
  --description_type ${DESCRIPTION_TYPE}
cat phyre/${DESCRIPTION_TYPE}/src_dev.txt > phyre/${DESCRIPTION_TYPE}/src_dev_test.txt
cat phyre/${DESCRIPTION_TYPE}/src_test.txt >> phyre/${DESCRIPTION_TYPE}/src_dev_test.txt
