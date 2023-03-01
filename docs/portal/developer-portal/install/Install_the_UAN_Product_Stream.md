# Install or Upgrade UAN

## Install and Upgrade Framework

The Install and Upgrade Framework (IUF) provides commands which install, upgrade and deploy products on systems managed by CSM. IUF capabilities are described in detail in the [IUF section](https://cray-hpe.github.io/docs-csm/en-14/operations/iuf/iuf/) of the [Cray System Management Documentation](https://cray-hpe.github.io/docs-csm/en-14/). The initial install and upgrade workflows described in the [HPE Cray EX System Software Stack Installation and Upgrade Guide for CSM (S-8052)](https://www.hpe.com/support/ex-S-8052) detail when and how to use IUF with a new release of UAN or any other HPE Cray EX product.

This document **does not** replicate install, upgrade or deployment procedures detailed in the [IUF section](https://cray-hpe.github.io/docs-csm/en-14/operations/iuf/iuf/) of the [Cray System Management Documentation](https://cray-hpe.github.io/docs-csm/en-14/). This document provides details regarding software and configuration content specific to UAN which may be needed when installing, upgrading or deploying a UAN release. The [IUF section](https://cray-hpe.github.io/docs-csm/en-14/operations/iuf/iuf/) of the [Cray System Management Documentation](https://cray-hpe.github.io/docs-csm/en-14/) will indicate when sections of this document should be referred to for detailed information.

IUF will perform the following tasks for a release of UAN.

- IUF `deliver-product` stage:
  - Uploads UAN configuration content to VCS
  - Uploads UAN information to the CSM product catalog
  - Uploads UAN content to Nexus repositories
  - Uploads the UAN Stock Kernel image to IMS
- IUF `update-vcs-config` stage:
  - Updates the VCS integration branch with new UAN configuration content
- IUF `update-cfs-config` stage:
  - Creates new CFS configurations with new UAN configuration content
- IUF `prepare-images` stage:
  - Creates updated UAN images based on COS with new UAN content
- IUF `managed-nodes-rollout` stage:
  - Boots UAN nodes with an image containing new UAN content

IUF uses a variety of CSM and SAT tools when performing these tasks. The [IUF section](https://cray-hpe.github.io/docs-csm/en-14/operations/iuf/iuf/) of the [Cray System Management Documentation](https://cray-hpe.github.io/docs-csm/en-14/) describes how to use these tools directly if it is desirable to use them instead of IUF.

## IUF Stage Details for UAN

This section describes any UAN details that an administrator may need to be aware of before executing IUF stages. Entries are prefixed with **Information** if no administrative action is required or **Action** if an administrator may need to perform tasks outside of IUF.

### update-vcs-config

**Action**: Before executing this stage, the administrator should ensure the IUF site variables file (see `iuf -sv SITE_VARS`) is updated to reflect site preferences, including the desired VCS branching configuration. The branching configuration will be used by the `update-vcs-config` stage when modifying COS branches in VCS.

### update-cfs-config

**Action**: Before executing this stage, any site-local UAN configuration changes should be made so the following stages execute using the desired UAN configuration values. See the [About UAN Configuration](../operations/About_UAN_Configuration.md) section of this documentation for UAN configuration content details. Note that the [Prepare for UAN Product Installation](../installation_prereqs/Prepare_for_UAN_Product_Installation.md) section is required for fresh install scenarios.

## UAN Content Installed

The following subsections describe the majority of the UAN content installed and configured on the system by IUF. The new version of UAN \(2.6.XX\) and its artifacts will be displayed in the CSM product catalog alongside any previously released version of UAN and its artifacts.


### Configuration

UAN provides configuration content in the form of Ansible roles and plays. This content is uploaded to a VCS repository in a branch with a specific UAN version number \(2.6.XX\) to distinguish it from any previously released UAN configuration content. This content is described in detail in the [About UAN Configuration](../operations/About_UAN_Configuration.md) section.

For application nodes based on COS, the COS compute image is used as the base application node image and two COS CFS layers are required. The `cos-application.yml` Ansible playbook ensures that the COS content is applied as part of the image customization and node personalization processes. A second Ansible playbook, `cos-application-after.yml`, runs at the end to ensure that the application node initrd is rebuilt.

Input files for `sat bootprep` are provided in the `hpc-csm-software-recipe` VCS repository and include COS components in the CFS configuration, node image, and BOS session template definitions. The `compute-and-uan-bootprep.yaml` input file is used for compute and application nodes.

### Procedure to Set Root Password For UAN/Application Nodes

The following instructions describe how to set the root password for UAN/Application nodes.

1.  Obtain the HashiCorp Vault root token.

    ```bash
    ncn-m001# kubectl get secrets -n vault cray-vault-unseal-keys \
    -o jsonpath='{.data.vault-root}' | base64 -d; echo
    ```

1.  Log into the HashiCorp Vault pod.

    ```bash
    ncn-m001# kubectl exec -itn vault cray-vault-0 -c vault -- sh
    ```

1.  Once attached to the pod's shell, log into vault and read the `secret/cos` key by executing the following commands. If the secret is empty, "No value found at secret/cos" will be displayed.

    ```bash
    pod# export VAULT_ADDR=http://cray-vault:8200
    pod# vault login
    pod# vault read secret/uan
    ```

1.  If no value is found for this key, complete the following steps in another shell on the NCN management node.

    a.  Generate the password HASH for the root user. Replace 'PASSWORD' with a chosen root password.

        ```bash
        ncn-m001# openssl passwd -6 -salt $(< /dev/urandom tr -dc A-Z-a-z-0-9 | head -c4) PASSWORD
        ```

    b.  Take the HASH value returned from the previous command and enter the following in the vault pod's shell. Instead of HASH, use the value returned from the previous step.  You must escape the HASH value with the single quote to preserve any special characters that are part of the HASH value. If you previously have exited the pod, repeat steps 1-3 above; there is no need to perform the vault read since the content is empty.

        ```bash
        pod# vault write secret/uan root_password='HASH'
        ```

    c.  Verify the new hash value is stored.

        ```bash
        pod# vault read secret/uan
        ...
        pod# exit
        ```
### UAN Stock Kernel Image

UAN provides a stock kernel Application Node image which may be used on Application nodes that do not require any COS compatibility as UAN does. This image is not based on the COS image which the default UAN image is and is uploaded to IMS as part of the installation process. The stock kernel Application Node image is based on SLES 15 SP4.

### RPMs

UAN provides RPMs used on UAN nodes. The RPMs are uploaded to Nexus as part of the installation process.

The following Nexus raw repositories are created:

- uan-2.6.XX-sle-15sp4
- uan-2.6.XX-sle-15sp3

The following Nexus group repositories are created and reference the aforementioned COS Nexus raw repos.

- uan-2.6-sle-15sp4
- uan-2.6-sle-15sp3

The uan-2.6-sle-15sp4 and uan-2.6-sle-15sp3 Nexus group repositories are used when building UAN node images and are accessible on UAN nodes after boot.
