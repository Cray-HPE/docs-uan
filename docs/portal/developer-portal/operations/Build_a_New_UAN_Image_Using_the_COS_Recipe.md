
# Build a New UAN Image Using a COS Recipe

Prior to HPE Cray Supercomputing UAN release 2.3, a similar copy of the COS image recipe was imported with the UAN install. Beginning with the 2.3 release, this product does not install an image recipe. A COS image recipe must be used. Additional UAN packages will be installed by CFS and the `uan_packages` role. In UAN release 2.6, this procedure is automated as part of the IUF process of installing and upgrading the UAN product. See [Install or Upgrade UAN](../install/Install_the_UAN_Product_Stream.md) for details.

The following procedures are provided for cases where a new UAN image must be built after initial installation. This document describes two methods of building UAN images:

- [Using IUF to Build a New UAN Image (UAN 2.6+)](#using-iuf-to-build-a-new-uan-image-uan-26): use this procedure if you are using the IUF automation and the UAN software release version is 2.6 or later.
- [Manually Build a New UAN Image from a COS Recipe (UAN 2.3+)](#manually-build-a-new-uan-image-from-a-cos-recipe-uan-23): use this procedure if you are not using the IUF automation or the UAN software release is earlier than 2.6 and later than 2.3.

## Using IUF to Build a New UAN Image (UAN 2.6+)

The procedure for using IUF to build and prepare images is documented in the [Image Preparation](https://cray-hpe.github.io/docs-csm/en-15/operations/iuf/workflows/image_preparation/) section of the CSM documentation. After IUF runs, the UAN CFS configuration will be created, the UAN image will be configured using that configuration, and the UAN BOS session template will be created using the new configuration and image.

The following information is provided for reference.

Two IUF stages are run to create a new UAN image:

1. `update-cfs-config`: Creates a new CFS configuration defined by the information in the bootprep file.
1. `prepare-images`: Applies the new CFS configuration to the image defined in the bootprep file.

After IUF runs these two stages, the UAN CFS configuration will be created, the UAN image will be configured using that configuration, and a UAN BOS session template will be created using the new configuration and image.

Before using IUF to build a new UAN image from a COS recipe, be sure that the information in the IUF Recipe Variables file (`product_vars.yaml`) and bootprep file (`compute-and-uan-bootprep.yaml`) are correct for the wanted UAN CFS configuration and the COS image recipe.

- Example `product_vars.yaml` showing COS and UAN versions and working VCS branches:

  ```bash
  cos:
    version: 2.5.120 # Provides the COS image to use as a base UAN image
    working_branch: "{{ working_branch }}" # COS CFS branch to use (typically matches compute nodes)

  uan:
    version: 2.6.0 # Provides the UAN CFS configuration
    working_branch: "{{ working_branch }}" # Provides the UAN CFS branch to use
  ```

- Example `compute-and-uan-bootprep.yaml` showing UAN CFS configuration and images (COS and UAN):

  ```bash
  configurations:
  - name: "{{default.note}}uan-{{recipe.version}}{{default.suffix}}"
    layers:
    - name: shs-{{default.network_type}}_install-{{slingshot_host_software.working_branch}}
      playbook: shs_{{default.network_type}}_install.yml
      product:
        name: slingshot-host-software
        version: "{{slingshot_host_software.version}}"
        branch: "{{slingshot_host_software.working_branch}}"
    - name: cos-application-{{cos.working_branch}}
      playbook: cos-application.yml
      product:
        name: cos
        version: "{{cos.version}}"
        branch: "{{cos.working_branch}}"
    - name: csm-packages-{{csm.version}}
      playbook: csm_packages.yml
      product:
        name: csm
        version: "{{csm.version}}"
    - name: uan-{{uan.working_branch}}
      playbook: site.yml
      product:
        name: uan
        version: "{{uan.version}}"
        branch: "{{uan.working_branch}}"
    - name: csm-diags-application-{{csm_diags.version}}
      playbook: csm-diags-application.yml
      product:
        name: csm-diags
        version: "{{csm_diags.version}}"
    - name: sma-ldms-application-{{sma.version}}
      playbook: sma-ldms-application.yml
      product:
        name: sma
        version: "{{sma.version}}"
    - name: cpe-pe_deploy-{{cpe.working_branch}}
      playbook: pe_deploy.yml
      product:
        name: cpe
        version: "{{cpe.version}}"
        branch: "{{cpe.working_branch}}"
    - name: analytics-site-{{analytics.working_branch}}
      playbook: site.yml
      product:
        name: analytics
        version: "{{analytics.version}}"
        branch: "{{analytics.working_branch}}"
    - name: slurm-site-{{slurm.working_branch}}
      playbook: site.yml
      product:
        name: slurm
        version: "{{slurm.version}}"
        branch: "{{slurm.working_branch}}"
    - name: cos-application-last-{{cos.working_branch}}
      playbook: cos-application-after.yml
      product:
        name: cos
        version: "{{cos.version}}"
        branch: "{{cos.working_branch}}"

  images:
  # images that use base.name will inherit the note and suffix in their name
  - name: "{{default.note}}{{base.name}}{{default.suffix}}"
    ref_name: base_cos_image
    base:
      product:
        name: cos
        type: recipe
        version: "{{cos.version}}"
  
  - name: "compute-{{base.name}}"
    ref_name: compute_image
    base:
      image_ref: base_cos_image
    configuration: "{{default.note}}compute-{{recipe.version}}{{default.suffix}}"
    configuration_group_names:
    - Compute
  
  - name: "uan-{{base.name}}"
    ref_name: uan_image
    base:
      image_ref: base_cos_image
    configuration: "{{default.note}}uan-{{recipe.version}}{{default.suffix}}"
    configuration_group_names:
    - Application
    - Application_UAN
  ```

After the `product_vars.yaml` and `compute-and-uan-bootprep.yaml` files are updated to reflect the wanted COS and UAN versions and VCS branches to use, IUF may be executed.

## Manually Build a New UAN Image from a COS Recipe (UAN 2.3+)

Perform the following before starting this procedure:

- Install the COS, Slingshot, and UAN product streams.
- Initialize the cray administrative CLI.

In the COS recipe for 2.2, several dependencies have been removed, including Slingshot, DVS, and Lustre. Those packages are now installed during CFS Image Customization. More information on this change is covered in the [Create UAN Boot Images](Create_UAN_Boot_Images.md) procedure.

1. Identify the COS image recipe to base the UAN image on. Select the recipe that matches the version of COS that the compute nodes will be using.

   ```bash
   ncn-m001# cray ims recipes list --format json | jq '.[] | select(.name | contains("compute"))'
   {
     "created": "2021-02-17T15:19:48.549383+00:00",
     "id": "4a5d1178-80ad-4151-af1b-bbe1480958d1",  <<-- Note this ID
     "link": {
       "etag": "3c3b292364f7739da966c9cdae096964",
       "path": "s3://ims/recipes/4a5d1178-80ad-4151-af1b-bbe1480958d1/recipe.tar.gz",
       "type": "s3"
     },
     "linux_distribution": "sles15",
     "name": "cray-shasta-compute-sles15sp3.x86_64-2.2.27",
     "recipe_type": "kiwi-ng"
   }
   ```

2. Save the id of the IMS recipe in an environment variable.

   ```bash
   ncn-m001# IMS_RECIPE_ID=4a5d1178-80ad-4151-af1b-bbe1480958d1
   ```

3. Use the IMS recipe id to build the UAN image:

   More detail on this IMS procedure may be found in the procedure "Build an Image Using IMS REST Service" in the CSM documentation.

   ```bash
   ncn-m001# IMS_PUBLIC_KEY=$(cray ims public-keys list --format json | jq -r ".[] | .id" | head -1)
   ncn-m001# IMS_ARCHIVE_NAME=$(cray ims recipes describe $IMS_RECIPE_ID --format json | jq -r .name)
   ncn-m001# IMS_ARCHIVE_NAME=${IMS_ARCHIVE_NAME/compute/uan}
   ncn-m001# cray ims jobs create --job-type create --public-key-id $IMS_PUBLIC_KEY --image-root-archive-name $IMS_ARCHIVE_NAME --artifact-id $IMS_RECIPE_ID
   ```

4. Perform [Create UAN Boot Images](Create_UAN_Boot_Images.md#) to run CFS Image Customization on the resulting image.
