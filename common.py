########
#  generic OpenMPI singularity recipe for twnia2
#  (ofed+ucx+cuda+openmpi)
#  update : 2021/08/31
#  
#  host: 
#  CentOS 7.8 x86_64
#  mlnx_ofed (4.9-2.2.4.0)
#  gdrcopy (2.1)
#  knem (1.1.3)
#  slurm/pmix (18.08.8/2.2.2)
#  
# ref : https://github.com/NVIDIA/hpc-container-maker/\
#       blob/master/recipes/osu_benchmarks/common.py
########

# container component version
# ---------------------------------
# mlnx_ofed 4.x userspace driver version
twnia2_mlnx_ofed = '4.9-2.2.4.0' 

# gdrcopy/knem userspace libarary version 
twnia2_gdrcopy = '2.2'
twnia2_knem = '1.1.3'

twnia2_ucx = '1.10.1'
twnia2_openmpi = '4.1.1'
# ---------------------------------

# Development stage
Stage0 += baseimage(image='nvcr.io/nvidia/cuda:11.4.1-devel-ubuntu18.04',
                    _as='devel')

# replace mirror site to NCHC free software labs
Stage0 += raw(singularity="sed -i 's#archive.ubuntu.com#free.nchc.org.tw#' /etc/apt/sources.list")

# compiler
Stage0 += gnu(fortran=True)

# mellanox legacy ofed
Stage0 += mlnx_ofed(version=twnia2_mlnx_ofed)

# communication libraries
Stage0 += gdrcopy(ldconfig=True, version=twnia2_gdrcopy)
Stage0 += knem(ldconfig=True, version=twnia2_knem)
Stage0 += ucx(version=twnia2_ucx,
              ofed=True, cuda=True,
              knem='/usr/local/knem',
              gdrcopy='/usr/local/gdrcopy',
              ldconfig=True,
              with_verbs=True,
              with_dm=True,
              enable_mt=True,
              enable_numa=True,
              enable_devel_headers=True,
              enable_shared=True,
              disable_static=True,
              without_xpmem=True,
              without_java=True)

# with slurm pmi2 support
Stage0 += slurm_pmi2(prefix='/usr/local/pmi')

# OpenMPI
Stage0 += openmpi(cuda=True, ucx=True, infiniband=False, ldconfig=True, 
                  version=twnia2_openmpi,
                  disable_static=True,
                  enable_shared=True,
                  enable_mpi_fortran=True,
		  enable_mpi_cxx=True,
                  enable_mpi1_compatibility=True,
                  without_xpmem=True,
                  without_hcoll=True,
                  with_slurm=True,
                  with_pmi='/usr/local/pmi',
                  with_pmix='internal',
                  with_hwloc='internal',
                  with_libevent='internal',
                  with_platform='contrib/platform/mellanox/optimized')

# Deployment stage
Stage1 += baseimage(image='nvcr.io/nvidia/cuda:11.4.1-base-ubuntu18.04')
Stage1 += Stage0.runtime(_from='devel')

# performance and compatibility tuning
Stage1 += environment(variables={'CUDA_CACHE_DISABLE': '1',
                                 'LD_LIBRARY_PATH': '/usr/local/cuda/compat:$LD_LIBRARY_PATH',
                                 'SLURM_MPI_TYPE': 'pmi2',
                                 'OMPI_MCA_btl': '^openib,smcuda',
                                 'OMPI_MCA_osc': 'ucx',
                                 'OMPI_MCA_pml': 'ucx',
                                 'UCX_TLS': 'all',
                                 'UCX_MEMTYPE_CACHE': 'n'})
