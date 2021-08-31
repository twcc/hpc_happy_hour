# HPC 的快樂時光 ( HPC happy hour)

## introduction
- 提供適用 Taiwania 2 環境的 Open MPI 容器範本，能依此範本建立屬於你的跨節點應用程式
- 容器跨節點成功與否的關鍵，在於容器內編譯的 library (如 pmi2/pmix/mlnx_ofed/gdrcopy 等) 版本和實體機相容性
- **當實體機變動時，會更新此 repo**。用戶可能需依據此 repo 重建容器
- HPC 環境使用 [singularity](https://sylabs.io/singularity) 容器
- 容器範本使用 [HPC Container Maker (HPCCM)](https://github.com/NVIDIA/hpc-container-maker) 撰寫(你可能會需要了解一下 HPCCM 使用方式)
- 靈感來自於 [Building HPC Containers Demystified](https://developer.nvidia.com/blog/building-hpc-containers-demystified)

## 使用 singularity 容器跨節點的關鍵
- 搭配 singularity 容器跨節點可使用 3 種方法
  - 實體機的 srun (with pmi2/pmix，推薦使用此方法)
  - 實體機的 mpirun (需和容器內版本一致)
  - 容器內的 mpirun (此法有點複雜)
- 由於 pmi2 成熟穩定，**目前 twnia2 採 `srun with pmi2` 為主**
- 未來 slurm 升版可能會推向 with pmix 

## host version
- 簡述實體機目前重要項目版本
- CentOS 7.8 
- [mlnx_ofed 4.9-2.2.4.0](https://docs.mellanox.com/display/MLNXOFEDv492240/)
- [gdrcopy 2.2](https://github.com/NVIDIA/gdrcopy/releases/tag/v2.1)
- knem 1.1.3 (with mlnx_ofed)
- slurm pmi2 18.08.8
- slurm with [pmix 2.2.2](https://github.com/openpmix/openpmix/tree/v2.2.2) 

## requirement
- follow 此 repo 你需要以下工具
  - [Singularity](https://sylabs.io/singularity)  >= 3.2  
  - [HPC Container Maker (HPCCM)](https://github.com/NVIDIA/hpc-container-maker)  >= 19.11
- 由於建立 singularity 容器需要 sudo 權限，建議可利用 TWCC VCS 環境建立 
  - 儘管是建立 CUDA 相關的容器，但在 build 的環境僅需要 CPU，不需要 GPU

## hpccm script 說明
- 主要參考自此[範例](https://github.com/NVIDIA/hpc-container-maker/tree/master/recipes/osu_benchmarks)
- `common.py` : 適用 twnia2 的基礎 Open MPI 的 hpccm 腳本，也就是實體機有變動，會更新此腳本
- 採用 multi stage build 方式，可大大縮小容器大小
  - Stage0 (Development stage) : 主要用於編譯過程
  - Stage1 (Deployment stage) : 把 Stage0 編譯好的檔案，複製到 base 的容器

## 操作方式 - 以建立 OSU Micro-Benchmarks 為例 
- 下載 `common.py` 及 `osu_benchmarks/osu_benchmarks.py`
- 使用 hpccm 產生 singularity definition file
```bash=
hpccm --recipe osu_benchmarks.py --format singularity --singularity-version=3.2 > osu_benchmarks.def
```
- 建立容器
```bash=
sudo singularity build osu_benchmarks.sif osu_benchmarks.def > osu_benchmarks.log 2>&1
```
- 查看 log
```bash=
tail -f osu_benchmarks.log 
```

## slurm job script
- 提交 slurm job 的範例腳本
> `module load singularity` 主要是導入 srun 搭配 singularity 所需環境變數  
> 實際上 singularity 已安裝於各個節點上  
```bash=
#!/bin/bash
#SBATCH --job-name=hello_singularity
#SBATCH --nodes=2
#SBATCH --gres=gpu:1 
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:10:00
#SBATCH --account=$project_id    
#SBATCH --partition=gtest

module purge
module load singularity

srun singularity exec --nv osu_benchmarks.sif get_local_rank osu_bw -d cuda D D
```
