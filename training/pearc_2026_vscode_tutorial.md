# PEARC26 Tutorial — Fold a protein on Nexus, from VS Code

You follow along while the presenter runs one science task end to end on Nexus: predicting protein
structures with OpenFold, on a GPU you allocate yourself, from VS Code on your laptop. Protein
folding is the first of several such tasks; the machinery around it — **CS Bridge** for the session,
**VizFold** for the work — is the same for the ones that follow.

**Nexus** is the project these tools are built for, and it spans three machines: **Delta**,
**DeltaAI**, and **Nexus** itself. This walkthrough uses Nexus; the other two work the same way and
are listed alongside it wherever a value differs.

**The Nexus cluster you will use today is a demo deployment, not the production one.** It is a
smaller machine — a 10 GB A100 vGPU rather than the B200s — provisioned so that a full workshop
can install and fold concurrently. Same scheduler, same commands, same dashboard. VizFold knows it
as the `nexus-dev` site.

**Do the prerequisites before the workshop** — or start them in the background as the room opens.
They gate on a Nexus account being approved by a human, and they end with an OpenFold build of about
ten minutes, so they are not something to begin when the demo does.

They finish at `vizfold install openfold`. That is where the demo expects everyone to be; keep going
past it if you like, but the presenter starts from there.

---

## Prerequisites

### 1. An approved Nexus account

Sign up at **<https://portal.nexus.gatech.edu>**. The form asks for **Name**, **Email**,
**Institution**, **Cluster Username**, an **Event Code** — the workshop organizers share that
separately — and an optional **Reason**.

Submitting notifies the Nexus administrators, who approve or reject the request. On approval you
receive an email with what to do next; steps 4 to 6 need that account, so start here and let the
approval arrive while you install VS Code.

If you would rather use your own **Delta** or **DeltaAI** allocation, you can, taking the queue as
it comes.

### 2. VS Code 1.98 or newer

Check under Help → About.

### 3. The Remote - SSH and CS Bridge extensions

| Extension | Find it by |
| --- | --- |
| **Remote - SSH** | `ms-vscode-remote.remote-ssh` in Extensions |
| **CS Bridge** | search `CS Bridge`, publisher `cybershuttle`, or open [the listing](https://marketplace.visualstudio.com/items?itemName=cybershuttle.csbridge) |

CS Bridge appears in the activity bar once installed. Click its icon and sign in with a Microsoft
account — any free one will do. It authenticates the encrypted Dev Tunnel that carries your session;
it is not linked to your cluster identity and gives Microsoft no access to the cluster.

That is everything to bring. The rest is the session.

---

### 4. Add your cluster as an SSH host

CS Bridge reads `~/.ssh/config`. If your machine is already listed, it appears in the **SSH Hosts**
view and you can skip ahead. Otherwise click **+** in that view and paste the command you would
normally use:

```
ssh <you>@login.nexus.cybershuttle.org
```

| Machine | Login node | GPU account |
| --- | --- | --- |
| Nexus | `login.nexus.cybershuttle.org` | `pearc26-tutorial` |
| Delta | `login.delta.ncsa.illinois.edu` | `<your-alloc>-delta-gpu` |
| DeltaAI | `dtai-login.delta.ncsa.illinois.edu` | `<your-alloc>-dtai-gh` |

CS Bridge parses that into a `Host` block and writes it to `~/.ssh/config`. Duo push and passphrase
prompts appear as VS Code input boxes on the first connection — approve on your phone as usual.

Nexus charges this workshop to `pearc26-tutorial`, your default account there, so the session form
arrives with it filled in. Delta and DeltaAI charge GPU work to a separate account from CPU work, so
pick the GPU one; `sacctmgr -nP show assoc user=$USER format=account` on the login node lists yours.

---

### 5. Open a terminal on it

Expand the host's entry in **SSH Hosts** and click **Terminal**. That opens a shell on the
login node, and holds a control connection open behind it — every command after this one reuses it,
so Duo asks once rather than once per connection.

Leave that terminal open. The rest of the prerequisites run in it.

### 6. Install vizfold and the OpenFold backend

```bash
curl -fsSL https://raw.githubusercontent.com/AI2Science/vizfold-foundation/main/install.sh | bash
```

That puts two binaries in `~/.local/bin`: the prebuilt `vizfold` for this machine's architecture,
and `micromamba`, which creates and runs every environment underneath it. It also wires tab
completion into your bash and zsh rc, so `vizfold ins<Tab>` and `vizfold install <Tab>` complete
from the next shell on.

If `~/.local/bin` was not already on `PATH`, the installer appends the `export` to your shell rc and
prints the line to run now. If it was, and the shell still cannot find `vizfold`, run `hash -r`.

Run it bare to see what it does:

```bash
vizfold
```

```text
VizFold executor administration CLI

Usage: vizfold <COMMAND>

Commands:
  install             Install the checkout everything runs from (`repo`), or a model backend from it
  download            Download a backend's data (OpenFold AlphaFold2 databases/params)
  status              Show resolved config, which backends are installed, and whether it all checks out
  uninstall           Remove one part, or everything the install generated
  update              Move the checkout to this binary's release (`repo`), or reinstall a backend from it
  self-update         Replace this binary with the latest release. Run `update repo` after, for the checkout
  serve               Start the workbench dashboard, over the given backends (default: all installed)
  list                List executor records
  show                Show one executor record
  run                 Fold targets in one execution: bundled examples, FASTAs, directories of FASTAs -- or a queued run by id
  register-artifacts  Register known artifacts for a completed run
  completions         Print this shell's tab-completion script. `install.sh` wires it into your shell rc
  help                Print this message or the help of the given subcommand(s)

Options:
  -h, --help     Print help
  -V, --version  Print version
```

The binary ships only itself. `install repo` fetches the checkout every installer and every
example lives in:

```bash
vizfold install repo
```

It clones to `~/vizfold-repo`, then settles which cluster this is, where the install prefix goes,
which AlphaFold2 mirror holds the protein databases and what the scheduler takes, and writes all of
it to `~/.config/vizfold/vizfold.json`. It also stages the dashboard and installs its dependencies,
so `vizfold serve` later starts rather than installs. Nothing else clones on your behalf — a
backend install stops and names it:

```text
repo: no checkout at /home/<you>/vizfold-repo
  -> vizfold install repo
```

With the checkout in place, install the OpenFold backend:

```bash
vizfold install openfold
```

It asks you to confirm the site, the install prefix, the account and the build partition, each
already filled in from this machine's profile; accept each with enter. From a login node it submits
its own build job and streams the output, so run it inside `tmux` or `screen` — the build then
survives a dropped laptop:

```bash
tmux new -s vizfold          # then `vizfold install openfold` inside it
```

Detach with `Ctrl-b d`, reattach with `tmux attach -t vizfold`. It takes about ten minutes once it
starts, plus the queue wait (8 minutes of build measured on Delta; Nexus unmeasured). Re-running it
resumes from the last completed step.

The install works out which machine it is on from the SLURM `ClusterName`, builds a micromamba
environment with OpenFold's CUDA extension, and links that machine's AlphaFold2 mirror, so nothing
large is downloaded.

| | Install prefix | AlphaFold2 mirror |
| --- | --- | --- |
| Nexus | `/projects/<you>/vizfold` | `/projects/alphafold2/database` |
| Delta | `/work/nvme/<alloc>/<you>/vizfold` | `/work/hdd/data/alphafold2/database` |
| DeltaAI | `/work/nvme/<alloc>/<you>/vizfold-gh` | `/work/hdd/data/alphafold2/database` |

Paths from here on are Nexus's. `vizfold status` prints yours.

DeltaAI's prefix is suffixed `-gh` on purpose: `/work/nvme` is shared with x86 Delta, and the
aarch64 environment must not clobber it. On Nexus the install also pins a matching NVRTC library —
its driver is older than the CUDA the environment ships, and without the pin relaxation fails. That
is automatic; it goes by as `driver CUDA … preloading libnvrtc…`.

Optionally, add the second backend:

```bash
vizfold install esmfold
```

ESMFold needs no AlphaFold2 databases and compiles no CUDA extension — it pulls its weights from
HuggingFace at fold time — so it installs faster, and gives the dashboard a second backend to serve.

**That is the sync point.** `vizfold status` should show `openfold ok`; step 3 below checks it
properly. Everything from here on happens in the session, with the presenter.

---

## 1. Create a session

In the **Sessions** view click **+**, pick your host, and switch to the **GPU** tab. Choose the
allocation, the resources, and how long you want them for:

| Field | Nexus | Delta | DeltaAI |
| --- | --- | --- | --- |
| Partition | `gpu` | `gpuA100x4-interactive` | `ghx4-interactive` |
| Account | `pearc26-tutorial` | `<your-alloc>-delta-gpu` | `<your-alloc>-dtai-gh` |
| GPUs | 1 | 1 | 1 |
| CPUs | 8 | 8 | 8 |
| Memory | 32 GB | 32 GB | 32 GB |
| Walltime | `01:00:00` | `01:00:00` | `01:00:00` |

- One hour covers the whole session: about ten minutes of OpenFold build, then the folds and the
  dashboard. Ask for more where the partition allows it — the `-interactive` partitions on Delta and
  DeltaAI **cap at one hour**, while `gpuA100x4` on Delta and `ghx4` on DeltaAI go to 48 hours with
  a queue wait in front.
- Ask for **32 GB** on all three, and no less: the VS Code server and the OpenFold build need it
  together, and a smaller job runs out of memory and takes the terminal down with it.

---

## 2. Start it, and connect

Click **Start**. CS Bridge writes the batch script, submits it with `sbatch`, and shows the job go
`submitting → queued → preparing → ready to connect`. Behind those states it starts the `linkspan`
agent on your compute node and exposes it over the Dev Tunnel; no inbound ports are opened on the
cluster.

Once the session reads **ready to connect**, click **Connect**. A new VS Code window opens, attached
to the compute node. Open a terminal in it — **Terminal → New Terminal**, or ``Ctrl+` `` — and
confirm where you are:

```bash
hostname                # a compute node, not a login node
nvidia-smi              # your GPU: A100 vGPU (Nexus), A100 (Delta), GH200 (DeltaAI)
```

Everything from here runs in that terminal, inside the allocation.

---

## 3. Check the install

```bash
vizfold status
```

```text
VizFold status

COMPONENT   STATUS  DETAIL
----------  ------  ------------------------------------------------------------
micromamba  ok      /home/<you>/.local/bin/micromamba
cli         ok      0.10.2 (latest)
repo        ok      /home/<you>/vizfold-repo at v0.10.2
config      ok      19 keys
openfold    ok      /projects/<you>/vizfold/envs/vizfold-openfold
esmfold     absent  not installed (/projects/<you>/vizfold/envs/vizfold-esmfold)
scheduler   ok      gpu, gpu, <your-account>, <your-account>

Everything checks out.

Config: /home/<you>/.config/vizfold/vizfold.json
  ESMFOLD_ENV_PREFIX = /projects/<you>/vizfold/envs/vizfold-esmfold
  OPENFOLD_ACCOUNT = <your-account>
  OPENFOLD_AF2_ROOT = /projects/alphafold2/database
  ...
  database = /projects/<you>/vizfold/vizfold.db (present)
```

`Everything checks out.` is what you need. Each of the seven rows is a part that can break on its
own, and anything wrong names itself here with a `Problems:` list and the command that fixes it
(`absent` = not installed; `unverified` = the check could not be run from here, which is not a
failure). `esmfold absent` is expected if you skipped it.

The prefix — environments, backend state, databases, every run — sits under your project space
rather than your quota-capped home; only the checkout, `~/vizfold-repo`, is on home. Both are
on filesystems the compute nodes share, so a later session finds this install where you left it.

---

## 4. See what you can fold

```bash
vizfold list proteins
```

```text
ID      RESIDUES  ALIGNMENTS  DESCRIPTION
------  --------  ----------  -------------------------------------
1G1J_1  43        Y           NON-STRUCTURAL GLYCOPROTEIN NSP4
1UBQ_1  76        Y           UBIQUITIN
1STM_1  157       Y           SATELLITE PANICUM MOSAIC VIRUS
6KWC_1  191       Y
2OMF_1  340       Y           MATRIX PORIN OUTER MEMBRANE PROTEIN F
```

**ALIGNMENTS** is the column to read before you fold. `Y` means `alignments/<id>` is already in the
checkout and the fold reuses it — seconds of setup. `N` means there is nothing to reuse and the run
pays for the full MSA search against the AlphaFold2 databases, which is the expensive part of a
prediction. Every bundled protein ships with its alignments, so all five read `Y`.

`vizfold list proteins --json` prints the same records for anything driving the CLI — `id`,
`residues`, `description`, `sequence`, and `alignments` as a boolean.

---

## 5. Fold from the CLI

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

`vizfold run` takes several targets and folds them in one execution, with the model loaded once:

```bash
vizfold run 1UBQ_1 1G1J_1          # one run, outputs keyed by FASTA tag
```

Attention maps are dumped by default; pass `--attn=false` to skip them.

The larger proteins need more GPU memory. Nexus's 10 GB A100 vGPU suits the shorter sequences —
`1UBQ_1` (76 residues) and `1G1J_1` (43) — while `6KWC_1` (191) and `2OMF_1` (340) are better run on
Delta or DeltaAI, where a 191-residue fold takes about **78 seconds** on a full A100.

Observe what landed:

```bash
vizfold list runs
vizfold show run 1
```

`vizfold show run 1` prints the run and its artifacts; the run directory is the `run_output_directory`
row of that table. A relaxed ubiquitin prediction is **1231 atoms**:

```bash
grep -c '^ATOM' /projects/<you>/vizfold/runs/1/predictions/1UBQ_1_model_1_ptm_relaxed.pdb
```

<details>
<summary>What that one command did</summary>

`vizfold run <target>...` takes bundled protein ids, paths to FASTAs, directories of FASTAs, or the
id of a run recorded earlier — recording the run first in every case but the last, and registering
the outputs when the fold lands.

Add `--no-exec` to record a run without folding it, for control over the inputs. The run's id and
sequence are read out of the FASTA, and preflight rejects a run recorded under any other name.
`vizfold run --help` lists every override.

```bash
vizfold run ./my-protein.fasta \
  --alignment-dir ./my-alignments \
  --no-exec
vizfold run 2                      # then fold it by id
```

The backend also installs its own CLI into its environment, which invokes the model directly:
no paths are filled in and no run is recorded.

```bash
micromamba run -p /projects/<you>/vizfold/envs/vizfold-openfold openfold --help
```
</details>

---

## 6. Open the dashboard

So far the structure is a path on disk. The run's last line pointed at `vizfold serve` — start it in
the same terminal.

```bash
vizfold serve
```

With no arguments it serves every backend you installed; name them (`vizfold serve openfold`) to
narrow it. It hands the dashboard the binary, the install prefix, the run database and the backend
list, so the dashboard drives exactly the install you just made.

```text
Starting workbench at http://localhost:3000 (openfold)
```

It starts straight away: `vizfold install repo` already staged the dashboard and installed its
dependencies, provisioning a Node ≥22.13 into your prefix if the node had none.

VS Code forwards that port automatically — check the **Ports** panel next to the terminal, where
`3000` should be listed. To view it **inside** VS Code:

> `Cmd/Ctrl+Shift+P` → **Simple Browser: Show** → `http://localhost:3000`

Drag that tab to the side so the browser and terminal are visible together.

The dashboard opens on three things: the **backends** being served, the **runs** already folded —
run 1 among them — and the **proteins available to fold**, the same list `vizfold list proteins`
printed. Click run 1: the predicted structure renders in a 3D viewer (drag to rotate, scroll to
zoom) alongside the attention maps for each layer and head.

---

## 7. Fold from the dashboard

The dashboard also submits folds, from the proteins it already knows about — nothing to upload, no
paths to type.

1. Pick one or more proteins from that list. Anything marked as carrying alignments folds without an
   MSA search; on Nexus's vGPU, stay with the shorter sequences.
2. Create the run from that selection and start it.
3. Watch its status move through `submitted` → `running` → `completed` on the run's own page.
4. Open each structure the run produced — one viewer per protein, each with its own attention maps.

Same executor, same work as step 8: the dashboard records the run and shells out to
`vizfold run <id>`.

Worth looking at while they are open:

- **1UBQ** is the classic β-grasp fold — a five-strand sheet wrapped around one α-helix. **1G1J** is
  a 43-residue viral peptide with almost no tertiary structure. Two very different things out of the
  same weights.
- The per-residue confidence colouring shows where the model is sure: termini and loops are the
  least confident regions in both, and the short peptide is far less confident overall.
- In the attention maps, compare an early layer against layer 47. Early layers attend locally along
  the sequence; late layers attend between residues far apart in sequence but adjacent in 3D. That
  is the geometric reasoning becoming visible.

On Delta or DeltaAI, fold a third: `6KWC_1` is a 191-residue β-jelly-roll xylanase, a dense sandwich
of β-sheets, and `2OMF_1` a 340-residue membrane porin — a β-barrel, about three minutes on a full
A100.

---

## 8. Clean up

The GPU session is the only transient component. End the job with **Stop** in the CS Bridge Sessions
view, or let the walltime expire.

Your structures, their attention maps, and the install behind them stay on the cluster filesystem.
**Restart** on the stopped session brings back the same partition, account and resources, with the
runs in the dashboard where you left them — and nothing from step 4 or 5 to repeat.

```bash
vizfold uninstall            # everything: both backends, the checkout, the config, the run database
vizfold uninstall openfold   # only that backend; config, runs, and the checkout stay
vizfold uninstall repo       # only the checkout
rm ~/.local/bin/vizfold
```

`install`, `update` and `uninstall` all take the same three parts — `repo`, `openfold`, `esmfold` —
so each is installed, moved and removed the same way. Bare `uninstall` prompts first.

The loop is the same for a sequence of your own: point `vizfold run` at your FASTA and read the
result in this dashboard — here on the demo Nexus, or on production Nexus, Delta and DeltaAI, where
a full card takes the longer sequences too. Protein folding is one task; the session, the CLI and
the dashboard under it are what the next ones will use.

---

## Troubleshooting

**Anything wrong with the install itself — start with `vizfold status`.** It reports each part
(micromamba, cli, repo, config, each backend, scheduler) and lists what is broken with the command
that fixes it. Most of the entries below are what those problems look like.

**No hosts listed in CS Bridge.** `~/.ssh/config` is empty or unreadable. Add the host with the
**+** button in SSH Hosts, then hit refresh.

**Microsoft sign-in fails.** Your network is blocking `login.microsoftonline.com` or
`*.devtunnels.ms`. Both must be reachable; the Dev Tunnel is the only supported transport today.

**Job stuck in `PENDING`.** The partition is full or you asked for too much. Try fewer CPUs or less
memory, or run `squeue -u $USER --start` on the login node for an estimate.

**"Slurm is not available".** You picked a host with no `sinfo` on `PATH` — probably not a login
node.

**The Connect window disconnects.** The session shows **Unreachable**; click **Reconnect** to
rebuild the relay. `View → Output → CS Bridge` shows the failing step.

**`repo: no checkout at …`.** A backend install, or `update`, before `vizfold install repo`.
Run that first; it is the only thing that clones.

**`config: not initialized`, then `-> vizfold install <backend>`.** Nothing has written
`~/.config/vizfold/vizfold.json` yet, or the freshly written one has not propagated across NFS.
Check `vizfold status`, wait a few seconds, retry.

**`No proteins under <dir>. Re-run vizfold install openfold.`** The proteins come from
`$OPENFOLD_HOME/examples/monomer/`, so `OPENFOLD_HOME` points at something that is not a full
checkout. A missing checkout reports itself as `repo: no checkout at …` before this ever prints;
`vizfold status` says so as `repo absent`, `vizfold install repo` creates it, and
`vizfold update repo` brings it back to this binary's release.

**`vizfold status` says the config was written by a different vizfold.** The config on disk came
from an older release and holds names this binary no longer reads. `vizfold install openfold`
rewrites it.

**The install says `site [local]`, then `no install prefix`.** It could not work out which cluster
you are on — Delta's login nodes cannot always reach the Slurm controller, so `scontrol show config`
returns nothing. Name the site yourself:

```bash
OPENFOLD_SITE=nexus-dev vizfold install openfold   # or delta / delta-gh
```

**`Invalid account or account/partition combination`.** The GPU account and partition must match —
see the table in step 2. Confirm yours with `sacctmgr -nP show assoc user=$USER format=account`.
`vizfold status` checks both names against the scheduler and says which one it does not recognise.

**The build ran out of memory.** The session was started with less than 32 GB, and the VS Code
server and the OpenFold build do not fit together below that. Stop the session, start one with more,
and re-run `vizfold install openfold` — it resumes from the last completed step.

**Port 3000 does not open.** Check the **Ports** panel — if `3000` is absent, VS Code missed the
auto-forward. Add it manually with **Forward a Port**.

**A dashboard fold sticks on `submitted`.** The run's own page shows its error message once SLURM
reports back. The deeper trace is `/projects/<you>/vizfold/runs/<id>.submit.log`.

**`vizfold status` says `openfold absent`, but you installed it in an earlier session.** That
session was on a different machine — check `hostname` against the one you used. Delta and DeltaAI
share `/work/nvme` but not their environments, and an install done on one does not serve the other.

---

## Where to get help

- CS Bridge issues: <https://github.com/cyber-shuttle/CS-Bridge/issues>
- VizFold: <https://github.com/AI2Science/vizfold-foundation>
- Both are built by the [ARTISAN research group](https://gt-artisan.github.io/) at Georgia Tech.
