# Prepare for UAN Product Installation

Perform this procedure to ready the HPE Cray Supercomputing EX system for HPE Cray Supercomputing UAN product installation.

Install and configure the HPE Cray Supercomputing COS product before performing this procedure.

If the HPE Cray Supercomputing EX system contains Compute Nodes (CNs) that will be repurposed as UANs, those CNs must be configured as CNs first. The _HPE Cray Supercomputing User Access Node (UAN) Administrator Guide (S-8033)_ provides instructions for reconfiguring a CN as UAN after product installation.

1. Verify that the management network switches are properly configured.

   See the [switch configuration procedures](https://cray-hpe.github.io/docs-csm/en-14/install/csm-install/readme/#5-configure-management-network-switches) in the HPE Cray System Management Documentation.

1. Ensure that the management network switches have the proper firmware.

    See the procedure "Update the Management Network Firmware" in the HPE Cray EX hardware documentation.

1. Ensure that the host reservations for the UAN CAN/CHN network have been properly set.

    See the procedure "Add UAN CAN IP Addresses to SLS" in the HPE Cray Supercomputing EX hardware documentation.

    1. For systems where UANs are going to host UAIs, identify a block of IP addresses for the services running in K3s. Please see [Configuring a UAN for K3s (Technical Preview)](../advanced/Enabling_K3s.md) for information on reserving a block of IP addresses on CAN/CHN for K3s MetalLB use.

       **Note**: The identification of IP addresses for the services running in K3s should be made at system installation time to avoid the possibility of IP collisions with CSM services.
   
1. [Configure the BMC for UANs with iLO](Configure_the_BMC_for_UANs_with_iLO.md)

1. [Configure the BIOS of an HPE UAN](Configure_the_BIOS_of_an_HPE_UAN.md)

1. Verify that the firmware for each UAN BMC meets the specifications.

   Use the System Admin Toolkit firmware command to check the current firmware version on a UAN node.

   ```bash
   ncn-m001# sat firmware -x BMC_XNAME
   ```

1. Ensure that the `cray-console-node` pods are connected to UANs so that they are monitored and their consoles are logged.

    1. Obtain a list of the xnames for all UANs (remove the `--subrole` argument to list all Application nodes).

       ```bash
       ncn# cray hsm state components list \
       --role Application --subrole UAN \
       --format json \
       | jq -r .Components[].ID | sort
       x3000c0s19b0n0
       x3000c0s24b0n0
       x3000c0s31b0n0
       ```

    1. Obtain a list of the console pods.

       ```bash
       ncn# PODS=$(kubectl get pods -n services \
       -l app.kubernetes.io/name=cray-console-node \
       --template '{{range .items}}{{.metadata.name}} {{end}}')
       ```

    1. Use `conman -q` to scan the list of connections conman is monitoring (only UAN xnames are shown for brevity).

       ```bash
       ncn# for pod in $PODS; do \
       kubectl exec -n services \
       -c cray-console-node $pod \
       -- conman -q; done
       x3000c0s19b0n0
       x3000c0s24b0n0
       x3000c0s31b0n0
       ```

       If a console connection is not present, the install may continue, but a console connection should be established before attempting to boot the UAN.

Next, install the UAN product by performing the procedure [Install the UAN Product Stream](../install/Install_the_UAN_Product_Stream.md).
