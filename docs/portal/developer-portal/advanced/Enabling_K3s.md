# Configuring a UAN for K3s (Technical Preview)

**WARNING**: This feature is a Technical Preview, as such it requires completion of the [Prerequisites](#prerequisites) section. Future releases will streamline these manual configuration steps and enhance the experience of using the rootless Podman containers. Therefore, some of these configuration options may change in future releases.

## UAI Experience on UANs
In HPE Cray Supercomputing UAN release 2.6, a new playbook has been added to create a single node, K3s cluster. This K3s environment can then run the services necessary to replicate the experience of User Access Instances (UAIs) on one or more UANs.

### Use of K3s
K3s will serve as the orchestrator of services necessary to replicate the capabilities of UAIs on UAN hardware. These services include HAProxy, MetalLB, and eventually DNS services like ExternalDNS and PowerDNS. Notably, this does **not** orchestrate instances of `sshd` and `podman` containers through K3s. K3s and the initial set of services mimic how the "Broker UAIs" in CSM to handle the SSH ingress and redirection of users into their interactive environment.

### Use of Podman
Traditional UAIs in CSM required some level of privilege in CSM for access to host volume mounts, networking, and startup activities. Podman containers offer an attractive solution for an interactive environment in which to place users. They can be rootless containers that do not rely on privilege escalation. When running on UANs, Podman containers have access to a hosting environment that is already tailored to users.

### Overview
The overall component flow for replicating containerized environments for End-Users on UANs is as follows:
1. A user uses `ssh` to initiate a connection to the HAProxy load-balancer running in K3s.
1. HAProxy, using the configured load balancing algorithms, will forward the SSH connection to an instance of `sshd` running on a UAN.
1. `sshd`, running on a UAN through systemd, will initiate a rootless Podman container as the user using the `ForceCommand` configuration.
1. The user is placed in a Podman container for an interactive session, or their `SSH_ORIGINAL_COMMAND` is run in the container.
1. When the user disconnects, the Podman process exits, and the container is removed.

There are alternate configurations of Podman that would allow for different workflows. For example, the main pid of the container could be long running, to facilitate easier re-entry to the container on subsequent logins. 

## Prerequisites 

The following steps must be completed prior to configuring the UAN with K3s.

1. Designate a UAN to operate as the K3s control-plane node. See [Designating Application Nodes for K3s](Designating_Application_Nodes_for_K3s.md).

  **Note**: In a future release, additional UANs will be able to join as extra manager or worker nodes. 

1. Identify a pool of IP addresses for the services running in K3s.

  **Note**: The identification of a pool of IP addresses for the services running in K3s is best made at system installation time in order to avoid the possibility of IP collisions. If this is not possible, steps must be taken to ensure IP collisions are avoided.
   
  This address pool must be routable from the UAN control-plane. It is suggested to split the `[CAN|CHN] Dynamic MetalLB` subnet into two subnets, `[CAN|CHN] Dynamic MetalLB` and `[CAN|CHN] Dynamic MetalLB K3s`, the latter being used for K3s services. Subnet definitions are initially uploaded to SLS at installation time by CSI. If the `[CAN|CHN] Dynamic MetalLB` subnet is split after initial installation, steps must be taken to ensure that IPs in the newly created `[CAN|CHN] Dynamic MetalLB K3s` subnet are not in use and the `MetalLB Controller` pod in CSM must be restarted. Alternatively, the starting and ending IPs for K3s may be defined directly in `vars/uan_helm.yml`.  These steps are described below.

  Here is an example of splitting the existing `[CAN|CHN] Dynamic MetalLB` subnet. By default, the subnet with the `FullName` attribute of `[CAN|CHN] Dynamic MetalLB K3s` will be used for K3s, depending on whether `CAN` or `CHN` is being used for the customer access network.  This default `FullName` may be overridden by setting the `sls_can_metallb_fullname` variable in CFS to the expected name.
    
  **Important**: Before splitting `[CAN|CHN] Dynamic MetalLB`, be sure to verify none of the IP Addresses in the new `[CAN|CHN] Dynamic MetalLB K3s` subnet are being used. The `ims` and `user` namespaces are the most likely to contain these IPs. 

  ```bash
  kubectl get services -n ims
  kubectl get services -n user
  kubectl get services -A
  ```

  Edit SLS to make the following changes in the CAN or CHN network allocations:

  ```bash
  ### Existing [CAN|CHN] Dynamic MetalLB Subnet in SLS
  ### Split this as shown below into two subnets
          "CIDR": "x.x.x.192/26",
          "FullName": "CAN Dynamic MetalLB",
          "Gateway": "x.x.x.193",
          "MetalLBPoolName": "customer-access",
          "Name": "can_metallb_address_pool",
          "VlanID": 6,

  ### New [CAN|CHN] Dynamic MetalLB Subnet
          "CIDR": "x.x.x.192/27",
          "FullName": "CAN Dynamic MetalLB",
          "Gateway": "x.x.x.193",
          "MetalLBPoolName": "customer-access",
          "Name": "can_metallb_address_pool",
          "VlanID": 6,

  ### New [CAN|CHN] Dynamic MetalLB K3s
          "CIDR": "x.x.x.224/27",
          "FullName": "CAN Dynamic MetalLB K3s",
          "Gateway": "x.x.x.225",
          "MetalLBPoolName": "customer-access-k3s",
          "Name": "can_metallb_k3s_address_pool",
          "VlanID": 6,
  ```

  Reallocate the CSM MetalLB pool `customer-access` from CSM to reflect the SLS changes above. To shrink the `customer-access` pool in CSM, edit the configmap and pick the new CIDR block for the `[CAN|CHN] Dynamic MetalLB` subnet in SLS. In this example the CIDR block was `x.x.x.193/26` and is now `x.x.x.193/27`:

  ```bash
  # kubectl edit -n metallb-system cm/metallb
  ...
  data:
    config: |
      address-pools:
      - addresses:
        - x.x.x.193/27
        name: customer-access
        protocol: bgp
  ...
  ```

  To complete migrating the IP Address range out of CSM, restart the `MetalLB Controller` pod in CSM.

  ```bash
  kubectl delete pod -n metallb-system -l app.kubernetes.io/component=controller
  ```

  Here's an example of defining the MetalLB IP pool range directly in `vars/uan_helm.yml`.

  ```yaml
  metallb_ipaddresspool_range_start: "<start-of-range>"
  metallb_ipaddresspool_range_end: "<end-of-range>"
  ```

  By default, these arguments are commented out or omitted. MetalLB will be
  able to start, but the Custom Resource Definition for IPAddressPool and
  L2AdvertisementAddress will not be created and no Load Balancer IP address
  will be allocated.

  This pool will allow for external `LoadBalancer` IP address to be assigned to services like `HAProxy`. Initially, these IP addresses will serve as the SSH ingress for instances of `HAProxy`.


1. Configure and create the `/etc/subuid` and `/etc/subgid` files.

   To allow for users to run rootless Podman containers, these files must be present and configured with an entry for each user. These files must be uploaded to the `user` S3 bucket:

   ```bash
   $ cray artifacts list user --format json
   {
     "artifacts": [
       {
         "Key": "subuid",
         "LastModified": "2023-02-21T23:41:43.948000+00:00",
         "ETag": "\"c543aebb9b40bcf48879885734447090\"",
         "Size": 145686,
         "StorageClass": "STANDARD",
         "Owner": {
           "DisplayName": "User Service User",
           "ID": "USER"
        }
       },
       {
         "Key": "subgid",
         "LastModified": "2023-02-21T23:41:43.948000+00:00",
         "ETag": "\"73032ede132e44d2c1bc567246901737\"",
         "Size": 145686,
         "StorageClass": "STANDARD",
         "Owner": {
           "DisplayName": "User Service User",
           "ID": "USER"
         }
       }
     ]
   }

1. Place a Podman container image suitable for users within a container image registry accessible from the UAN.

## Configuring with Configuration Framework Service (CFS)

After completing the [Prerequisites](#prerequisites) section, the following are available to proceed with configuring a UAN to run K3s.

- A fully configured UAN
- An IPAddress start and end range to assign to MetalLB
- Prepared subuid and subgid files 

### Configuration Files and Playbook

Configuration for K3s and related services are controlled in the following ansible files in the UAN VCS repository:
```bash
$ ls uan-config-management/vars/ | egrep "k3s|sshd|helm"
uan_helm.yml
uan_k3s.yml
uan_sshd.yml
```
The ansible playbook to install and configure K3s may be found here:
```bash
$ ls uan-config-management | grep k3s
k3s.yml
```

### Ansible Roles

The following Ansible roles are provided in the `uan-config-management` repository in VCS. There are `README.md` files in each Ansible role directory in this repository that provide further details.

- **uan-k3s-install**: Download and stage K3s assets necessary to initialize and configure k3s on a node
- **uan-k3s-stage**: Install and configure K3s on a node
- **uan-helm**: Perform tasks to initialize an environment to install helm charts
- **uan-haproxy**: Deploy a list of HAProxy charts to the k3s cluster
- **uan-metallb**: Deploy the MetalLB chart to the k3s cluster
- **uan-sshd**: Create and enable instances of `sshd` with systemd
- **uan-podman**: Update /etc/

### Artifactory Assets

UAN uploads artifacts to deploy to the UAN control-plane node in a new nexus repository:

- uan-2.6.XX-third-party

The following Nexus group repository is created and references the previous UAN Nexus raw repos.

- uan-2.6-third-party

This repository will contain the installer for K3s, Helm charts for HAProxy and MetalLB, and so on.

### Validation Tests 

To validate the K3s cluster after it is deployed, see the [Validation Checks](#validation-checks) section of this document for details.

## Configuring K3s, MetalLB, HAProxy, and SSHD for use with Podman

Each of the following sections describes how the various components deployed to K3s and the UANs may be configured to enable users to SSH to rootless Podman containers. As there is no one configuration to fit any one use case, read and understand each section to modify the configuration as needed. After each section has been completed, see [Deploy K3s to the UAN](#deploy-k3s-to-the-uan).

### MetalLB 

By default, `metallb_ipaddresspool_range_start` and `metallb_ipaddresspool_end` will be defined from the `[CAN|CHN] Dynamic MetalLB K3s` subnet in SLS, if it exists. Alternatively, they may be configured directly in `vars/uan_helm.yml`:
```bash
$ grep "^metallb_ipaddresspool" vars/uan_helm.yml
metallb_ipaddresspool_range_start: "x.x.x.x"
metallb_ipaddresspool_range_end: "x.x.x.x"
```

MetalLB will assign an IP address to each service running in K3s that requires and external IP address. For HAProxy, each instance of HAProxy will require an IP address. Podman containers do *not* require their own IP address.

### HAProxy Configuration
Each SSH ingress is backed by a K3s deployment of HAProxy. By default, a single instance of HAProxy is enabled in `vars/uan_helm.yml`:
```yaml
uan_haproxy:
  - name: "haproxy-uai"
    namespace: "haproxy-uai"
    chart: "{{ haproxy_chart }}"
    chart_path: "{{ helm_install_path }}/charts/{{ haproxy_chart }}.tgz"
    args: "--set service.type=LoadBalancer"
```
This file must be further configured with additional values to populate the HAProxy configuration. For example, to load-balance SSH to three UANs, the following configuration changes must be made:
```yaml
uan_haproxy:
  - name: "haproxy-uai"
    namespace: "haproxy-uai"
    chart: "{{ haproxy_chart }}"
    chart_path: "{{ helm_install_path }}/charts/{{ haproxy_chart }}.tgz"
    args: "--set service.type=LoadBalancer"
    config: |
      global
        log stdout format raw local0
        maxconn 1024
      defaults
        log     global
        mode    tcp
        timeout connect 10s
        timeout client 36h
        timeout server 36h
        option  dontlognull
      listen ssh
        bind *:22
        balance leastconn
        mode tcp
        option tcp-check
        tcp-check expect rstring SSH-2.0-OpenSSH.*
        server uan01 uan01.example.domain.com:9000 check inter 10s fall 2 rise 1
        server uan02 uan02.example.domain.com:9000 check inter 10s fall 2 rise 1
        server uan03 uan03.example.domain.com:9000 check inter 10s fall 2 rise 1
```
This example that must be tailored to the wanted configuration. See the [SSHD Configuration](#sshd-configuration) section to create new instances of SSHD to respond to HAProxy connections outside of the standard SSHD running on port 22.

For more information on HAProxy configurations, see [HAProxy Configuration](<https://docs.haproxy.org/2.7/configuration.html>)

To enable additional instances of HAProxy representing alternate configurations, add an element to the list `uan_haproxy`.
### SSHD Configuration
The role `uan_sshd` runs in the playbook `k3s.yml` to start and configure new instances of SSHD to respond to HAProxy forwarded connections. Each new instance of SSHD is defined in `vars/uan_sshd.yml` as an element in the list `uan_sshd_configs`:
```yaml
uan_sshd_configs:
  - name: "uai"
    config_path: "/etc/ssh/uan"
    port: "9000"
```
This configuration will create a systemd unit file `/usr/lib/systemd/system/sshd_uai.service` and will mark the service as enabled. An SSH configuration file will also be created at `/etc/ssh/uan/sshd_uai_config` to start `sshd` listening on port 9000.

This default configuration will simply place users into their standard shell. To create a rootless Podman container upon logging in, specify an alternate configuration:
```yaml
  - name: "uai"
    config_path: "/etc/ssh/uan"
    port: "9000"
    config: |
      Match User *
        AcceptEnv DISPLAY
        X11Forwarding yes
        AllowTcpForwarding yes
        PermitTTY yes
        ForceCommand podman --root /scratch/containers/$USER run -it -h uai --cgroup-manager=cgroupfs --userns=keep-id --network=host -e DISPLAY=$DISPLAY registry.local/cray/uai:latest
```

**Note**: In the example above, the image `registry.local/cray/uai:latest` was provided as an example, but this example must be modified to reference an available container image.

### Deploy K3s to the UAN
After the VCS repository has been updated with the appropriate values, generate a new image and reboot the UAN. 

Alternatively, update the active CFS configuration on a single running UAN to include the `k3s.yml` playbook and uncomment out the following line from k3s.yml:
```yaml
  tasks:
    - name: Application node personalization play
      include_role:
        name: "{{ item }}"
      with_items:
        #- uan_k3s_stage # Uncomment to stage K3s assets without Image Customization
        - uan_k3s_install
```
This configuration will download the necessary assets without requiring an image rebuild.

After the node has been booted and configured, proceed with the [Validation Checks](#validation-checks) section to verify the components have been configured correctly.

# Validation Checks

## K3s Validation

To verify the `k3s.yml` playbook succeeded, perform the following verification checks.

1. Verify `kubectl` from the UAN.

   ```bash
   uan01:~ # export KUBECONFIG=~/.kube/k3s.yml
   uan01:~ # kubectl get nodes
   NAME    STATUS   ROLES                  AGE     VERSION
   uan01   Ready    control-plane,master   3h58m   v1.26.0+k3s1
   ```

1. Verify HAProxy and MetalLB are installed with `helm`

   ```bash
   uan01:~ # export KUBECONFIG=~/.kube/k3s.yml
   uan01:~ # helm ls -A
   NAME       	NAMESPACE     	REVISION	UPDATED                                	STATUS  	CHART         	APP VERSION
   haproxy-uai	haproxy-uai   	1       	2023-03-01 10:55:10.916137137 -0600 CST	deployed	haproxy-1.17.3	2.6.6
   metallb    	metallb-system	1       	2023-03-01 10:40:15.548380973 -0600 CST	deployed	metallb-0.13.7	v0.13.7
   ```

1. Check pod status of HAProxy and MetalLB

   ```bash
   uan01:~ # kubectl get pods -A | egrep "haproxy|metallb"
   metallb-system   metallb-controller-5b89f7554c-mzjvt       1/1     Running   0          4h1m
   metallb-system   metallb-speaker-ltnkx                     1/1     Running   0          4h1m
   haproxy-uai      haproxy-uai-7kg6p                         1/1     Running   0          3h46m
   ```

1. Verify MetalLB has assigned an external IP address to HAProxy:

   Examine the CPS cm-pm pod logs using the following command:

   ```bash
   uan01:~ # kubectl get services -A -l app.kubernetes.io/name=haproxy
   NAMESPACE     NAME          TYPE           CLUSTER-IP     EXTERNAL-IP      PORT(S)        AGE
   haproxy-uai   haproxy-uai   LoadBalancer   x.x.x.x        x.x.x.x          22:30886/TCP   3h47m
   ```

1. Verify that the new instance of SSHD is running:

   ```bash
   uan01:~ # systemctl status sshd_uai
   ● sshd_uai.service - OpenSSH Daemon Generated for uai
     Loaded: loaded (/usr/lib/systemd/system/sshd_uai.service; disabled; vendor preset: disabled)
     Active: active (running) since Wed 2023-03-01 12:43:31 CST; 2h 4min ago
   ```
1. Finally, use SSH to log in through the HAProxy load balancer:
   ```bash
   $ ssh x.x.x.x
   Trying to pull registry.local/cray/uai:1.0...
   Getting image source signatures
   Copying blob 07a88a2f44f8 done
   Copying blob 99a1d1c8ca98 done
   Copying blob a028e278fdc1 done
   Copying blob 5caad07f5e12 done
   Copying blob 157b0fca679c done
   Copying config de48e6a913 done
   Writing manifest to image destination
   Storing signatures
   sh-4.4$
   ```
