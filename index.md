# Nexus Documentation

Nexus is a unified AI and scientific computing platform designed to support
research requiring interactive computing, batch HPC, data-intensive workflows,
and AI-enabled science. It is comprised of systems designed to help researchers move smoothly from
local development environments to large-scale production runs while keeping
data, software, and researcher workflows connected.

The documentation site is organized to support both traditional HPC usage and
the broader Nexus platform vision. Users who want to log in, move data, run
jobs, and find software should be able to get productive quickly. Users who
want Jupyter, VS Code, orchestration, checkpoint restart, shared model
services, and federation to other resources will also find a clear path.

## Start here

If you are new to Nexus, begin with these pages:

- {doc}`quickstart`
- {doc}`overview/architecture`
- {doc}`access/accounts`
- {doc}`access/login`
- {doc}`support/help`

Nexus documentation covers the login commands and batch scripts, and the
advanced sections explain interactive development, persistent services, data
movement, orchestration, and how work can extend outward to systems such as
Delta and DeltaAI.

## System Status

Keep an eye on status updates here:
 
- {doc}`status`

```{toctree}
:maxdepth: 2
:caption: Getting Started

quickstart
%overview/architecture
overview/hardware
%overview/platform
%access/accounts
access/login
```

```{toctree}
:maxdepth: 2
:caption: User Guide

data/storage
data/data-transfer
software/environment
software/containers
jobs/slurm-basics
%jobs/gpu-jobs
jobs/interactive
jobs/checkpoint-restart
%interactive/vscode
%interactive/jupyter
training/index
support/help
%support/faq
%policies/security
%policies/acceptable-use
%policies/acknowledgment
```
