# Install or Upgrading UAN

## Install and Upgrade Framework (IUF) Overview

The Install and Upgrade Framework (IUF) provides commands which install, upgrade and deploy products on systems managed by CSM. IUF capabilities are described in detail in the [Cray System Management Documentation](https://github.com/Cray-HPE/docs-csm/blob/release/1.3/README.md). The initial install and upgrade workflows described in the [HPE Cray EX System Software Getting Started Guide S-8000](https://www.hpe.com/support/ex-S-8000) detail when and how to use IUF with a new release of UAN or any other HPE Cray EX product.

This document **does not** replicate install, upgrade or deployment procedures detailed in the [Cray System Management Documentation](https://github.com/Cray-HPE/docs-csm/blob/release/1.3/README.md). This document provides details regarding software and configuration content specific to UAN which may be needed when installing, upgrading or deploying a UAN release. The [Cray System Management Documentation](https://github.com/Cray-HPE/docs-csm/blob/release/1.3/README.md) will indicate when sections of this document should be referred to for detailed information.

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

IUF uses a variety of CSM and SAT tools when performing these tasks. The IUF section of the [Cray System Management Documentation](https://github.com/Cray-HPE/docs-csm/blob/release/1.3/README.md) describes how to use these tools directly if it is desirable to use them instead of IUF.

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
