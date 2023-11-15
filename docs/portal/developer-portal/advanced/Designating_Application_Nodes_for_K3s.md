# Designating Application Nodes for K3s (Technical Preview)

**WARNING**: This feature is a Technical Preview. Future releases will streamline these manual configuration steps. Therefore, some of these configuration options may change in future releases.

## Overview

Before K3s can be enabled to support UAIs on Application nodes, the Application nodes must be grouped in HSM as either `k3s_server` or `k3s_agent` nodes. The UAN Ansible K3s playbook uses these groups to determine what role they will have. Nodes grouped as `k3s_server` will become K3s control-plane (master) nodes, while nodes grouped as `k3s_agent` will become K3s agent (worker) nodes.

When assigning roles, carefully consider the number of `k3s_server` nodes such that a quorum is maintained. A minimum of three `k3s_server` nodes are required for a quorum. Consult [K3s High Availability](https://docs.k3s.io/datastore/ha-embedded) documentation for more information.

**INFO:** For more information on how CFS uses HSM node groups to create Ansible host groups, see the [Cray System Management Documentation](https://cray-hpe.github.io/docs-csm). Follow the links to the `Cray System Management Administration Guide->Configuration Management->Ansible Inventory->Dynamic inventory and host groups` section.

When HPE Cray Supercomputing UAN software is installed or upgraded using IUF, and these HSM node groups do not exist or have no members, one `Application_UAN` node type will be placed in the `k3s_server` group. The remaining nodes will be placed in the `k3s_agent` group. If these groups exist and are not empty, IUF will not change them.

This document provides procedures to manually change the membership of the `k3s_server` and `k3s_agent` HSM node groups.

## Procedures

### Getting a List of all Application_UAN Nodes 

This command gathers all nodes with the `Application` role and `UAN` subrole from HSM. The output is sorted by XNAME.

```bash
$ cray hsm state components list \
--role Application --subrole UAN \
--format json | jq -r '.Components[].ID' \
| sort
   ```

### Getting the Members of an HSM Node Group

This command returns the members of a given HSM Node Group. Substitute either `k3s_server` or `k3s_agent` for `GROUP_NAME`.

```bash
$ cray hsm groups members list $GROUP_NAME
```

### Creating the HSM Node Group

If the HSM Node Group does not exist, the `cray hsm groups create` command can create it. The following two examples show how group members may be provided as a comma-separated string of XNAMEs on the command line, or listed in a file.

**NOTE:** HSM Node Groups used for K3s must be exclusive. That is, a given node may be in either the `k3s_server` or `k3s_agent` group, not both. HSM provides the `exclusive-group` element to enforce this policy. By having the `k3s_server` and `k3s_agent` groups have the same `k3s` `exclusive-group`, nodes are prevented from being members of both.

This example creates the `k3s_server` group listing members on the command line.

 ```bash
 $ cray hsm groups create \
 --members-ids "XNAME1,XNAME2,..." \
 --exclusive-group "K3s" \
 --description "K3s Control-Plane Nodes"\
 --label "k3s_server"
 ```

This example creates the `k3s_agent` group using members in a text file.

 ```bash
 $ cray hsm groups create \
 --members-file /path-to-member-file \
 --exclusive-group "K3s" \
 --description "K3s Agent Nodes"\
 --label "k3s_agent"
   ```

### Modifying the HSM Node Group

The `cray hsm groups members create` and `cray hsm groups members delete` commands modify membership of an existing HSM Node Group. In these examples, `GROUP_NAME` would be either `k3s_server` or `k3s_agent`.

#### Adding a Member

```bash
$ cray hsm groups members create --id XNAME $GROUP_NAME
```

#### Deleting a Member

```bash
$ cray hsm groups members delete XNAME $GROUP_NAME
```

### Deleting an HSM Node Group

This command deletes the node group contained in `GROUP_NAME`.

```bash
$ cray hsm groups delete $GROUP_NAME
```
