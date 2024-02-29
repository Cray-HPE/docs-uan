
# Create UAN Boot Images

Beginning with UAN 2.6, the procedures described here are automatically performed by IUF during installation and upgrade of the HPE Cray Supercomputing UAN product. See [Install or Upgrade UAN](../install/Install_the_UAN_Product_Stream.md) for details. The procedures shown here are for cases when a new image is needed after the UAN product is installed or upgraded and the product release is prior to 2.6. For release 2.6 and newer, perform [Build a New UAN Image Using a COS Recipe](Build_a_New_UAN_Image_Using_the_COS_Recipe.md) for these cases.

## Overview

This procedure updates the configuration management git repository to match the installed version of the HPE Cray Supercomputing UAN product. That updated configuration is then used to create UAN boot images and a BOS session template.

UAN specific configuration, and other required configurations related to UANs are covered in this topic. See product-specific documentation for further information on configuring other HPE products (for example, workload managers and the HPE Cray Programming Environment\) that may be configured on the UANs.

The workflow for manually creating images to boot UANs is:

1. [Prepare CFS Configuration](#prepare-cfs-configuration):
   - Clone the UAN configuration git repository and create a branch based on the branch imported by the UAN installation.
   - Update the configuration content and push the changes to the newly created branch.
1. [Create SAT Bootprep File](#create-sat-bootprep-file): Enter the information that `sat bootprep` will use to automatically create CFS configurations, IMS images, and BOS session templates for UANs.
1. [Run `sat bootprep`](#run-sat-bootprep) to generate all the artifacts a BOS session requires to boot UANs.
1. [Boot UANs](Boot_UANs.md) to boot the UANs with the new image and BOS session template.

Replace `PRODUCT_VERSION` and `CRAY_EX_HOSTNAME` in the example commands in this procedure with the current UAN product version installed \(See Step 1\) and the hostname of the HPE Cray Supercomputing EX system, respectively.

## Prepare CFS Configuration

1. Obtain the artifact IDs and other information from the `cray-product-catalog` Kubernetes ConfigMap. Record the following information:
   - the `clone_url`
   - the `import_branch` value

   Upon successful installation of the UAN product, the UAN configuration is cataloged in this ConfigMap. This information is required for this procedure.

    `PRODUCT_VERSION` will be replaced by a numbered version string, such as `2.1.7` or `2.3.0`.

    ```bash
    ncn-m001# kubectl get cm -n services cray-product-catalog -o json | jq -r .data.uan
    PRODUCT_VERSION:
      configuration:
        clone_url: https://vcs.CRAY_EX_HOSTNAME/vcs/cray/uan-config-management.git 
        commit: 6658ea9e75f5f0f73f78941202664e9631a63726                   
        import_branch: cray/uan/PRODUCT_VERSION                           
        import_date: 2021-02-02 19:14:18.399670
        ssh_url: git@vcs.CRAY_EX_HOSTNAME:cray/uan-config-management.git                      
    ```

1. Obtain the password for the `crayvcs` user from the Kubernetes secret for use in the next command.

    ```bash
    ncn-m001# VCS_USER=$(kubectl get secret -n services vcs-user-credentials --template={{.data.vcs_username}} | base64 --decode)
              VCS_PASS=$(kubectl get secret -n services vcs-user-credentials --template={{.data.vcs_password}} | base64 --decode)
    ```

1. Clone the UAN configuration management repository. Replace CRAY\_EX\_HOSTNAME in the clone url with **api-gw-service-nmn.local** when cloning the repository.

    The repository is in the VCS/Gitea service and the location is reported in the cray-product-catalog Kubernetes ConfigMap in the `configuration.clone_url` key. The CRAY\_EX\_HOSTNAME from the `clone_url` is replaced with `api-gw-service-nmn.local` in the command that clones the repository.

    ```bash
    ncn-m001# git clone https://$VCS_USER:$VCS_PASS@api-gw-service-nmn.local/vcs/cray/uan-config-management.git
    . . .
    ncn-m001# cd uan-config-management && git checkout cray/uan/PRODUCT_VERSION && git pull
    Branch 'cray/uan/PRODUCT_VERSION' set up to track remote branch 'cray/uan/PRODUCT_VERSION' from 'origin'.
    Already up to date.
    ```

1. Create a branch using the imported branch from the installation to customize the UAN image.

    This branch name will be reported in the `cray-product-catalog` Kubernetes ConfigMap in the `configuration.import_branch` key under the UAN section. The format is cray/uan/PRODUCT\_VERSION. In this guide, an `integration-PRODUCT_VERSION` branch is used for examples to comply with IUF defaults, but the name can be any valid git branch name configured to be used by IUF.

    Modifying the cray/uan/PRODUCT\_VERSION branch that the UAN product installation created is not allowed by default.

    ```bash
    ncn-m001# git checkout -b integration-PRODUCT_VERSION && git merge cray/uan/PRODUCT_VERSION
    Switched to a new branch 'integration-PRODUCT_VERSION'
    Already up to date.
    ```

1. Apply any site-specific customizations and modifications to the Ansible configuration for the UAN nodes and commit the changes.

    The default Ansible play to configure UAN nodes is `site.yml` in the base of the `uan-config-management` repository. The roles that are executed in this play allow for custom configuration as required for the system.

    Consult the individual Ansible role `README.md` files in the uan-config-management repository roles directory to configure individual role variables. Roles prefixed with `uan_` are specific to UAN configuration and include network interfaces, disk, LDAP, software packages, and message of the day roles.

    ***NOTE:*** Admins ***must*** ensure the `uan_can_setup` variable is set to the correct value for the site. This variable controls how the nodes are configured for user access. When `uan_can_setup` is `yes`, user access is over the `CAN` or `CHN`, based on the BICAN System Default Route setting in SLS. When `uan_can_setup` is `no`, the Admin must configure the user access interface and default route. See [Configure Interfaces on UANs](Configure_Interfaces_on_UANs.md)

    **Warning:** Never place sensitive information such as passwords in the git repository.

    The following example shows how to add a `vars.yml` file containing site-specific configuration values to the `Application_UAN` group variable location.

    These and other Ansible files do not necessarily need to be modified for UAN image creation. See [Basic UAN Configuration](Basic_UAN_Configuration.md) for instructions for site-specific UAN configuration, including CAN/CHN configuration.

    ```bash
    ncn-m001# vim group_vars/Application_UAN/vars.yml
    ncn-m001# git add group_vars/Application_UAN/vars.yml
    ncn-m001# git commit -m "Add vars.yml customizations"
    [integration-PRODUCT_VERSION ecece54] Add vars.yml customizations
     1 file changed, 1 insertion(+)
     create mode 100644 group_vars/Application_UAN/vars.yml
    ```

1. Push the changes to the repository using the proper credentials, including the password obtained previously.

    ```bash
    ncn-m001# git push --set-upstream origin integration-PRODUCT_VERSION
    Username for 'https://api-gw-service-nmn.local': crayvcs
    Password for 'https://crayvcs@api-gw-service-nmn.local':
    . . .
    remote: Processed 1 references in total
    To https://api-gw-service-nmn.local/vcs/cray/uan-config-management.git
     * [new branch]      integration-PRODUCT_VERSION -> integration-PRODUCT_VERSION
     Branch 'integration-PRODUCT_VERSION' set up to track remote branch 'integration-PRODUCT_VERSION' from 'origin'.
    ```

    The configuration parameters have been stored in a branch in the UAN git repository. The next phase of the process uses `sat bootprep` to handle creating the CFS configurations, IMS images, and BOS session templates for UANs.

## UAN SAT Bootprep Input File Contents

With Shasta Admin Toolkit (SAT) version `2.2.16` and later, HPE recommends that administrators create an input file for use with `sat bootprep`.

A `sat bootprep` input file will have three sections:

- `configurations`: specifies each layer to be included in the CFS configuration for the UAN images for image customization and node personalization.
- `images`: specifies the IMS images to create for UAN nodes.
- `session_templates`: creates BOS session templates. This section references the named IMS image that `sat bootprep` generates, as well as a CFS configuration.

These sections create CFS configurations, IMS images, and BOS session templates respectively. Each section may have multiple elements to create more than one CFS, IMS, or BOS artifact. The format is similar to the input files for CFS, IMS, and BOS, but SAT will automate the process with fewer steps. Follow the subsections below to create a UAN bootprep input file.

See also [*HPE Cray EX System Software Stack Installation and Upgrade Guide for CSM (S-8052)*](https://www.hpe.com/support/ex-S-8052) for further information on configuring other HPE products, as this procedure documents only the required configuration of the UAN.

## Create SAT Bootprep File

1. Verify that installed version of SAT is `2.2.16` or later.

   ```bash
   ncn-m001# sat showrev --products --filter 'product_name="sat"'
   ```

1. Obtain the version of each product that will be included in a CFS configuration layer.

   ```bash
   ncn-m001# sat showrev --products --filter 'product_name="PRODUCT_NAME"'
   ```
  
  The example `sat bootprep` input file in this procedure includes the following products:
    - `slingshot-host-software`
    - `cos`
    - `csm`
    - `uan`

  Your site may require additional products in the input file.

1. Record or save the list of COS image recipes returned in the previous step.

   You will select one of these recipes as the base for the UAN image in a later step.

1. Create a `sat bootprep` input file.

   ```bash
   ncn-m001# touch uan-bootprep.yaml
   ```

1. Open the empty `sat bootprep` input file in an editor.

1. Add the CFS configuration content.

   The Slingshot Host Software CFS layer must be listed first. This layer is required as the UAN layer will attempt to install DVS and Lustre packages that require SHS be installed first. The correct playbook for Cassini or Mellanox must also be specified. Consult the Slingshot Host Software documentation for more information.

   Beginning with UAN version `2.6.0`, CFS configuration roles which are provided by COS are now defined as two separate COS configuration layers as shown in the following example. Prior to UAN version `2.6.0`, these roles were included in the UAN configuration layer. Separating these roles into COS layers allows COS updates to be independent from UAN updates.

   The following example creates a CFS configuration named `uan-config`:

   Example:

   ```yaml
   configurations:
   - name: uan-config
     layers:
     - name: shs-mellanox_install-integration
       playbook: shs_mellanox_install.yml
       product:
        name: slingshot-host-software
         version: 2.0.0
         branch: integration
   #  - name: shs-cassini_install-integration
   #    playbook: shs_cassini_install.yml
   #    product:
   #      name: slingshot-host-software
   #      version: 2.0.0
   #      branch: integration
     - name: cos-application-integration
       playbook: cos-application.yml
       product:
         name: cos
         version: 2.5
     - name: csm-packages-integration
       playbook: csm_packages.yml
       product:
         name: csm
         version: 1.4
     - name: uan-set-nologin
       playbook: set_nologin.yml
       product:
         name: uan
         version: 2.7.0
         branch: integration-PRODUCT_VERSION
     - name: uan
       playbook: site.yml
       product:
         name: uan
         version: 2.7.0
         branch: integration-PRODUCT_VERSION
  
     ... add configuration layers for other products here, if desired ...

     - name: uan-rebuild-initrd
       playbook: rebuild-initrd.yml
       product:
         name: uan
         version: 2.7.0
         branch: integration-PRODUCT_VERSION
     - name: uan-unset-nologin
       playbook: unset_nologin.yml
       product:
         name: uan
         version: 2.7.0
         branch: integration-PRODUCT_VERSION
   ```

1. Add the content for the UAN image, using an appropriate name to correctly identify the UAN image being built.

   UAN images are built using the COS recipe, so this step specifies which image recipe to use based on what is provided by COS. The `ims` section references the `uan-config` CFS configuration so that CFS image customization will use that configuration along with the specified node groups.

   The following example will create an IMS image with the name `cray-shasta-uan-sles15sp3.x86_64-2.3.25`. 

   ```yaml
   images:
   - name: cray-shasta-uan-sles15sp3.x86_64-2.3.25
     ims:
       is_recipe: true
       name: cray-shasta-compute-sles15sp3.x86_64-2.3.25
     configuration: uan-config
     configuration_group_names:
     - Application
     - Application_UAN
   ```

1. Add the content for the BOS session templates.

 You may need to change the `boot_sets` key `uan` in the following example. If there are more than one `boot_sets` in the session template, each key must be unique.

```yaml
session_templates:
- name: uan-2.4.0
  image: cray-shasta-uan-sles15sp3.x86_64-2.3.25
  configuration: uan-config
  bos_parameters:
    boot_sets:
      uan:
        kernel_parameters: spire_join_token=${SPIRE_JOIN_TOKEN}
        node_roles_groups:
        - Application_UAN
```

1. Save changes to the `sat bootprep` input YAML file and exit the editor.

## Run `sat bootprep`

1. Execute the `sat bootprep` command to generate the configurations and artifacts needed to boot UANs.

   This command may take some time as it will initiate IMS image creation and CFS image customization.

   ```bash
   ncn-m001# sat bootprep run uan-bootprep.yaml
   ```

   Modify the CFS layers or input file if necessary to successfully complete `sat bootprep`.

   If any artifacts are going to be overwritten, SAT will prompt for confirmation before overwriting them. This is useful when making CFS changes as SAT will automatically configure the layers to use the latest git commits if the branches are specified correctly.

1. Save the input file to a known location after `sat bootprep` completes successfully.

   You can use this input file to regenerate artifacts as changes are made or different product layers are added.
