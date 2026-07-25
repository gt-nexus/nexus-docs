# Hardware Details

Nexus integrates NVIDIA DGX B200 systems and RTX PRO 6000 Blackwell Server Edition GPUs. The platform organizes these GPU resources into three categories: flagship DGX nodes for large-scale training and tightly coupled workloads, scheduled RTX nodes for flexible AI and scientific computing, and persistent-service RTX nodes for long-running inference, gateways, and other service-oriented workloads.

## System Summary

| Resource | Aggregate |
|---|---|
| GPUs | 480 |
| CPU cores | 8,576 |
| System memory | 118 TB |
| Node-local NVMe storage | ~2.0 PB |
| Shared all-flash storage | 10+ PB |

## Node Inventory

| Category | Location | Nodes | GPUs | CPU cores | System memory | Node-local NVMe |
|---|---|---:|---:|---:|---:|---:|
| DGX B200 | Georgia Tech | 16 | 128 | 1,792 | 32 TB | 547.2 TB |
| Scheduled RTX PRO 6000 | Georgia Tech | 38 | 304 | 4,864 | 70 TB | 1,203.84 TB |
| Persistent-service RTX PRO 6000 | Georgia Tech and NCSA | 6 | 48 | 768 | 10 TB | 190.08 TB |
| CPU/admin | Georgia Tech | 12 | — | 1,152 | 6 TB | 46.08 TB |
| **Total** |  | **72** | **480** | **8,576** | **118 TB** | **1,987.2 TB** |

## Flagship AI Nodes (DGX-Class Systems)

Designed for large-scale AI/ML training, multi-GPU workloads, and high-performance scientific simulations. Nexus includes **16 DGX-class nodes**, delivering 128 GPUs, 1,792 CPU cores, 32 TB of system memory, and 547.2 TB of aggregate node-local storage.

Each node is equipped with:

- 8× NVIDIA B200-class GPUs
- High-bandwidth HBM (~180 GB per GPU)
- NVSwitch-based intra-node connectivity
- Dual Intel Xeon processors (112 total CPU cores)
- 2 TB system memory per node
- 34.2 TB NVMe local storage per node
- 800 Gb/s NDR InfiniBand connectivity
- NVIDIA BlueField-3 DPUs for accelerated networking

## Scheduled AI Compute Nodes (RTX-Based Systems)

Designed to support a broad range of scheduled AI, simulation, and data-intensive workloads. Nexus includes **38 scheduled RTX-based GPU nodes**, delivering 304 GPUs, 4,864 CPU cores, 70 TB of system memory, and approximately 1.20 PB of aggregate node-local storage.

Each node is equipped with:

- 8× NVIDIA RTX PRO 6000 Blackwell Server Edition GPUs (96 GB GDDR7 per GPU)
- Dual Intel Xeon 6767P processors (128 total CPU cores)
- 32 nodes with 2 TB system memory per node
- 6 nodes with 1 TB system memory per node
- 1× 960 GB NVMe boot drive
- 8× 3.84 TB NVMe local data drives
- 31.68 TB NVMe local storage per node
- 2× 400 Gb/s NVIDIA ConnectX-7 VPI adapters
- Integrated dual-port 10 GbE connectivity for management and data services

## Persistent AI Service Nodes

Nexus includes **6 persistent-service GPU nodes**: 4 Type 4 systems at Georgia Tech and 2 systems at NCSA. Together, they deliver 48 NVIDIA RTX PRO 6000 GPUs, 768 CPU cores, 10 TB of system memory, and 190.08 TB of node-local NVMe storage. These systems support long-running, non-Slurm services such as shared model inference, scientific gateways, and other persistent AI-enabled workflows.

All six nodes provide:

- 8× NVIDIA RTX PRO 6000 Blackwell Server Edition GPUs (96 GB GDDR7 per GPU)
- Dual 64-core Intel Xeon processors (128 total CPU cores)
- 31.68 TB of node-local NVMe storage

The deployment-specific configurations are:

| Deployment | Nodes | Platform | System memory per node | NVMe configuration per node | High-speed networking |
|---|---:|---|---:|---|---|
| Georgia Tech Type 4 | 4 | Relion XE4418GT-Air; dual Intel Xeon 6767P | 2 TB DDR5 | 1× 960 GB boot and 8× 3.84 TB data | 2× ConnectX-7 VPI at 400 Gb/s |
| NCSA | 2 | HPE ProLiant DL380a Gen12; dual Intel Xeon 6760P | 1 TB DDR5 | 2× 480 GB RAID 1 boot and 4× 7.68 TB data | 4× 100 GbE ports |

## High-Performance Networking and Fabric

The primary Nexus compute and storage infrastructure at Georgia Tech integrates NVIDIA NDR InfiniBand fabrics operating at up to 800 Gb/s, enabling low-latency, high-throughput communication across compute and storage resources. The NCSA persistent-service nodes use 100 GbE connectivity for service-oriented and federated workflows. The networking infrastructure includes:

- Non-blocking compute fabric for DGX nodes using an 8-rail NDR InfiniBand topology
- Dedicated storage fabric optimized for high-throughput data movement between compute and the VAST storage system
- NVIDIA QM9700 switches (32-port, 800 Gb/s) deployed across compute and storage tiers
- High-speed optical transceivers and copper/optical cabling supporting NDR connectivity
- NVIDIA UFM (Unified Fabric Manager) appliances for centralized monitoring and management of north-south and east-west traffic
- 400 Gb/s ConnectX-7 connectivity for Georgia Tech RTX compute and persistent-service nodes
- 100 GbE connectivity for the NCSA persistent-service nodes
- A separate 1/10 Gb Ethernet management network for in-band and out-of-band system control

## High-Performance Storage System

The Nexus storage system is built on the VAST Data platform, an all-flash architecture designed for high-bandwidth AI workloads, efficient handling of large shared datasets, and seamless integration with the compute fabric for end-to-end data-driven workflows. The system leverages a disaggregated architecture combining storage-class memory (SCM) and NVMe flash to deliver scalable performance and capacity.

The storage infrastructure includes **8 VAST Ceres V2 storage appliances**, each equipped with:

- ~1.35 PB NVMe flash capacity per appliance
- 12.8 TB storage-class memory (SCM) for acceleration
- NVIDIA BlueField-3 DPUs for data movement and offload
- Aggregate raw NVMe capacity of ~10.8 PB
- A dedicated high-speed backend network (200–400 Gb Ethernet) supported by NVIDIA SN4700 switches

## Management and Interactive Nodes

Supporting system services, user access, and workflow orchestration. Nexus includes **12 management and interactive nodes**, delivering 1,152 CPU cores, 6 TB of system memory, and approximately 46 TB of aggregate node-local storage.

Each node is equipped with:

- Dual Intel Xeon processors (96 total CPU cores)
- 0.5 TB system memory per node
- 3.84 TB NVMe local storage
- 400 Gb/s ConnectX-7 networking for high-performance data movement
- 10 Gb Ethernet connectivity for management and access services
