#!/bin/bash

SCENE=$1
RUNNAME=$2

DATA_DIR="/home/ubuntu/xr-gs/data/nerf_llff_data/$SCENE"
RESULT_DIR="$DATA_DIR/results_$RUNNAME"

echo "Scene: $SCENE"
echo "Run name: $RUNNAME"
echo "Result dir: $RESULT_DIR"

mkdir -p "$RESULT_DIR"

CUDA_VISIBLE_DEVICES=0 \
python /home/ubuntu/xr-gs/gsplat/examples/simple_trainer.py xrgs \
    --data_dir "$DATA_DIR" --data_factor 1 \
    --result_dir "$RESULT_DIR"
