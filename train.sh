#!/bin/bash
echo 'pnet training'
python3 preprocessing/gen_pnet_data.py
python3 preprocessing/assemble_pnet_imglist.py
python3 training/pnet/train.py

echo 'rnet training'
python3 preprocessing/gen_rnet_data.py
python3 preprocessing/assemble_rnet_imglist.py
python3 training/rnet/train.py

echo 'onet training'
python3 preprocessing/gen_landmark_48.py
python3 preprocessing/gen_onet_data.py
python3 preprocessing/assemble_onet_imglist.py
python3 training/onet/train.py
