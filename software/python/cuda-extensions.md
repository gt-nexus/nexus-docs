# Building CUDA extensions with pip

Some Python packages contain GPU code written in CUDA that must be compiled on your system, either while `pip install` runs or the first time you import the package. Compiling that code needs NVIDIA's CUDA compiler, `nvcc`, and it must be compiled against the exact PyTorch installed in your environment. This page shows how to do that on Nexus for any such package. A tested example, the [beast](https://github.com/paninski-lab/beast) repository with its `gsplat` dependency, is at the end.

These packages are not installed centrally, because each one must be built against the PyTorch in your own environment, and projects often pin their own version or fork. Nexus provides the tools; you build the package in your environment.

## 1. What Nexus provides

- **`miniforge3/25.3.0-3`**: conda, for creating your own Python environments with any Python version. After `module load miniforge3/25.3.0-3`, the command `conda activate` works right away; you do not need `conda init`.
- **`cuda/13.3.0`** (the default) and `cuda/13.4.1`: the CUDA toolkit, including `nvcc`. The module also sets `CUDA_HOME`, which PyTorch uses to find `nvcc`.
- **Internet access from compute nodes** to PyPI, the PyTorch wheel index, GitHub and conda-forge, so the whole installation can run inside a GPU job.

## 2. The four rules

Every step below follows from these four rules. If an installation of this kind fails, check them first.

1. **The CUDA major version of `nvcc` must match the CUDA version PyTorch was built with.** PyTorch refuses to compile an extension when the major versions differ. On Nexus, install PyTorch's CUDA 13 build (the `cu130` wheels) and use `cuda/13.3.0`; both have major version 13. Install PyTorch yourself first, from the `cu130` index, rather than letting another package pull in whatever PyTorch build pip chooses.
2. **Compile for all Nexus GPU types** by setting `TORCH_CUDA_ARCH_LIST="8.9;10.0;12.0"`. The three numbers are the GPU generations on Nexus: 8.9 for the L40, 10.0 for the B200 and 12.0 for the RTX PRO 6000 Blackwell. Without this variable, PyTorch compiles only for the GPU in the job where you build, and your package fails with "no kernel image is available" on the other GPU types.
3. **Install the build tools first and use `pip install --no-build-isolation`.** Normally pip builds each package in a separate, temporary environment that does not contain your PyTorch, so the CUDA build cannot find it. `--no-build-isolation` makes pip build with what is already installed in your environment, which is why `setuptools`, `wheel`, `ninja` and the package's own build tools must be installed before it. `ninja` makes the compilation much faster.
4. **Build inside a Slurm job, not on the login node.** Compiling CUDA code takes many CPU cores and a lot of memory for several minutes. Set `MAX_JOBS` to the number of cores you asked for, so the build uses them all.

## 3. Where to keep things

By default, conda, pip and the build put their downloads, caches and temporary files in your home folder and in `/tmp`. A PyTorch environment alone takes several GB, so the steps below keep everything in your scratch folder instead. If you want to keep the environment long-term, use your project storage instead of scratch: set `WORK` in step 2 to a folder in your project storage, and everything else follows.

- `CONDA_PKGS_DIRS`: where conda keeps the packages it downloads.
- `PIP_CACHE_DIR`: where pip keeps downloads and the packages it compiled. A later reinstall of the same version reuses the compiled package instead of compiling again.
- `TMPDIR`: where pip unpacks and compiles packages while it installs them.
- `conda create -p <path>`: creates the environment at a path you choose, instead of the default `~/.conda/envs` in your home folder.

## 4. Step by step

### Step 1: start an interactive GPU job

Use the shared `gpu-rtxpro` partition for building. Replace `<your-account>` with your Slurm account. A one-hour limit is enough and usually starts sooner.

```bash
salloc -A <your-account> -p gpu-rtxpro --gpus=1 -c 16 --mem=64G -t 01:00:00
hostname
nvidia-smi --query-gpu=name,compute_cap --format=csv,noheader
```

**Expected output:** `salloc: Granted job allocation <jobid>`, a compute node name such as `atl1-1-01-007-17-0.pace.gatech.edu`, and `NVIDIA RTX PRO 6000 Blackwell Server Edition, 12.0`.

On Nexus, `salloc` opens your shell directly on the job's compute node (Nexus sets `LaunchParameters=use_interactive_step`), so the commands below run there without `srun`. If `hostname` ever shows a login node instead, run `srun --pty bash` first to get a shell on the compute node.

### Step 2: point downloads, caches and temporary files at scratch

```bash
export WORK=/storage/scratch/$USER
export CONDA_PKGS_DIRS=$WORK/conda-pkgs
export PIP_CACHE_DIR=$WORK/pip-cache
export TMPDIR=$WORK/tmp && mkdir -p $TMPDIR
```

**Expected output:** nothing.

### Step 3: create and activate a Python environment

Use the Python version your package supports; this example uses 3.10.

```bash
module load miniforge3/25.3.0-3
conda create -y -p $WORK/envs/myenv python=3.10
conda activate $WORK/envs/myenv
which python
python --version
```

**Expected output:** your prompt starts with `(myenv)`, then `/storage/scratch/<you>/envs/myenv/bin/python` and `Python 3.10.x`.

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

### Step 6: install your package

First install the build tools your package's documentation lists (for example `poetry-core` or `scikit-build-core`). Then install the package with `--no-build-isolation`, in whichever form its documentation gives:

```bash
pip install <package-name> --no-build-isolation                         # from PyPI
pip install git+https://github.com/<owner>/<repo> --no-build-isolation  # from a git URL
pip install -e . --no-build-isolation                                   # from inside a clone
```

**Expected output:** while the CUDA code compiles, pip prints `Building wheel for <package> (pyproject.toml): still running...` a few times, then `Successfully built <package>` and a `Successfully installed ...` line. Compiling for three GPU types takes several minutes.

Some packages do not compile during `pip install`, but the first time you import or run them instead (for example, the `gsplat` package from PyPI). For those, the same rules apply at that first run: `cuda/13.3.0` loaded and `TORCH_CUDA_ARCH_LIST` set, inside a GPU job.

### Step 7: check the result

First, check that the compiled library contains code for all three Nexus GPU types. Replace `<module>` with the name you import the package by:

```bash
PKG=$(python -c "import <module>, os; print(os.path.dirname(<module>.__file__))")
for so in $(find "$PKG" -name '*.so'); do echo "$so"; cuobjdump --list-elf "$so" | grep -o 'sm_[0-9]*' | sort -u; done
```

**Expected output:** each compiled library's path, followed by `sm_100`, `sm_120` and `sm_89`. A library that prints no `sm_` lines contains no GPU code, which is normal for helper libraries.

Then run a small piece of your package's own code on the GPU, such as an example from its documentation. It should run without compiling anything.

## 5. Using the environment later

You only install once. In later sessions or batch jobs, load the modules and activate the environment by its path. We tested these commands interactively; a batch script uses the same commands. Example batch script:

```bash
#!/bin/bash
#SBATCH -A <your-account>
#SBATCH -p gpu-rtxpro
#SBATCH --gpus=1
#SBATCH -c 8
#SBATCH -t 02:00:00

module load miniforge3/25.3.0-3 cuda/13.3.0
conda activate /storage/scratch/$USER/envs/myenv
python your_script.py
```

A batch script runs on the job's first node, so a single Python process like this one runs directly. An MPI program, or work spread over several nodes, needs `srun` to start its processes across the job.

## 6. Troubleshooting

- **An error saying the detected CUDA version does not match the version used to compile PyTorch:** rule 1 is broken. Check `python -c "import torch; print(torch.version.cuda)"` and `nvcc --version`. If PyTorch is not a 13.x build, reinstall it from the `cu130` index (step 4).
- **"no kernel image is available for execution on the device":** the package was compiled without your GPU's generation (rule 2). Set `TORCH_CUDA_ARCH_LIST` as in step 5 and reinstall with `pip install --no-cache-dir --force-reinstall --no-build-isolation ...`. `--no-cache-dir` matters here: without it, pip reuses the package it compiled earlier, with the old GPU list.
- **The build fails because torch is not found, or reports a missing build tool:** rule 3. Install the build tools listed in the package's documentation into your environment, and add `--no-build-isolation`.
- **The build is killed, or the job runs out of memory while compiling:** lower `MAX_JOBS` (for example to 8), or request more memory with `--mem`.
- **`hostname` shows a login node after `salloc`:** run `srun --pty bash` to get a shell on the job's compute node, then continue.
- **`conda activate` does not work:** load the module first with `module load miniforge3/25.3.0-3`.
- **"Disk quota exceeded":** the caches went to your home folder. Set the variables from step 2 before installing.

## 7. Example: beast with gsplat

[beast](https://github.com/paninski-lab/beast) needs Python 3.10, a specific fork of `gsplat` compiled from source, and the `ffmpeg` program. We ran this example on an RTX PRO node in November 2026. Follow steps 1, 2, 4 and 5 above as written; the beast-specific parts are below.

**Step 3, with its own environment name:**

```bash
module load miniforge3/25.3.0-3
conda create -y -p $WORK/envs/beast python=3.10
conda activate $WORK/envs/beast
```

**Step 6, beast's build tools, then beast from its repository** (this also downloads and compiles gsplat):

```bash
pip install lightning poetry-core
cd $WORK && git clone https://github.com/paninski-lab/beast && cd beast
pip install -e . --no-build-isolation
```

**Expected output:** `Building wheel for gsplat (pyproject.toml): still running...` a few times, then `Successfully built beast-backbones gsplat` and a `Successfully installed ...` line that includes `gsplat-1.4.0` and `beast-backbones-2.0.3`. This took 7 minutes on 16 cores.

**Step 7, the checks:**

```bash
SO=$(find $CONDA_PREFIX/lib/python3.10/site-packages/gsplat -name '*.so' | head -1); echo "$SO"
cuobjdump --list-elf "$SO" | grep -o 'sm_[0-9]*' | sort -u
module load ffmpeg/7.1.2-gcccore-14.3.0
python -c "import beast, gsplat, cv2, torch; print('beast ok | gsplat', gsplat.__version__, '| opencv', cv2.__version__, '| cuda', torch.cuda.is_available())"
```

**Expected output:** the path of `gsplat/csrc.so`, then `sm_100`, `sm_120` and `sm_89`, then `beast ok | gsplat 1.4.0 | opencv 5.0.0 | cuda True`.

In later jobs, also load `ffmpeg/7.1.2-gcccore-14.3.0`, because beast calls the `ffmpeg` program.
