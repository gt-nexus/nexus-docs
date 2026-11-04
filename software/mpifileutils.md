# mpiFileUtils

[mpiFileUtils](https://mpifileutils.readthedocs.io/en/v0.11/index.html) is a suite of
MPI-parallel replacements for common file-management commands such as `cp`, `rm`,
`find`, `du`, `diff`, `rsync`, and `tar`. Instead of a single process walking a
directory tree, mpiFileUtils spreads the work across many MPI ranks and nodes, so
operations on large datasets (millions of files or many terabytes) finish far faster
than their serial counterparts.

On Nexus, run mpiFileUtils as Slurm jobs on the **CPU partition**. Please do not run
large file operations on the login nodes, and do not use GPU partitions for them.

## Loading the module

```bash
module load mpifileutils/0.12-gompi-2025b
```

This also loads the GCC compiler and OpenMPI toolchain (`gompi/2025b`) that the tools
were built with. To confirm the tools are available:

```bash
module list
which dcp dwalk dsync
```

## Available tools

| Tool      | Replaces            | Description                                                       |
| --------- | ------------------- | ----------------------------------------------------------------- |
| `dcp`     | `cp -r`             | Copy files and directories in parallel                            |
| `dsync`   | `rsync`             | Synchronize a destination with a source (copy only differences)   |
| `drm`     | `rm -rf`            | Remove files and directories in parallel                          |
| `dwalk`   | `ls -R`, `du`       | Walk a tree; list, sort, and summarize files and sizes            |
| `dfind`   | `find`              | Search a tree for files matching criteria                         |
| `dcmp`    | `diff -r`           | Compare the contents of two directory trees                       |
| `dtar`    | `tar`               | Create and extract tar archives in parallel                       |
| `dchmod`  | `chmod`, `chgrp`    | Change permissions and group ownership                            |
| `ddup`    | —                   | Find duplicate files                                              |
| `dbcast`  | —                   | Broadcast a file to node-local storage on every node in a job     |
| `dreln`   | —                   | Rewrite symbolic links that point into a moved directory          |

Each tool prints its options with `--help`, for example `dcp --help`. Full
documentation for every tool is in the
[mpiFileUtils user guide](https://mpifileutils.readthedocs.io/en/v0.11/tools.html).

## Running a batch job

mpiFileUtils tools must be launched with `srun` inside a Slurm allocation. The
example below copies a directory tree using 4 CPU nodes.

```bash
#!/bin/bash
#SBATCH --job-name=dcp-copy
#SBATCH --partition=cpu-int
#SBATCH --account=<your_account>
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=32
#SBATCH --time=02:00:00
#SBATCH --output=dcp-%j.out

module load mpifileutils/0.12-gompi-2025b

srun dcp --preserve --progress 60 /path/to/source /path/to/destination
```

Submit it with:

```bash
sbatch dcp-copy.sh
```

Replace `<your_account>` with your allocation's account name and update the paths.
Use the same pattern for any of the tools, swapping out the `srun` line.

```{tip}
File operations are usually limited by the filesystem rather than by CPU. Start with
1–4 nodes and roughly 16–64 tasks per node, then scale up only if throughput keeps
improving. Very high task counts can overload shared storage without making the job
faster.
```

## Running interactively

For short tasks or testing, request an interactive allocation on the CPU partition:

```bash
salloc --partition=cpu-int --account=<your_account> --nodes=1 --ntasks-per-node=32 --time=01:00:00
module load mpifileutils/0.12-gompi-2025b
srun dwalk --print --sort size /path/to/dir
```

Exit the allocation with `exit` when you are done.

## Common examples

The commands below are run inside a job (batch or interactive) after loading the
module.

### Copy a directory tree

```bash
srun dcp --preserve /path/to/source /path/to/destination
```

`--preserve` keeps permissions, ownership, timestamps, and extended attributes.
Add `--progress 60` to print a status line every 60 seconds.

### Synchronize two directories

```bash
srun dsync /path/to/source /path/to/destination
```

`dsync` copies only files that are missing or differ in the destination, which makes
it well suited to resuming an interrupted transfer or refreshing a copy. Add
`--delete` to remove files from the destination that no longer exist in the source.

```{warning}
`dsync --delete` permanently removes files in the destination. Double-check the
source and destination paths before using it.
```

### Summarize disk usage

```bash
srun dwalk --sort size --print /path/to/dir | head -50
```

To print just the totals and a size histogram, use:

```bash
srun dwalk --distribution size:0,1K,1M,1G,1T /path/to/dir
```

### Save a file list and reuse it

Walking a large tree is often the most expensive step. Save the result once with
`--output` and feed it to other tools with `--input`:

```bash
srun dwalk --output dir.mfu /path/to/dir
srun dfind --input dir.mfu --name '*.log' --print
srun drm --input dir.mfu
```

### Find files

```bash
srun dfind --name '*.tmp' --mtime +30 /path/to/dir --print
```

### Remove a directory tree

```bash
srun drm /path/to/dir_to_delete
```

To remove only files matching a pattern, use `--match`, and preview first with
`--dryrun`:

```bash
srun drm --match '\.tmp$' --dryrun /path/to/dir
srun drm --match '\.tmp$' /path/to/dir
```

```{warning}
`drm` deletes data immediately and in parallel; there is no recycle bin. Run with
`--dryrun` first when in doubt.
```

### Compare two directory trees

```bash
srun dcmp /path/to/source /path/to/destination
```

Use this after a large copy to verify that the destination matches the source.

### Create and extract tar archives

```bash
# Create an archive
srun dtar --create --file archive.tar /path/to/dir

# Extract an archive into the current directory
srun dtar --extract --file archive.tar
```

### Change permissions and group

```bash
srun dchmod --group <groupname> --mode g+rX /path/to/dir
```

### Find duplicate files

```bash
srun ddup /path/to/dir
```

## Tips

- **Use the CPU partition.** File operations do not benefit from GPUs; running them on
  the CPU partition keeps GPU nodes free for compute work.
- **Avoid the login nodes.** Always launch the tools with `srun` inside a job.
- **Be careful with destination paths.** As with `cp`, `dcp src dest` copies `src`
  *into* `dest` if `dest` already exists as a directory.
- **Check the job output.** mpiFileUtils reports errors (for example, permission
  problems on individual files) in the job output file; review it after large runs.
- **Resume with `dsync`.** If a `dcp` job runs out of time, rerun the transfer with
  `dsync` to copy only what is missing.

## More information

- [mpiFileUtils documentation (v0.11)](https://mpifileutils.readthedocs.io/en/v0.11/index.html)
- [mpiFileUtils on GitHub](https://github.com/hpc/mpifileutils)
- {doc}`../support/help`
