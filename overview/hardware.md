# Hardware Details

Nexus integrates NVIDIA DGX B200 systems and RTX PRO 6000 Blackwell Server Edition GPUs. The DGX B200 nodes provide a purpose-built AI supercomputing foundation with tightly coupled GPUs, high-bandwidth interconnects, and optimized software for large-scale model training and inference, while the RTX PRO 6000-based nodes offer flexible, high-memory GPU resources for a wide range of AI, simulation, and data-intensive workloads.

## System Summary

| Resource | Aggregate |
|---|---|
| GPUs | 464 |
| CPU cores | 8,320 |
| System memory | 116 TB |
| Node-local NVMe storage | ~1.9 PB |
| Shared all-flash storage | 10+ PB |

## Flagship AI Nodes (DGX-Class Systems)

Designed for large-scale AI/ML training, multi-GPU workloads, and high-performance scientific simulations. Nexus includes **16 DGX-class nodes**, delivering 128 GPUs, 1,792 CPU cores, 32 TB of system memory, and 547 TB of aggregate node-local storage.

Each node is equipped with:

- 8× NVIDIA B200-class GPUs
- High-bandwidth HBM (~180 GB per GPU)
- NVSwitch-based intra-node connectivity
- Dual Intel Xeon processors (112 total CPU cores)
- 2 TB system memory per node
- 34.2 TB NVMe local storage per node
- 800 Gb/s NDR InfiniBand connectivity
- NVIDIA BlueField-3 DPUs for accelerated networking

## Flexible AI Compute Nodes (RTX-Based Systems)

Designed to support a broad range of AI, simulation, and data-intensive workloads. Nexus includes **42 RTX-based GPU nodes**, delivering 336 GPUs, 5,376 CPU cores, 78 TB of system memory, and approximately 1.33 PB of aggregate node-local storage.

Each node is equipped with:

- 8× NVIDIA RTX PRO 6000 GPUs (96 GB GDDR7 per GPU)
- Dual Intel Xeon processors (128 total CPU cores)
- 36 nodes with 2 TB system memory per node
- 6 nodes with 1 TB system memory per node
- 31.68 TB NVMe local storage per node
- 400 Gb/s NVIDIA ConnectX-7 networking for high-performance communication
- Integrated Ethernet connectivity for management and data services

## High-Performance Networking and Fabric

Nexus integrates NVIDIA NDR InfiniBand fabrics operating at up to 800 Gb/s, enabling low-latency, high-throughput communication across compute and storage resources. The networking infrastructure includes:

- Non-blocking compute fabric for DGX nodes using an 8-rail NDR InfiniBand topology
- Dedicated storage fabric optimized for high-throughput data movement between compute and the VAST storage system
- NVIDIA QM9700 switches (32-port, 800 Gb/s) deployed across compute and storage tiers
- High-speed optical transceivers and copper/optical cabling supporting NDR connectivity
- NVIDIA UFM (Unified Fabric Manager) appliances for centralized monitoring and management of north-south and east-west traffic
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
