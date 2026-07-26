# PEARC26 Tutorial — Fold a protein on Nexus, from VS Code

You will fold two proteins on a Nexus GPU — one from the CLI, one from the VizFold dashboard — in a
compute-node session started from **CS Bridge**, inside VS Code on your laptop.

**Nexus** is the project these tools are built for, and it spans three machines: **Delta**,
**DeltaAI**, and **Nexus** itself. This walkthrough uses Nexus; the other two work the same way and
are listed alongside it wherever a value differs.

**The Nexus cluster you will use today is a demo deployment, not the production one.** It is a
smaller machine — a 10 GB A100 vGPU rather than the B200s — provisioned so that a full workshop
can install and fold concurrently. Same scheduler, same commands, same dashboard. VizFold knows it
as the `nexus-dev` site.

**Complete the prerequisites before the session.** They account for most of the elapsed time —
the OpenFold build alone is ~10 minutes plus a queue wait — and they are unreliable over conference
wifi. With them in place, the session runs about 30 minutes: start a session, fold, review the
results.

---

## Before you arrive

### On your laptop

| | Requirement | How to check |
| --- | --- | --- |
| 1 | A **Nexus account** for the demo cluster, or your own **Delta** or **DeltaAI** allocation — on those you take the queue as it comes | `ssh` to that machine's login node succeeds |
| 2 | **VS Code 1.98 or newer** | Help → About |
| 3 | The **Remote - SSH** extension | Search `ms-vscode-remote.remote-ssh` in Extensions |
| 4 | **CS Bridge** — search `CS Bridge`, publisher `cybershuttle`, or open [the listing](https://marketplace.visualstudio.com/items?itemName=cybershuttle.csbridge) | Its icon appears in the activity bar |
| 5 | A **Microsoft account** (any free one) | CS Bridge uses it only to authenticate the Dev Tunnel |

Click the CS Bridge icon once and sign in with the Microsoft account. It authenticates the encrypted
Dev Tunnel that carries your session; it is not linked to your cluster identity and gives Microsoft
no access to the cluster.

### On the cluster, from a login node

Everything below happens in one ssh session to the **login node** of the machine you will use — the
install submits its own build job.

```bash
ssh <you>@login.nexus.cybershuttle.org
sacctmgr -nP show assoc user=$USER format=account
```

Note your account name — you will type it into the session form on the day. For this workshop Nexus
uses `pearc26-tutorial`, your default there. Delta and DeltaAI charge GPU work to a separate account
from CPU work, so pick the GPU one:

| Machine | Login node | GPU account |
| --- | --- | --- |
| Nexus | `login.nexus.cybershuttle.org` | `pearc26-tutorial` |
| Delta | `login.delta.ncsa.illinois.edu` | `<your-alloc>-delta-gpu` |
| DeltaAI | `dtai-login.delta.ncsa.illinois.edu` | `<your-alloc>-dtai-gh` |

Still on the login node, bootstrap the CLI. It puts the prebuilt `vizfold` binary for that machine's
architecture into `~/.local/bin`:

```bash
curl -sL https://raw.githubusercontent.com/AI2Science/vizfold-foundation/main/install.sh | bash
vizfold --help
```

If `~/.local/bin` was not already on `PATH`, the installer appends the `export` to your shell rc and
prints the line to run now. If it was, and the shell still cannot find `vizfold`, run `hash -r`.

Now install the OpenFold backend. It submits an interactive build job and streams the output, so run
it inside `tmux` or `screen` — that way the build survives a dropped connection:

```bash
tmux new -s vizfold
vizfold install openfold
```

It asks you to confirm the site, install prefix, account and build partition, each already filled in
from that machine's profile; accept each with enter. It then submits the build and streams the
output: about ten minutes once it starts, plus the queue wait (8 minutes of build measured on Delta,
Nexus unmeasured). Detach with `Ctrl-b d`, reattach with `tmux attach -t vizfold`.

The install clones the source to `~/vizfold-src`, works out which machine it is on from the SLURM
`ClusterName`, builds a micromamba environment with OpenFold's CUDA extension, and links that
machine's AlphaFold2 mirror, so nothing large is downloaded.

| | Build partition | Install prefix | AlphaFold2 mirror |
| --- | --- | --- | --- |
| Nexus | `gpu` | `/projects/<you>/vizfold` | `/media/volume/data/alphafold2/database` |
| Delta | `cpu` | `/work/nvme/<alloc>/<you>/vizfold` | `/work/hdd/data/alphafold2/database` |
| DeltaAI | `ghx4` | `/work/nvme/<alloc>/<you>/vizfold-gh` | `/work/hdd/data/alphafold2/database` |

Paths from here on are Nexus's. `vizfold status` prints yours.

DeltaAI's prefix is suffixed `-gh` on purpose: `/work/nvme` is shared with x86 Delta, and the
aarch64 environment must not clobber it. On Nexus the install also pins a matching NVRTC library —
its driver is older than the CUDA the environment ships, and without the pin relaxation fails. That
is automatic; it goes by as `driver CUDA … preloading libnvrtc…`.

Confirm the result before you finish:

```bash
vizfold status
```

```text
VizFold status

COMPONENT  STATUS  DETAIL
---------  ------  ------
binary     ok      0.6.0 (latest)
repo       ok      /home/<you>/vizfold-src at v0.6.0
config     ok      19 keys
openfold   ok      /projects/<you>/vizfold/envs/vizfold-openfold
esmfold    absent  not installed (/projects/<you>/vizfold/envs/vizfold-esmfold)
scheduler  ok      gpu, gpu, <your-account>, <your-account>

Everything checks out.

Config: /home/<you>/.config/vizfold/vizfold.json
  ESMFOLD_ENV_PREFIX = /projects/<you>/vizfold/envs/vizfold-esmfold
  OPENFOLD_ACCOUNT = <your-account>
  OPENFOLD_AF2_ROOT = /media/volume/data/alphafold2/database
  ...
  database = /projects/<you>/vizfold/vizfold.db (present)
```

`Everything checks out.` is what you need. Each row is a part that can break on its own, and
anything wrong names itself here with a `Problems:` list and the command that fixes it (`absent` =
not installed; `unverified` = the check could not be run from here, which is not a failure).

The prefix — environments, backend state, databases, every run — sits under your project space
rather than your quota-capped home; only the source checkout, `~/vizfold-src`, is on home. Both are
on filesystems the compute nodes share, so what you installed from the login node is what your GPU
session will find on the day.

---

## 1. Add your machine as a host

That completes the login-node work; the remainder is in VS Code. CS Bridge reads `~/.ssh/config` —
if the machine is already listed, it appears in the **SSH Hosts** view and you can skip ahead.

Otherwise, in **SSH Hosts** click **+**, and paste the command you would normally use:

```
ssh <you>@login.nexus.cybershuttle.org
```

— substituting your machine's login node from the table above.

CS Bridge parses that into a `Host` block and writes it to `~/.ssh/config`. Duo push and passphrase
prompts appear as VS Code input boxes on the first connection — approve on your phone as usual.

---

## 2. Start a GPU session

With the host in place, ask it for a GPU. In the **Sessions** view click **+**, pick your host, and
switch to the **GPU** tab:

| Field | Nexus | Delta | DeltaAI |
| --- | --- | --- | --- |
| Partition | `gpu` | `gpuA100x4-interactive` | `ghx4-interactive` |
| Account | `pearc26-tutorial` | `<your-alloc>-delta-gpu` | `<your-alloc>-dtai-gh` |
| GPUs | 1 | 1 | 1 |
| CPUs | 8 | 8 | 8 |
| Memory | 32 GB | 32 GB | 32 GB |
| Walltime | `01:00:00` | `01:00:00` | `01:00:00` |

- The `-interactive` partitions on Delta and DeltaAI skip the queue but **cap at one hour**. For
  longer, use `gpuA100x4` on Delta or `ghx4` on DeltaAI — up to 48 hours, with a queue wait.
- Ask for **32 GB** on all three, and no less: the VS Code server and the OpenFold build need it
  together, and a smaller job runs out of memory and takes the terminal down with it.

Click **Start**. CS Bridge writes the batch script, submits it with `sbatch`, and shows the job go
`submitting → queued → preparing → ready to connect`. Behind those states it starts the `linkspan`
agent on your compute node and exposes it over the Dev Tunnel; no inbound ports are opened on the
cluster.

---

## 3. Connect

Once the session reads **ready to connect**, click **Connect**. A new VS Code window opens, attached
to the compute node. Confirm the node, and that the install you did at home came with you:

```bash
hostname                # a compute node, not a login node
nvidia-smi              # your GPU: A100 vGPU (Nexus), A100 (Delta), GH200 (DeltaAI)
vizfold status          # openfold ok, "Everything checks out."
```

The config (`~/.config/vizfold/vizfold.json`) and the install prefix are both on shared filesystems,
so nothing needs reinstalling here. If `vizfold` is not found, run `hash -r`; if `openfold` reads
`absent`, see Troubleshooting.

The remaining steps run in that window's integrated terminal, on the allocated GPU.

---

## 4. Fold your first protein from the CLI

VizFold ships example proteins with precomputed alignments, so they fold without an MSA search. See
what you have:

```bash
vizfold list examples
```

```text
ID      RESIDUES  DESCRIPTION
------  --------  -------------------------------------
1G1J_1  43        NON-STRUCTURAL GLYCOPROTEIN NSP4
1UBQ_1  76        UBIQUITIN
1STM_1  157       SATELLITE PANICUM MOSAIC VIRUS
6KWC_1  191
2OMF_1  340       MATRIX PORIN OUTER MEMBRANE PROTEIN F
```

Fold ubiquitin — 76 residues, and the example the Nexus profile picks by default:

```bash
vizfold run 1UBQ_1
```

```text
Queued OpenFold run 1 (1UBQ_1, 76 residues)

Executing run 1
... OpenFold's own output streams here ...

Preflight: passed
...

Command exit_code: 0

Final status: completed

Run 1 completed in <n>s. View it with: vizfold serve
```

Attention maps are dumped by default; pass `--attn=false` to skip them.

The larger examples need more GPU memory. Nexus's 10 GB A100 vGPU suits the shorter sequences —
`1UBQ_1` (76 residues) and `1G1J_1` (43) — while `6KWC_1` (191) and `2OMF_1` (340) are better run on
Delta or DeltaAI, where a 191-residue fold takes about **78 seconds** on a full A100.

<details>
<summary>What that one command did</summary>

`vizfold run <target>` takes a bundled example id, a path to a FASTA, or the id of a run you queued
earlier — queueing first in the first two cases, registering the outputs when the fold lands.

Queue it yourself for control over the inputs. `--fasta` takes the file itself or a directory
holding exactly one; the run's id and sequence are read out of it, and preflight rejects a run
recorded under any other name. `vizfold queue openfold --help` lists every override.

```bash
vizfold queue openfold \
  --fasta ./my-protein.fasta \
  --alignment-dir ./my-alignments
vizfold run 2                      # then execute it by id
```

The backend also installs its own CLI into its environment, which invokes the model directly:
no paths are filled in and no run is recorded.

```bash
/projects/<you>/vizfold/bin/micromamba \
  run -p /projects/<you>/vizfold/envs/vizfold-openfold openfold --help
```
</details>

Inspect the result:

```bash
vizfold show run 1
grep -c '^ATOM' /projects/<you>/vizfold/runs/1/predictions/1UBQ_1_model_1_ptm_relaxed.pdb
```

A relaxed ubiquitin prediction is **1231 atoms**; a relaxed 6KWC is 2839. `vizfold show run 1`
prints the run directory in its `artifacts:` table (`run_output_directory`) — the shell does not
have it as a variable.

---

## 5. Open the dashboard in VS Code

So far the structure is a path on disk. The run's last line pointed at `vizfold serve` — start it in
the same terminal.

```bash
vizfold serve
```

If the node has no Node ≥22.13 on `PATH`, the first run provisions one into your install prefix
before installing the dashboard's dependencies — a couple of minutes, once.

```text
Provisioning Node (first run only)...
Installing workbench dependencies (npm install)...
Starting workbench at http://localhost:3000
```

VS Code forwards that port automatically — check the **Ports** panel next to the terminal, where
`3000` should be listed. To view it **inside** VS Code:

> `Cmd/Ctrl+Shift+P` → **Simple Browser: Show** → `http://localhost:3000`

Drag that tab to the side so the browser and terminal are visible together.

The dashboard lists **run 1**. Click it: the predicted structure renders in a 3D viewer (drag to
rotate, scroll to zoom) alongside the attention maps for each layer and head.

---

## 6. Fold a second protein from the dashboard

The dashboard also submits folds. At the top of the run list is a **Fold a protein** card:

| Field | Value |
| --- | --- |
| Protein | `1G1J_1 — NON-STRUCTURAL GLYCOPROTEIN NSP4 (43 residues)` |
| Dump attention maps | checked |

Click **Fold**. You land on the new run's page while it is still `submitted`; the status moves
through `running` to `completed` — this is the smallest example — and the viewer appears when it
does.

Same executor, same work as step 4: the dashboard queues the run and shells out to
`vizfold run <id>`.

---

## 7. Compare the two

Two structures now, one submitted from the terminal and one from the browser. Open run 1 and run 2
in two dashboard tabs. Worth looking at:

- **1UBQ** is the classic β-grasp fold: a five-strand sheet wrapped around one α-helix. **1G1J** is
  a 43-residue viral peptide with almost no tertiary structure. Two very different things out of the
  same weights.
- The per-residue confidence coloring shows where the model is sure: termini and loops are the least
  confident regions in both, and the short peptide is far less confident overall.
- In the attention maps, compare an early layer against layer 47. Early layers attend locally along
  the sequence; late layers attend between residues far apart in sequence but adjacent in 3D. That
  is the geometric reasoning becoming visible.

If you are on Delta or DeltaAI, fold a third: `6KWC_1` is a 191-residue β-jelly-roll xylanase, a
dense sandwich of β-sheets, and `2OMF_1` a 340-residue membrane porin — a β-barrel, about three
minutes on a full A100.

---

## 8. Clean up

The GPU session is the only transient component. End the job with **Stop** in the CS Bridge
Sessions view, or let the walltime expire.

Both structures, their attention maps, and the install behind them stay on the cluster filesystem.
**Restart** on the stopped session brings back the same partition, account and resources, with run 1
and run 2 in the dashboard where you left them.

```bash
vizfold uninstall            # everything: both backends, the config, the run database — after a prompt
vizfold uninstall openfold   # only that backend; config, runs, and the checkout stay
rm ~/.local/bin/vizfold
```

The loop is the same for a sequence of your own: point `vizfold run` at your FASTA and read the
result in this dashboard — here on the demo Nexus, or on production Nexus, Delta and DeltaAI, where
a full card takes the longer sequences too.

---

## Troubleshooting

**Anything wrong with the install itself — start with `vizfold status`.** It reports each part
(binary, repo, config, each backend, scheduler) and lists what is broken with the command that fixes
it. Most of the entries below are what those problems look like.

**No hosts listed in CS Bridge.** `~/.ssh/config` is empty or unreadable. Add the host with the
**+** button in SSH Hosts, then hit refresh.

**Microsoft sign-in fails.** Your network is blocking `login.microsoftonline.com` or
`*.devtunnels.ms`. Both must be reachable; the Dev Tunnel is the only supported transport today.

**Job stuck in `PENDING`.** The interactive partition is full or you asked for too much. Try fewer
CPUs or less memory, or run `squeue -u $USER --start` on the login node for an estimate.

**"Slurm is not available".** You picked a host with no `sinfo` on `PATH` — probably not a login
node.

**The Connect window disconnects.** The session shows **Unreachable**; click **Reconnect** to
rebuild the relay. `View → Output → CS Bridge` shows the failing step.

**`run vizfold install openfold first`.** The config is not initialized, or the freshly written
`~/.config/vizfold/vizfold.json` has not propagated across NFS yet. Check `vizfold status`, wait a
few seconds, retry.

**`No examples under <dir>. Re-run vizfold install openfold.`** The examples come from
`$OPENFOLD_HOME/examples/monomer/`, so the checkout is missing or `OPENFOLD_HOME` points elsewhere.
`vizfold status` says so as `repo BROKEN`; `vizfold update` clones it or brings it back to this
binary's release.

**`vizfold status` says the config was written by a different vizfold.** The config on disk came
from an older release and holds names this binary no longer reads. `vizfold install openfold`
rewrites it.

**The install says `site [local]`, then `no install prefix`.** It could not work out which cluster
you are on — Delta's login nodes cannot always reach the Slurm controller, so `scontrol show config`
returns nothing. Name the site yourself:

```bash
OPENFOLD_SITE=nexus-dev vizfold install openfold   # or delta / delta-gh
```

If `sinfo` and `squeue` also hang, the controller is genuinely down and the build job cannot be
submitted either.

**`Invalid account or account/partition combination`.** The GPU account and partition must match —
see the table in step 2. Confirm yours with `sacctmgr -nP show assoc user=$USER format=account`.
`vizfold status` checks both names against the scheduler and says which one it does not recognise.

**Port 3000 does not open.** Check the **Ports** panel — if `3000` is absent, VS Code missed the
auto-forward. Add it manually with **Forward a Port**.

**A dashboard fold sticks on `submitted`.** The run's own page shows its error message once SLURM
reports back. The deeper trace is `/projects/<you>/vizfold/runs/<id>.submit.log`.

**The install stopped when my ssh dropped.** `vizfold install openfold` streams an interactive job,
so the job ends with the connection — `tmux` or `screen` avoids that. Re-running it resumes from the
last completed step either way.

**`vizfold status` says `openfold absent` inside the session, but it was `ok` from the login node.**
The session is on a different machine than you installed from — check `hostname` against the login
node you used. Delta and DeltaAI share `/work/nvme` but not their environments, and an install done
on one does not serve the other.

---

## Where to get help

- CS Bridge issues: <https://github.com/cyber-shuttle/CS-Bridge/issues>
- VizFold: <https://github.com/AI2Science/vizfold-foundation>
- Both are built by the [ARTISAN research group](https://gt-artisan.github.io/) at Georgia Tech.
