# Fold a Protein on Delta from VS Code

**PEARC26 Hands-On Workshop**

Run a full protein-structure prediction on an NCSA GPU without writing a batch script or opening a terminal on a login node. Everything happens inside VS Code on your laptop.

| Duration | Platform | Tools | Backend / Hardware |
|---|---|---|---|
| ~60 minutes | NCSA Delta / DeltaAI | CS Bridge + VizFold | OpenFold on A100 / GH200 |

## What You Will Have Built

1. A VS Code window running **on a Delta GPU compute node**, opened by the CS Bridge extension.
2. **VizFold** and the **OpenFold** backend installed into your project space on that node.
3. One folded structure - **6KWC**, a 190-residue xylanase - submitted from the command line.
4. A second folded structure - **1UBQ**, ubiquitin - submitted from the **VizFold dashboard**, running in VS Code's built-in browser.
5. Both structures in an interactive 3D viewer, with OpenFold's attention maps.

The GPU install is the long pole at roughly eight minutes. The folds themselves take one to two minutes each.

---

## STEP 00: Do This at Home

### Before You Arrive

None of these work well over conference WiFi under time pressure.

| # | Requirement | How to check |
|---:|---|---|
| 1 | An **ACCESS/NCSA account** with a GPU allocation on Delta or DeltaAI, with Duo 2FA enrolled | `ssh <you>@login.delta.ncsa.illinois.edu` succeeds |
| 2 | **VS Code 1.98** or newer | Help -> About |
| 3 | The **Remote - SSH** extension | `ms-vscode-remote.remote-ssh` |
| 4 | A **Microsoft account** | Any free one, used only for the Dev Tunnel |
| 5 | Network access to `login.microsoftonline.com` and `*.devtunnels.ms` | Ask IT to allowlist both |

Then find your SLURM account name - you will type it into the session form.

```bash
ssh <you>@login.delta.ncsa.illinois.edu
sacctmgr -nP show assoc user=$USER format=account
```

You will see entries like `bbol-delta-gpu` on Delta or `bbol-dtai-gh` on DeltaAI. Note the **GPU** one.

---

## STEP 01: Install CS Bridge

Install **CS Bridge** from the VS Code Marketplace. Search for **CS Bridge**, publisher **cybershuttle**, or open the listing directly.

Click the CS Bridge icon in the activity bar on the left edge.

On first use it asks you to sign in with a Microsoft account. That account authenticates the encrypted Dev Tunnel that carries your session. It is not linked to your NCSA identity and gives Microsoft no access to your cluster.

---

## STEP 02: Add Delta as a Host

CS Bridge reads `~/.ssh/config`. If Delta is already there, it appears in the **SSH Hosts** view and you can skip ahead.

Otherwise click **+** and paste the command you would normally use:

```bash
ssh <you>@login.delta.ncsa.illinois.edu
```

For DeltaAI, use:

```bash
ssh <you>@dtai-login.delta.ncsa.illinois.edu
```

CS Bridge parses that into a `Host` block and writes it to `~/.ssh/config`.

Duo push and passphrase prompts appear as VS Code input boxes on the first connection. Approve on your phone as usual.

---

## STEP 03: Start a GPU Session

In the **Sessions** view, click **+**, pick your Delta host, and switch to the **GPU** tab.

| Field | Delta | DeltaAI |
|---|---|---|
| Partition | `gpuA100x4-interactive` | `ghx4-interactive` |
| Account | `<alloc>-delta-gpu` | `<alloc>-dtai-gh` |
| GPUs | `1` | `1` |
| CPUs | `8` | `8` |
| Memory | `64 GB` | `64 GB` |
| Walltime | `01:00:00` | `01:00:00` |

```{important}
**Watch the two caps.**

The `-interactive` partitions start in seconds instead of queueing, but they **cap at one hour**. For longer jobs, use `gpuA100x4` or `ghx4` - up to 48 h - and expect a queue wait.

Ask for **at least 32 GB**. The VS Code server plus the OpenFold build will OOM in a small cgroup; a 2 GB job kills the terminal host outright.
```

Click **Start**.

CS Bridge writes the batch script, submits it with `sbatch`, and shows the job move through:

```text
submitting -> queued -> preparing -> ready to connect
```

Under the hood, it is starting the linkspan agent on your compute node and exposing it over the Dev Tunnel. No inbound ports are opened on the cluster.

---

## STEP 04: Connect

Click **Connect**. A new VS Code window opens, attached to the compute node.

Confirm it:

```bash
hostname            # a compute node, e.g. gpub042 - not a login node
nvidia-smi          # your A100 (Delta) or GH200 (DeltaAI)
echo $SLURM_JOB_ID  # your job
```

Everything from here runs in that window's integrated terminal. The GPU is already yours - nothing below needs to queue again.

---

## STEP 05: Install VizFold and OpenFold

Bootstrap the CLI. It downloads the prebuilt `vizfold` binary for the node's architecture into `~/.local/bin`.

```bash
curl -sL https://raw.githubusercontent.com/AI2Science/vizfold-foundation/main/install.sh | bash
vizfold --help
```

If the shell cannot find `vizfold`, run:

```bash
hash -r
```

or open a new terminal.

Now install the OpenFold backend:

```bash
vizfold install openfold
```

This streams every step. It clones the source to `~/vizfold-src`, detects that it is on Delta from the SLURM `ClusterName`, builds a micromamba environment with OpenFold's CUDA extension, and links the AlphaFold2 databases from NCSA's shared mirror at `/work/hdd/data/alphafold2/database` - so nothing large is downloaded.

Because you are already inside a GPU allocation, the build runs right here on your node rather than submitting a second job.

Check what it settled on with `vizfold status`:

```bash
vizfold status
```

Example output:

```text
VizFold status
Config: /u/<you>/.config/vizfold/vizfold.json

OPENFOLD_HOME = /u/<you>/vizfold-src
OPENFOLD_PREFIX = /work/nvme/<alloc>/<you>/vizfold
OPENFOLD_DATA_DIR = /work/nvme/<alloc>/<you>/vizfold/data
OPENFOLD_SITE = delta
OPENFOLD_GPU_PARTITION = gpuA100x4-interactive

Backends:
BACKEND   STATUS         ENV PREFIX
--------  -------------  --------------------------------------------
openfold  installed      .../vizfold/mamba/envs/openfold-env
esmfold   not installed  .../vizfold/esmfold-venv
```

Everything lives under your `/work/nvme` allocation, not your quota-capped home.

---

## STEP 06: Fold Your First Protein from the CLI

```{note}
Expected time: ~2 minutes.
```

VizFold ships a handful of example proteins with precomputed alignments, so you can fold them in seconds instead of spending hours on an MSA search.

See what you have:

```bash
vizfold list examples
```

Example output:

```text
ID       RESIDUES  DESCRIPTION
-------  --------  -------------------------------------
1G1J_1         43  NON-STRUCTURAL GLYCOPROTEIN NSP4
1UBQ_1         76  UBIQUITIN
1STM_1        154  SATELLITE PANICUM MOSAIC VIRUS
6KWC_1        190
2OMF_1        340  MATRIX PORIN OUTER MEMBRANE PROTEIN F
```

Fold `6KWC`, a bacterial xylanase:

```bash
vizfold fold 6KWC_1
```

Example output:

```text
Queued OpenFold run 1 (6KWC_1, 190 residues)
Executing run 1
Preflight: passed
...
Final status: completed
Registered artifacts for run 1
  run_output_directory       -> /work/nvme/<alloc>/<you>/vizfold/runs/1
  attention_output_directory -> /work/nvme/<alloc>/<you>/vizfold/runs/1/attention
Run 1 completed in 78s.
View it with: vizfold serve
```

The fold itself takes about **78 seconds** on one A100. Attention maps are dumped by default; pass `--attn=false` to skip them.

``{note} What `vizfold fold` does under the hood

`vizfold fold` runs the same OpenFold executor that the dashboard uses. It queues the selected example, performs the run in your existing GPU allocation, and registers the output artifacts so they are visible from the dashboard.

``

Inspect the result:

```bash
vizfold show run 1
grep -c '^ATOM' $OPENFOLD_PREFIX/runs/1/predictions/6KWC_1_model_1_ptm_relaxed.pdb
```

A relaxed `6KWC` prediction is **2839 atoms**. A few thousand atoms means it worked.

---

## STEP 07: Open the Dashboard in VS Code

```{note}
Expected time: ~3 minutes on the first run.
```

Start the dashboard:

```bash
vizfold serve
```

On first run this provisions Node into your install prefix and installs the dashboard's dependencies - a couple of minutes, once. After that it starts immediately.

Example output:

```text
Provisioning Node (first run only)...
Installing workbench dependencies (npm install)...
Starting workbench at http://localhost:3000
```

VS Code forwards that port automatically. Check the **Ports** panel next to the terminal, where `3000` should be listed.

To view it inside VS Code:

```text
Cmd/Ctrl + Shift + P -> Simple Browser: Show -> http://localhost:3000
```

Drag that tab to the side so the browser and terminal are visible together.

You should see the VizFold dashboard listing **run 1**. Click it: the predicted structure renders in an interactive 3D viewer - rotate with drag, zoom with scroll - alongside the attention maps for each layer and head.

---

## STEP 08: Fold a Second Protein from the Dashboard

```{note}
Expected time: ~1 minute.
```

Now do it without the terminal.

At the top of the run list is a **Fold a protein** card:

| Field | Value |
|---|---|
| Protein | `1UBQ_1` - UBIQUITIN, 76 residues |
| Dump attention maps | Checked |

Click **Fold**.

You land on the new run's page while it is still `submitted`; the status updates itself through `running` to `completed` in about a minute - ubiquitin is a quarter the size of `6KWC` - and the 3D viewer appears when it lands. No refreshing.

This is the same executor doing the same work as step 6. The dashboard is queueing, executing, and registering the run for you, exactly as `vizfold fold` did from the terminal.

---

## STEP 09: Compare the Two

Open run 1 and run 2 in two dashboard tabs.

| Structure | Run | Residues | Description |
|---|---:|---:|---|
| **6KWC** | 1 | 190 | A beta-jelly-roll xylanase - a dense sandwich of beta-sheets. |
| **1UBQ** | 2 | 76 | The classic beta-grasp fold: a five-strand sheet wrapped around one alpha-helix. |

Two very different topologies out of the same weights.

Things worth looking at:

- The **per-residue confidence colouring** shows where the model is sure. Termini and loops are the least confident regions in both.
- In the **attention maps**, compare an early layer against layer 47. Early layers attend locally, along the sequence; late layers attend across the structure, between residues far apart in sequence but adjacent in 3D. That is the geometric reasoning becoming visible.

Fold a third if you have time: `2OMF_1` is a 340-residue membrane porin, a beta-barrel, and takes about three minutes.

---

## STEP 10: Clean Up

Your work is on the cluster filesystem and survives the session.

To end the job, click **Stop** in the CS Bridge Sessions view - or just let the walltime expire.

To pick up later, click **Restart** on the stopped session: same partition, account, and resources, one click. Your VizFold install and every run you folded are still there.

### Remove VizFold Entirely

```bash
vizfold uninstall     # lists everything it will remove, then asks
rm ~/.local/bin/vizfold
```

---

## Reference: Troubleshooting

``{note} No hosts listed in CS Bridge
The PDF lists this troubleshooting item but does not include expanded text in the extracted content.
``

``{note} Microsoft sign-in fails
The PDF lists this troubleshooting item but does not include expanded text in the extracted content.
``

```{note} Job stuck in PENDING
The interactive partition is full or you asked for too much. Try fewer CPUs or less memory, or run the following on the login node for an estimate:

```bash
squeue -u $USER --start
```
```

```{note} "Slurm is not available"
The PDF lists this troubleshooting item but does not include expanded text in the extracted content.
```

```{note} The Connect window disconnects
The PDF lists this troubleshooting item but does not include expanded text in the extracted content.
```

```{note} "run vizfold install openfold first"
The PDF lists this troubleshooting item but does not include expanded text in the extracted content.
```

```{note} `vizfold list examples` is empty
The PDF lists this troubleshooting item but does not include expanded text in the extracted content.
```

```{note} "Invalid account or account/partition combination"
The PDF lists this troubleshooting item but does not include expanded text in the extracted content.
```

```{note} Port 3000 does not open
The PDF lists this troubleshooting item but does not include expanded text in the extracted content.
```

```{note} A dashboard fold sticks on "submitted"
The PDF lists this troubleshooting item but does not include expanded text in the extracted content.
```

```{note} The install died when my laptop slept
The PDF lists this troubleshooting item but does not include expanded text in the extracted content.
```

---

## Links

- [CS Bridge on the VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=cybershuttle.csbridge)
- [ARTISAN research group](https://gt-artisan.github.io/)
- [CS Bridge issues](https://github.com/cyber-shuttle/CS-Bridge/issues)
- [VizFold Foundation](https://github.com/AI2Science/vizfold-foundation)

---

Built by the ARTISAN research group at Georgia Tech.
