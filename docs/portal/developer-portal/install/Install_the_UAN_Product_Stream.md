# Install or Upgrade UAN

## Install and Upgrade Framework

The Install and Upgrade Framework (IUF) provides commands which install, upgrade, and deploy products on systems managed by CSM. IUF capabilities are described in detail in the [IUF section](https://cray-hpe.github.io/docs-csm/en-14/operations/iuf/iuf/) of the [Cray System Management Documentation](https://cray-hpe.github.io/docs-csm/en-14/). The initial install and upgrade workflows described in the [HPE Cray EX System Software Stack Installation and Upgrade Guide for CSM (S-8052)](https://www.hpe.com/support/ex-S-8052) detail when and how to use IUF with a new release of UAN or any other HPE Cray EX product.

This document **does not** replicate the install, upgrade, or deployment procedures detailed in the [IUF section](https://cray-hpe.github.io/docs-csm/en-14/operations/iuf/iuf/) of the [Cray System Management Documentation](https://cray-hpe.github.io/docs-csm/en-14/). This document provides details regarding software and configuration content specific to UAN which may be needed when installing, upgrading, or deploying a UAN release. The [IUF section](https://cray-hpe.github.io/docs-csm/en-14/operations/iuf/iuf/) of the [Cray System Management Documentation](https://cray-hpe.github.io/docs-csm/en-14/) will indicate when sections of this document must be seen for detailed information.

IUF will perform the following tasks for a release of the HPE Cray Supercomputing UAN product software.

- IUF `process-media` stage:
  - Inventory and extract the UAN products in the media directory for use in subsequent stages
- IUF `pre-install-check` stage:
  - Perform pre-install readiness checks
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

### IUF Resource Files

IUF uses the following files to drive the install or upgrade of UAN. These files are provided by the `hpc-csm-software-recipe` VCS repository.

- `product_vars.yaml` (**Required**)
  - Contains the list of products and versions to be installed together. It also contains the `working_branch` variables for the products. This file is in a directory under `/etc/cray/upgrade/csm/`. For example, `/etc/cray/upgrade/csm/admin`.
  - The path to this file is defined on the `iuf` command line using the IUF recipe vars (`-rv`) option.  For example, `-rv /etc/cray/upgrade/csm/admin`.
- `site_vars.yaml` (**Required**)
  - This file allows the administrator to override values in `product_vars.yaml` and defines the site VCS branching strategy. It may be placed in any directory under `/etc/cray/upgrade/csm`.
  - The path to this file is defined on the `iuf` command line using the IUF site vars (`-sv`) option. For example, `-sv /etc/cray/upgrade/csm/admin/site_vars.yaml`.
- `compute-and-uan-bootprep.yaml` (**Required**)
  - This file is typically installed in the `/etc/cray/upgrade/csm/bootprep` directory and defines variables for the following tasks:
    - Create a compute node image which will be configured for use on UAN
    - Create the UAN CFS Configuration
    - Create the UAN BOS session template
  - This path to this file is defined on the `iuf` command line using the IUF bootprep-config-managed (`-bc`) options.  For example, `-bc /etc/cray/upgrade/csm/bootprep/compute-and-uan-bootprep.yaml`.

## IUF Stage Details for UAN

This section describes any UAN details that an administrator must be aware of before executing IUF stages. Entries are prefixed with **Information** if no administrative action is required or **Action** if an administrator must perform tasks outside of IUF.

### process-media

**Action**: Before executing this stage, the administrator must ensure that the UAN product tar file is in a media directory under `/etc/cray/upgrade/csm/`. When more than one product is being installed, place all the product tar files in the same directory.

### update-vcs-config

**Action**: Before executing this stage, the administrator must ensure the IUF site variables file (see `iuf -sv SITE_VARS`) is updated to reflect site preferences, including the wanted VCS branching configuration. The `update-vcs-config` stage will use the branching configuration when modifying UAN branches in VCS.

### update-cfs-config

**Action**: Before executing this stage, any site-local UAN configuration changes must be made so that the following stages execute using the wanted UAN configuration values. See the [Basic UAN Configuration](../operations/Basic_UAN_Configuration.md) section of this documentation for UAN configuration content details. The [Prepare for UAN Product Installation](../installation_prereqs/Prepare_for_UAN_Product_Installation.md) section is required for fresh installation scenarios.

## UAN Content Installed

The following subsections describe most of the UAN content installed and configured on the system by IUF. The new version of UAN \(2.7.XX\) and its artifacts will be displayed in the CSM product catalog alongside any previously released version of UAN and its artifacts.


### Configuration

UAN provides configuration content in the form of Ansible roles and plays. This content is uploaded to a VCS repository in a branch with a specific UAN version number. That release number, such as \(2.7.XX\) distinguishes it from any previously released UAN configuration content. This content is described in detail in the [Basic UAN Configuration](../operations/Basic_UAN_Configuration.md) section.

For application nodes based on COS, the COS compute image is used as the base application node image and two COS CFS layers are required. The first COS CFS layer runs the `cos-application.yml` Ansible playbook and ensures that the COS content is applied as part of the image customization and node personalization processes. This COS CFS layer must precede the UAN CFS layer in the UAN CFS configuration. A second COS CFS layer running the Ansible playbook, `cos-application-after.yml`, runs after the UAN CFS layer of the UAN CFS configuration. This second COS CFS layer ensures that the application node initrd is rebuilt and that any customer-defined filesystems are configured.

Input files for `sat bootprep` are provided in the `hpc-csm-software-recipe` VCS repository and include COS components in the CFS configuration, node image, and BOS session template definitions. The `compute-and-uan-bootprep.yaml` input file is used for compute and application nodes.

### Procedure to Set Root Password For UAN/Application Nodes

The following instructions describe how to set the root password for UAN/Application nodes.

1. Obtain the HashiCorp Vault root token.

    ```bash
    ncn-m001# kubectl get secrets -n vault cray-vault-unseal-keys \
    -o jsonpath='{.data.vault-root}' | base64 -d; echo
    ```

1. Log into the HashiCorp Vault pod.

    ```bash
    ncn-m001# kubectl exec -itn vault cray-vault-0 -c vault -- sh
    ```

1. After you are attached to the pod's shell, log into vault and read the `secret/uan` key by executing the following commands. If the secret is empty, "No value found at secret/uan" will be displayed.

    ```bash
    pod# export VAULT_ADDR=http://cray-vault:8200
    pod# vault login
    pod# vault read secret/uan
    ```

1. If no value is found for this key, complete the following steps in another shell on the NCN management node.

    a.  Generate the password HASH for the root user. Replace 'PASSWORD' with a chosen root password.

      ```bash
      ncn-m001# openssl passwd -6 -salt $(< /dev/urandom tr -dc A-Z-a-z-0-9 | head -c4) PASSWORD
      ```

    b.  Take the HASH value returned from the previous command and enter the following in the vault pod's shell. Instead of HASH, use the value returned from the previous step.  You must escape the HASH value with the single quote to preserve any special characters that are part of the HASH value. If you previously have exited the pod, repeat the previous Steps 1-3; there is no need to perform the vault read since the content is empty.

      ```bash
      pod# vault write secret/uan root_password='HASH'
      ```

    c.  Verify that the new hash value is stored.

      ```bash
      pod# vault read secret/uan
      ...
      pod# exit
      ```

1. **Optional** Write any uan_ldap sensitive data, such as the `ldap_default_authtok` value, to the HashiCorp Vault.

    The vault login command will request a token. That token value is the output of the Step 1. The vault `read secret/uan_ldap` command verifies that the `uan_ldap` data was stored correctly. Any values stored here will be written to the UAN `/etc/sssd/sssd.conf` file in the `[domain]` section by CFS.

    This example shows storing a value for `ldap_default_authtok`.  If more than one variable must be stored, they must be written in space separated `key=value` pairs on the same `vault write secret/uan_ldap` command line.

    ```bash
    ncn-m001# kubectl exec -it -n vault cray-vault-0 -- sh
    export VAULT_ADDR=http://cray-vault:8200
    vault login
    vault write secret/uan_ldap ldap_default_authtok='TOKEN'
    vault read secret/uan_ldap
    ```

### SLE HPC Image for Application Nodes

The UAN product provides an Application Node image. This image is based on SUSE Linux Enterprise High Performance Computing 15 (SLE HPC 15) and uses a "stock" (that is, not customized for HPE Cray systems) kernel. Customers can use this image on Application nodes that do not require any COS compatibility as UAN does. Unlike the default UAN image, this Application Node image is not based on the COS image. However, like the UAN default image, it is uploaded to IMS as part of the installation process.

Customers must finish the installation or upgrade of the UAN product before booting an Application Node with SLE HPC 15 provided by that UAN product release. See [Booting an Application Node with a SLES Image (Technical Preview)](../advanced/SLES_Image.md) for more information about this image and instructions on deploying it to Application Nodes.

### RPMs

UAN provides RPMs used on UAN nodes. The RPMs are uploaded to Nexus as part of the installation process.

The following Nexus raw repositories are created:

- uan-2.7.XX-sle-15sp4
- uan-2.7.XX-sle-15sp3

The following Nexus group repositories are created and reference the preceding Nexus raw repos.

- uan-2.7-sle-15sp4
- uan-2.7-sle-15sp3

The uan-2.7-sle-15sp4 and uan-2.7-sle-15sp3 Nexus group repositories are used when building UAN node images and are accessible on UAN nodes after boot.
