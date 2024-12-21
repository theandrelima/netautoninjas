# MPLS L3 VPN Setup

This project sets up an MPLS Layer 3 VPN topology using Containerlab. The topology consists of multiple clients and Cisco XRv routers, configured to support MPLS L3 VPN services.

## Topology Overview

The topology includes three sites, each with its own clients and PE routers, all interconnected through a central router:

- **Site 1**:
  - Client 1 connected to PE Router 1 (vpn_a)
  - Client 2 connected to PE Router 1 (vpn_b)

- **Site 2**:
  - Client 3 connected to PE Router 2 (vpn_a)

- **Site 3**:
  - Client 4 connected to PE Router 3 (vpn_b)

- **Central Router**:
  - Router Reflector (p_rtr1) connecting all PE routers.

## Project Structure

- `clab.yaml`: Defines the Containerlab topology, specifying nodes, types, connections, and configurations.
- `configs/`: Contains individual configuration files for each client and router.
  - `client1.cfg`: Configuration for Client 1.
  - `client2.cfg`: Configuration for Client 2.
  - `client3.cfg`: Configuration for Client 3.
  - `client4.cfg`: Configuration for Client 4.
  - `pe_rtr1.cfg`: Configuration for PE Router 1.
  - `pe_rtr2.cfg`: Configuration for PE Router 2.
  - `pe_rtr3.cfg`: Configuration for PE Router 3.
  - `p_rtr1.cfg`: Configuration for the central Router Reflector.

## Setup Instructions

1. Ensure you have Containerlab installed on your system.
2. Clone this repository to your local machine.
3. Navigate to the project directory.
4. Run the following command to deploy the topology:
   ```
   containerlab deploy -t clab.yaml
   ```
5. Access the clients and routers using the provided configuration files for further customization and testing.

## Additional Information

This setup utilizes BGP for routing and LDP for label distribution, ensuring efficient MPLS operations across the network. Each client is assigned to a specific VPN, allowing for isolated traffic flows.