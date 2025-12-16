Here's the RCA document without automation references, focused on manual human execution:

```markdown
# Root Cause Analysis: macOS to ContainerLab Network Connectivity Loss

## Issue Summary

Loss of network connectivity from macOS host to ContainerLab devices running in a Debian VM within OrbStack. The devices are on the `172.29.163.0/24` network and were previously accessible but suddenly became unreachable.

## Environment

- **Host OS**: macOS with OrbStack
- **VM**: Debian Bookworm (IP: 192.168.139.193)
- **Container Runtime**: Docker inside Debian VM
- **Network Tool**: ContainerLab
- **Affected Network**: `172.29.163.0/24` (clab Docker network)
- **Devices**: 4x Arista cEOS containers (spine1, spine2, leaf1, leaf2)

## Symptoms

- Unable to ping any device on `172.29.163.0/24` from macOS
- Unable to SSH to devices from macOS
- Connectivity from within Debian VM to devices works fine
- Other services (Nautobot on published ports) accessible from macOS via port forwarding

## Root Cause

**OrbStack's automatic network route management created an incorrect route for the ContainerLab network.**

When ContainerLab creates the `clab` Docker network inside the Debian VM, OrbStack detects it and automatically creates a route on macOS. However, OrbStack routes this traffic through its own internal gateway (`172.23.44.64` via virtual interface `feth3256`) instead of directly to the Debian VM (`192.168.139.193`).

The OrbStack internal gateway exists and is reachable, but it does not have proper forwarding/NAT rules to reach containers running inside the nested Debian VM, resulting in all traffic to `172.29.163.0/24` being dropped.

## Troubleshooting Steps

### 1. Verify Network Connectivity to Debian VM

```bash
# From macOS
ping 192.168.139.193
```

**Expected**: Should respond successfully
**Purpose**: Confirms basic connectivity to the VM host

### 2. Check Routing Table on macOS

```bash
# From macOS
netstat -nr | grep 172.29.163
```

**Expected Output (Problematic)**:
```
172.29.163/24      172.23.44.64       UGSc             feth3256
```

**Issue Identified**: Route points to OrbStack's internal gateway instead of the Debian VM

### 3. Test OrbStack Gateway Reachability

```bash
# From macOS
ping 172.23.44.64
```

**Expected**: Gateway responds (confirming it exists)
**Finding**: Gateway exists but doesn't forward traffic correctly

### 4. Verify Connectivity from Inside Debian VM

```bash
# SSH to Debian VM
ssh user@192.168.139.193

# Test from inside VM
ping 172.29.163.101  # spine1
ping 172.29.163.2    # nautobot
```

**Expected**: All pings work
**Purpose**: Confirms the Docker network and containers are functioning correctly

### 5. Check Docker Network Configuration

```bash
# From inside Debian VM
docker network inspect clab
```

**Purpose**: Verify the network subnet and gateway configuration match expectations
**Expected**: Subnet `172.29.163.0/24`, Gateway `172.29.163.1`

### 6. Check OrbStack VM Status

```bash
# From macOS
orb list
orb status
```

**Purpose**: Verify OrbStack and the Debian VM are running correctly

## Solution

### Immediate Fix (Temporary - Lost on Reboot)

```bash
# From macOS - Delete OrbStack's incorrect route
sudo route -n delete 172.29.163.0/24

# Immediately add correct route pointing to Debian VM
sudo route -n add 172.29.163.0/24 192.168.139.193

# Verify the route
netstat -nr | grep 172.29.163
```

**Expected Output**:
```
172.29.163/24      192.168.139.193    UGSc             <interface>
```

### Verify Fix

```bash
# From macOS
ping 172.29.163.101
ssh batman@172.29.163.101
```

### Making the Fix Persistent

**Note**: This fix must be re-applied after each macOS reboot or OrbStack restart.

**Option 1: Manual Re-application**

After each reboot, simply run:
```bash
sudo route -n delete 172.29.163.0/24 2>/dev/null
sudo route -n add 172.29.163.0/24 192.168.139.193
```

**Option 2: Create a Helper Script**

Create `~/fix-clab-route.sh`:

```bash
#!/bin/bash
sudo route -n delete 172.29.163.0/24 2>/dev/null
sudo route -n add 172.29.163.0/24 192.168.139.193
echo "ContainerLab route fixed - network should now be accessible"
```

Make it executable:
```bash
chmod +x ~/fix-clab-route.sh
```

Run it whenever needed:
```bash
~/fix-clab-route.sh
```

**Option 3: Shell Alias (for convenience)**

Add to `~/.zshrc` or `~/.bashrc`:

```bash
# Fix ContainerLab routing after OrbStack starts
alias fix-clab='sudo route -n delete 172.29.163.0/24 2>/dev/null; sudo route -n add 172.29.163.0/24 192.168.139.193 && echo "Route fixed"'
```

Reload your shell config:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

Then just run:
```bash
fix-clab
```

## Why This Happened

1. **OrbStack's Network Auto-Discovery**: OrbStack monitors Docker networks and automatically creates routes for them on the macOS host
2. **Nested Container Setup**: ContainerLab runs inside a Debian VM, which itself runs in OrbStack
3. **Routing Ambiguity**: OrbStack's auto-discovery doesn't properly handle nested Docker networks and routes them through its internal gateway instead of the VM
4. **Gateway Forwarding Gap**: The OrbStack internal gateway (`172.23.44.64`) lacks proper forwarding rules to reach containers inside the nested Debian VM

## When to Re-apply the Fix

The route correction must be re-applied after:
- macOS reboot
- OrbStack restart (`orb stop` / `orb start`)
- Debian VM restart
- `clab` Docker network recreation

**Recommended**: Keep the helper script or alias handy and run it after any of these events.

## Alternative Approach (If Route Fix Doesn't Work)

If the route fix fails or causes other issues, use SSH port forwarding:

**On Debian VM**, expose device SSH ports by modifying containerlab deployment or using `socat`:

```bash
# Example using socat for spine1
socat TCP-LISTEN:2201,fork TCP:172.29.163.101:22 &
socat TCP-LISTEN:2202,fork TCP:172.29.163.102:22 &
socat TCP-LISTEN:2203,fork TCP:172.29.163.103:22 &
socat TCP-LISTEN:2204,fork TCP:172.29.163.104:22 &
```

**From macOS**, access via forwarded ports:
```bash
ssh batman@192.168.139.193 -p 2201  # spine1
ssh batman@192.168.139.193 -p 2202  # spine2
ssh batman@192.168.139.193 -p 2203  # leaf1
ssh batman@192.168.139.193 -p 2204  # leaf2
```

## Verification Commands

After applying the fix, verify full connectivity:

```bash
# From macOS - Test connectivity to all devices
ping 172.29.163.101  # spine1
ping 172.29.163.102  # spine2
ping 172.29.163.103  # leaf1
ping 172.29.163.104  # leaf2

# Test SSH access
ssh batman@172.29.163.101  # Should prompt for password
```

## Related Issues

- **Nautobot Access Works**: Nautobot is accessible via `localhost:8080` because it uses published ports (`0.0.0.0:8080->8080/tcp`), which bypass the routing issue entirely
- **Debian VM Internal Access Works**: All connectivity from within the Debian VM works because it uses Docker's internal network directly
- **Only macOS Direct IP Access Affected**: The issue only affects direct IP access from macOS to container IPs

## Technical Details

**Incorrect Route (Created by OrbStack)**:
```
Destination: 172.29.163.0/24
Gateway: 172.23.44.64
Interface: feth3256 (OrbStack virtual interface)
```

**Correct Route (Manual Override)**:
```
Destination: 172.29.163.0/24
Gateway: 192.168.139.193 (Debian VM)
Interface: (OrbStack's VM interface)
```

The correct route ensures traffic destined for the ContainerLab network goes directly to the Debian VM, which has proper access to the Docker bridge network (`br-ca0835f2a1e5`) where the containers are attached.

## Quick Reference

**Check if fix is needed:**
```bash
netstat -nr | grep 172.29.163
# If gateway is 172.23.44.64, fix is needed
```

**Apply the fix:**
```bash
sudo route -n delete 172.29.163.0/24 2>/dev/null
sudo route -n add 172.29.163.0/24 192.168.139.193
```

**Verify it worked:**
```bash
ping 172.29.163.101
```
