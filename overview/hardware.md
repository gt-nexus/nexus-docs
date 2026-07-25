# Hardware Details

Nexus combines scheduled AI and scientific computing resources at Georgia Tech with persistent-service resources at Georgia Tech and NCSA. The installed system includes NVIDIA DGX B200 nodes for tightly coupled AI workloads, NVIDIA RTX PRO 6000 Blackwell Server Edition nodes for flexible GPU computing, and dedicated RTX-based nodes for long-running services.


## Choose a Resource

| Resource | Best suited for | Access model | Installed scale | GPU memory per node | Location |
|---|---|---|---:|---:|---|
| DGX B200 | Large-model training, tightly coupled multi-GPU workloads, and communication-intensive simulations | Scheduled through Slurm | 16 nodes / 128 GPUs | 1.44 TB HBM | Georgia Tech |
| Scheduled RTX PRO 6000 | General AI, inference, fine-tuning, simulation, data analysis, and single- or multi-GPU jobs | Scheduled through Slurm | 38 nodes / 304 GPUs | 768 GB GDDR7 | Georgia Tech |
| Persistent-service RTX PRO 6000 | Model-serving endpoints, scientific gateways, and other long-running services | Managed, non-Slurm access | 6 nodes / 48 GPUs | 768 GB GDDR7 | Georgia Tech and NCSA |

## Installed Node Inventory

| Category | Location | Access | Nodes | GPUs | CPU cores | System memory |
|---|---|---|---:|---:|---:|---:|
| DGX B200 | Georgia Tech | Slurm | 16 | 128 | 1,792 | 32 TB |
| Scheduled RTX PRO 6000 | Georgia Tech | Slurm | 38 | 304 | 4,864 | 70 TB |
| Persistent-service RTX PRO 6000 | Georgia Tech and NCSA | Managed service | 6 | 48 | 768 | 10 TB |
| Management and administrative | Georgia Tech | Platform operations | 12 | - | 1,152 | 6 TB |
| **Total installed** |  |  | **72** | **480** | **8,576** | **118 TB** |

The 480 installed GPUs consist of 432 GPUs in scheduled compute pools and 48 GPUs assigned to persistent-service infrastructure. The 12 management and administrative nodes support platform operations and are not a general-purpose compute pool.

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

Nexus includes six RTX PRO 6000 nodes dedicated to persistent services: four at Georgia Tech and two at NCSA. Together, they provide 48 GPUs, 768 CPU cores, 10 TB of system memory, and 184.32 TB of NVMe data capacity.

All six nodes include:

- 8× NVIDIA RTX PRO 6000 Blackwell Server Edition GPUs with 96 GB GDDR7 per GPU
- 768 GB aggregate GPU memory
- Dual 64-core Intel Xeon processors with 128 total CPU cores
- 30.72 TB of node-local NVMe data capacity

Deployment-specific differences are summarized below.

| Deployment | Nodes | Platform | System memory per node | Boot storage | Data storage | High-speed networking |
|---|---:|---|---:|---|---|---|
| Georgia Tech persistent service | 4 | Dual Intel Xeon 6767P processors | 2 TB DDR5 | 1× 960 GB NVMe | 8× 3.84 TB NVMe | 2× ConnectX-7 VPI at up to 400 Gb/s |
| NCSA persistent service | 2 | Dual Intel Xeon 6760P processors | 1 TB DDR5 | 2× 480 GB NVMe in RAID 1 | 4× 7.68 TB NVMe | 4× 100 GbE ports |

Persistent services are not submitted as Slurm jobs. Placement at Georgia Tech or NCSA depends on the service's security, data, networking, and operational requirements.

## High-Performance Storage System

The Nexus storage system is built on the VAST Data platform, an all-flash architecture designed for high-bandwidth AI workloads, efficient handling of large shared datasets, and seamless integration with the compute fabric for end-to-end data-driven workflows. The system leverages a disaggregated architecture combining storage-class memory (SCM) and NVMe flash to deliver scalable performance and capacity.

The storage infrastructure includes **8 VAST Ceres V2 storage appliances**, each equipped with:

- ~1.35 PB NVMe flash capacity per appliance
- 12.8 TB storage-class memory (SCM) for acceleration
- NVIDIA BlueField-3 DPUs for data movement and offload
- Aggregate raw NVMe capacity of ~10.8 PB
- A dedicated high-speed backend network (200–400 Gb Ethernet) supported by NVIDIA SN4700 switches

## Networking and Site Boundaries

The Georgia Tech DGX pool uses an eight-rail, non-blocking NDR InfiniBand compute fabric. Georgia Tech RTX compute and persistent-service nodes use NVIDIA ConnectX-7 connectivity at up to 400 Gb/s. The two NCSA persistent-service nodes use 100 GbE networking.

Published interface rates describe installed link capabilities; they are not guaranteed application throughput. Workload performance depends on communication patterns, protocol, topology, storage access, and system load.

Georgia Tech and NCSA are distinct deployment sites. Users should confirm data location, storage mounts, identity integration, endpoint exposure, and federation status before planning workflows that span both sites.

## Management and Administrative Nodes

Twelve CPU-only nodes support platform administration, user access, workflow orchestration, and related system services. These nodes are not part of the general-purpose compute pool.

Each node includes:

- 2× Intel Xeon processors with 96 total CPU cores
- 512 GB system memory
- 2× 1.92 TB NVMe drives
- 2× NVIDIA ConnectX-7 VPI adapters operating at up to 400 Gb/s
- Dual-port 10 GbE connectivity
