# Building CUDA extensions with pip

**Worked example:** the [beast](https://github.com/paninski-lab/beast) repository, which needs `gsplat` compiled from source.

## 1. When you need this page

Most Python packages install from ready-made files ("wheels") and need nothing special. Some packages, such as `gsplat`, contain GPU code written in CUDA that must be compiled on your system, either while `pip install` runs or the first time you import the package. Compiling that code needs NVIDIA's CUDA compiler, `nvcc`, and it must be compiled against the exact PyTorch installed in your environment. This page shows how to do that on Nexus, step by step, using the beast repository as the example. The same steps work for other packages of this kind.

These packages are not installed centrally, because each one must be built against the PyTorch in your own environment, and projects often pin their own version or fork (beast pins a specific fork of gsplat). Nexus provides the tools; you build the package in your environment.

## 2. What Nexus provides

- **`miniforge3/25.3.0-3`**: conda, for creating your own Python environments with any Python version. After `module load miniforge3/25.3.0-3`, the command `conda activate` works right away; you do not need `conda init`.
- **`cuda/13.3.0`** (the default) and `cuda/13.4.1`: the CUDA toolkit, including `nvcc`. The module also sets `CUDA_HOME`, which PyTorch uses to find `nvcc`.
- **`ffmpeg/7.1.2-gcccore-14.3.0`**: FFmpeg, for packages that call the `ffmpeg` program (beast does). It includes NVIDIA GPU video encoding and decoding (NVENC/NVDEC).
- **Internet access from compute nodes** to PyPI, the PyTorch wheel index, GitHub and conda-forge, so the whole installation can run inside a GPU job.

## 3. The four rules

Every step below follows from these four rules. If an installation of this kind fails, check them first.

1. **The CUDA major version of `nvcc` must match the CUDA version PyTorch was built with.** PyTorch refuses to compile an extension when the major versions differ. On Nexus, install PyTorch's CUDA 13 build (the `cu130` wheels) and use `cuda/13.3.0`; both have major version 13. Install PyTorch yourself first, from the `cu130` index, rather than letting another package pull in whatever PyTorch build pip chooses.
2. **Compile for all Nexus GPU types** by setting `TORCH_CUDA_ARCH_LIST="8.9;10.0;12.0"`. The three numbers are the GPU generations on Nexus: 8.9 for the L40, 10.0 for the B200 and 12.0 for the RTX PRO 6000 Blackwell. Without this variable, PyTorch compiles only for the GPU in the job where you build, and your package fails with "no kernel image is available" on the other GPU types.
3. **Install the build tools first and use `pip install --no-build-isolation`.** Normally pip builds each package in a separate, temporary environment that does not contain your PyTorch, so the CUDA build cannot find it. `--no-build-isolation` makes pip build with what is already installed in your environment, which is why `setuptools`, `wheel`, `ninja` and the package's own build tools must be installed before it. `ninja` makes the compilation much faster.
4. **Build inside a Slurm job, not on the login node.** Compiling CUDA code takes many CPU cores and a lot of memory for several minutes. Set `MAX_JOBS` to the number of cores you asked for, so the build uses them all.

## 4. Where to keep things

By default, conda, pip and the build put their downloads, caches and temporary files in your home folder and in `/tmp`. A PyTorch environment alone takes several GB, so the steps below keep everything in your scratch folder instead. If you want to keep the environment long-term, use your project storage instead of scratch: set `WORK` in step 2 to a folder in your project storage, and everything else follows.

- `CONDA_PKGS_DIRS`: where conda keeps the packages it downloads.
- `PIP_CACHE_DIR`: where pip keeps downloads and the packages it compiled. A later reinstall of the same version reuses the compiled package instead of compiling again.
- `TMPDIR`: where pip unpacks and compiles packages while it installs them.
- `conda create -p <path>`: creates the environment at a path you choose, instead of the default `~/.conda/envs` in your home folder.

## 5. Step by step: beast with gsplat

### Step 1: start an interactive GPU job

Use the shared `gpu-rtxpro` partition for building. Replace `<your-account>` with your Slurm account. A one-hour limit is enough and usually starts sooner.

```bash
salloc -A <your-account> -p gpu-rtxpro --gpus=1 -c 16 --mem=64G -t 01:00:00
hostname
nvidia-smi --query-gpu=name,compute_cap --format=csv,noheader
```

**Expected output:** `salloc: Granted job allocation <jobid>`, a compute node name such as `atl1-1-01-007-17-0.pace.gatech.edu`, and `NVIDIA RTX PRO 6000 Blackwell Server Edition, 12.0`.

### Step 2: point downloads, caches and temporary files at scratch

```bash
export WORK=/storage/scratch/$USER
export CONDA_PKGS_DIRS=$WORK/conda-pkgs
export PIP_CACHE_DIR=$WORK/pip-cache
export TMPDIR=$WORK/tmp && mkdir -p $TMPDIR
```

**Expected output:** nothing.

### Step 3: create and activate a Python environment

beast asks for Python 3.10.

```bash
module load miniforge3/25.3.0-3
conda create -y -p $WORK/envs/beast python=3.10
conda activate $WORK/envs/beast
which python
python --version
```

**Expected output:** your prompt starts with `(beast)`, then `/storage/scratch/<you>/envs/beast/bin/python` and `Python 3.10.x`.

### Step 4: install PyTorch's CUDA 13 build and check it

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu130
python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available()); print(torch.cuda.get_arch_list())"
```

**Expected output** (versions as of November 2026):

```
2.14.1+cu130 13.0 True
['sm_75', 'sm_80', 'sm_86', 'sm_90', 'sm_100', 'sm_120']
```

The important parts are `13.0` (CUDA major version 13, matching `cuda/13.3.0`) and `True` (PyTorch sees the GPU).

### Step 5: load nvcc and set up the build

```bash
module load cuda/13.3.0
nvcc --version | tail -2
echo $CUDA_HOME
export TORCH_CUDA_ARCH_LIST="8.9;10.0;12.0"
export MAX_JOBS=16
pip install setuptools wheel ninja
```

**Expected output:** `Cuda compilation tools, release 13.3, V13.3.33` and `/usr/local/nexus-apps/easybuild/software/CUDA/13.3.0`. `MAX_JOBS` matches the 16 cores requested with `-c 16` in step 1.

### Step 6: install the package

For beast, install its build tools, then install beast from its repository. This also downloads and compiles gsplat.

```bash
pip install lightning poetry-core
cd $WORK && git clone https://github.com/paninski-lab/beast && cd beast
pip install -e . --no-build-isolation
```

**Expected output:** the line `Building wheel for gsplat (pyproject.toml): still running...` appears a few times while gsplat compiles, then `Successfully built beast-backbones gsplat` and a `Successfully installed ...` line that includes `gsplat-1.4.0` and `beast-backbones-2.0.3`. This took 7 minutes on 16 cores in our test.

### Step 7: check the result

First, check that the compiled gsplat library contains code for all three Nexus GPU types:

```bash
SO=$(find $CONDA_PREFIX/lib/python3.10/site-packages/gsplat -name '*.so' | head -1); echo "$SO"
cuobjdump --list-elf "$SO" | grep -o 'sm_[0-9]*' | sort -u
```

**Expected output:** the path of `gsplat/csrc.so`, then `sm_100`, `sm_120` and `sm_89`.

Then check that everything imports together, with FFmpeg loaded:

```bash
module load ffmpeg/7.1.2-gcccore-14.3.0
python -c "import beast, gsplat, cv2, torch; print('beast ok | gsplat', gsplat.__version__, '| opencv', cv2.__version__, '| cuda', torch.cuda.is_available())"
```

**Expected output:** `beast ok | gsplat 1.4.0 | opencv 5.0.0 | cuda True`.

## 6. Using the environment later

You only install once. In later sessions or batch jobs, load the modules and activate the environment by its path. We tested these commands interactively; a batch script uses the same commands. Example batch script:

```bash
#!/bin/bash
#SBATCH -A <your-account>
#SBATCH -p gpu-rtxpro
#SBATCH --gpus=1
#SBATCH -c 8
#SBATCH -t 02:00:00

module load miniforge3/25.3.0-3 cuda/13.3.0 ffmpeg/7.1.2-gcccore-14.3.0
conda activate /storage/scratch/$USER/envs/beast
python your_script.py
```

## 7. Other packages of this kind

Follow steps 1 to 5 as written, then install the package with `--no-build-isolation` in step 6, after installing whatever build tools its documentation lists. Two cases to know:

- **Installed from source** (a git URL, or `pip install .` in a clone): the CUDA code is compiled during `pip install`, as in the example above.
- **Compiled at first use**: some packages compile their CUDA code the first time you import or run them instead (for example, the gsplat package from PyPI). In that case, the same rules apply at that moment: `cuda/13.3.0` loaded and `TORCH_CUDA_ARCH_LIST` set when you first run it, inside a GPU job.

## 8. Troubleshooting

- **An error saying the detected CUDA version does not match the version used to compile PyTorch:** rule 1 is broken. Check `python -c "import torch; print(torch.version.cuda)"` and `nvcc --version`. If PyTorch is not a 13.x build, reinstall it from the `cu130` index (step 4).
- **"no kernel image is available for execution on the device":** the package was compiled without your GPU's generation (rule 2). Set `TORCH_CUDA_ARCH_LIST` as in step 5 and reinstall with `pip install --no-cache-dir --force-reinstall --no-build-isolation ...`. `--no-cache-dir` matters here: without it, pip reuses the package it compiled earlier, with the old GPU list.
- **The build fails because torch is not found, or reports a missing build tool:** rule 3. Install the build tools listed in the package's documentation into your environment, and add `--no-build-isolation`.
- **The build is killed, or the job runs out of memory while compiling:** lower `MAX_JOBS` (for example to 8), or request more memory with `--mem`.
- **`conda activate` does not work:** load the module first with `module load miniforge3/25.3.0-3`.
- **"Disk quota exceeded":** the caches went to your home folder. Set the variables from step 2 before installing.
