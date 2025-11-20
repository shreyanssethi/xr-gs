CUDA_VISIBLE_DEVICES=0 python /home/ubuntu/xr-gs/gsplat/examples/simple_trainer.py default \
    --data_dir /home/ubuntu/xr-gs/data/nerf_llff_data/fern_xrgs --data_factor 1 \
    --result_dir /home/ubuntu/xr-gs/data/nerf_llff_data/fern_xrgs/$1
