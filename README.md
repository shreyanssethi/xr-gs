# xr-gs
Cross Resolution Gaussian Splatting (XR-GS)

**Instructions to build environment (Do on AWS Instance with CUDA)**
```
conda env create -f environment.yml
pip install git+https://github.com/nerfstudio-project/gsplat.git
cd gsplat/
pip install --no-build-isolation -e .

pip install git+https://github.com/rahul-goel/fused-ssim@328dc9836f513d00c4b5bc38fe30478b4435cbb5
pip install git+https://github.com/nerfstudio-project/nerfview@4538024fe0d15fd1a0e4d760f3695fc44ca72787
pip install git+https://github.com/rmbrualla/pycolmap@cc7ea4b7301720ac29287dbe450952511b32125e
pip install git+https://github.com/harry7557558/fused-bilagrid@90f9788e57d3545e3a033c1038bb9986549632fe -->
'''