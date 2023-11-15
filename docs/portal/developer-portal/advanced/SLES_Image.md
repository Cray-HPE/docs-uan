# Booting an Application Node with a SLE HPC Image (Technical Preview)

A SLE HPC image is available for use with Application Node types such as gateways and LNet routers. This image is considered a "Technical Preview" as the initial support for booting with SLE HPC Images without COS. This Application Node image differs from the standard COS-based image because this image does not include the COS kernel and libraries that Compute Nodes (CNs) have.

The image is built from the same pipeline as Non-Compute Node (NCN) Images. Similarities may be noticed including the kernel and package versions.

This procedure documents how to boot and configure this image.

## Limitations

As this feature is a "Technical Preview" of supporting SLE HPC Images on Application Nodes, there are several limitations:

* CFS Configurations that operate on COS and NCN images are not yet supported.
* CFS Node Personalization must be started manually.

## Procedure Overview

The following steps outline the process of configuring and booting an Application Node with the SLE HPC Image.

  1. Determine the image to use.

  1. Customize the image with SAT and generate a BOS Session Template

  1. Update BOS Session Template with the necessary parameters.

  1. Reboot the node.

## Procedure

Perform the following steps to configure and boot a SLE HPC image on an Application type node.

1. Log in to the master node `ncn-m001`. All commands in this procedure are run from the master node.

1. Verify that the UAN release contains a SLES image.

```bash
ncn-m001# UAN_RELEASE=@product_version@
ncn-m001# sat showrev --no-headings --filter "product_version = $UAN_RELEASE" --filter "product_name = uan"
```

1. Select an Image to boot or customize.

```bash
ncn-m001# APP_IMAGE_NAME=cray-application-sles15sp5.x86_64-5.2.42

ncn-m001# APP_IMAGE_ID=$(cray ims images list --format json  | jq --arg APP_IMAGE_NAME "$APP_IMAGE_NAME" -r 'sort_by(.created) | .[] | select(.name == $APP_IMAGE_NAME ) | .id' | head -1)

ncn-m001# cray ims images describe $APP_IMAGE_ID --format json
{
  "arch": "x86_64",
  "created": "2023-11-06T15:47:10.564555+00:00",
  "id": "51b19502-a13b-42ab-a653-b1ee7e6a7fb5",
  "link": {
    "etag": "",
    "path": "s3://boot-images/51b19502-a13b-42ab-a653-b1ee7e6a7fb5/manifest.json",
    "type": "s3"
  },
  "name": "cray-application-sles15sp5.aarch64-5.2.42"
}
```

1. Customize the image using SAT Bootprep. These commands will add a root password to the image as one is not included. Support for additional product layers will be added in subsequent releases. Update the fields below for the correct software versions, branch names, and

```bash
ncn-m001# cat product_vars.yml
recipe:
  version: app-sle-1
csm:
  version: 1.5.0
  branch: cray/csm/1.16.22
uan:
  version: @product_version@
  branch: integration-@product_version@

ncn-m001# cat bootprep.yml
configurations:
- name: "{{recipe.version}}"
  layers:
  - name: csm
    playbook: csm_packages.yml
    product:
      name: csm
      version: "{{csm.version}}"
      branch: "{{csm.branch}}"
  - name: uan
    playbook: site.yml
    product:
      name: uan
      version: "{{uan.version}}"
      branch: "{{uan.branch}}"
  - name: uan-{{uan.version}}
    playbook: rebuild-initrd.yml
    product:
      name: uan
      version: "{{uan.version}}"
      branch: "{{uan.branch}}"

images:
- name: "{{recipe.version}}"
  ims:
    is_recipe: false
    name: cray-application-sles15sp5.x86_64-5.2.42
  configuration: "{{recipe.version}}"
  configuration_group_names:
  - Application
  - Application_UAN

session_templates:
- name: "{{recipe.version}}"
  image:
    ims:
      name: "{{recipe.version}}"
  configuration: "{{recipe.version}}"
  bos_parameters:
    boot_sets:
      uan:
        kernel_parameters: console=ttyS0,115200 bad_page=panic crashkernel=512M hugepagelist=2m-2g intel_iommu=off intel_pstate=disable iommu.passthrough=on modprobe.blacklist=amdgpu numa_interleave_omit=headless oops=panic pageblock_order=14 rd.neednet=1 rd.retry=10 rd.shell split_lock_detect=off systemd.unified_cgroup_hierarchy=1 ip=:::::eth0:dhcp:10.92.100.225:169.254.169.254 quiet spire_join_token=${SPIRE_JOIN_TOKEN} root=live:s3://boot-images/REPLACE_ME/rootfs psi=1
        node_roles_groups:
        - Application
        rootfs_provider_passthrough: ""
        rootfs_provider: ""

ncn-m001# sat bootprep run --vars-file product_vars.yml bootprep.yml
```

1. Once SAT has completed successfully, the BOS session template must be updated to reference the correct root kernel parameter. This involves replacing "REPLACE_ME" with the resultant image ID from SAT bootprep. The image ID may be determined by first querying IMS.
```bash
ncn-m001# RECIPE_NAME=app-sle-1
ncn-m001# RESULTANT_ID=$(cray ims images list --format json | jq --arg imgname "$RECIPE_NAME" -r '.[] | select(.name == $imgname) | .id' | head -1)

ncn-m001# cray bos sessiontemplates describe $RECIPE_NAME --format json | jq 'del(.name,.tenant)' | sed -e "s/REPLACE_ME/$RESULTANT_ID/g" > $RECIPE_NAME.json
ncn-m001# cray bos sessiontemplates update $RECIPE_NAME --file $RECIPE_NAME.json
```

3. Use the session template to boot one or more nodes.
```bash
ncn-m001# cray bos sessions create --operation reboot --template-name $RECIPE_NAME --limit <xname(s)>
```

1. If the node does not complete the boot successfully, proceed to the troubleshooting section in this guide.

## Troubleshooting

Some general troubleshooting tips may help in getting started using the SLE HPC image.

### Dracut failures during booting

1. Could not find the kernel or the initrd. Verify the BSS boot parameters for the node. Specifically, check that the IMS Image ID is correct.

    ```bash
    http://rgw-vip.nmn/boot-images/13964414-bbad-40e9-9e31-a3683010febbasdf/kernel...HTTP 0x7f0fa808 status 404 Not Found
     No such file or directory (http://ipxe.org/2d0c618e)

    http://rgw-vip.nmn/boot-images/13964414-bbad-40e9-9e31-a3683010febbasdf/initrd...HTTP 0x7f0fa808 status 404 Not Found
     No such file or directory (http://ipxe.org/2d0c618e)
    ```

1. The dracut module `livenet` is missing from the initrd. Make sure that the initrd was regenerated with `/srv/cray/scripts/common/create-ims-initrd.sh` if CFS was used.

    ```bash
    2022-08-24 14:48:53 [    5.784023] dracut: FATAL: Don't know how to handle 'root=live:http://rgw-vip/boot-images/e88ed416-5d58-4421-9013-fa2171ac11b8/rootfs?AWSAccessKeyId=I43RBLH07R65TRO3AL02&Signature=bL661kZHPyEgBsLLEuJHFz3zKVs%3D&Expires=1661438587
    2022-08-24 14:48:53 [    5.805063] dracut: Refusing to continue
    ```


### Unable to log in to the node

1.  The node is not up. Connect to the console and determine why the node has not booted, starting with the troubleshooting tips.

```bash
ncn-m001:# ssh app01
ssh: connect to host uan01 port 22: No route to host
```
1. Unable to log in to the node with a password. No root password is defined in the image by default, one must be added by CFS or by modifying the squashfs filesystem.
```bash
ncn-m001:# ssh app01
    Password:
    Password:
    Password:
    root@app01's password:
    Permission denied, please try again
```

### DHCP hostname is not set

1. If the node does not have a hostname assigned from DHCP, try verifying the DHCP settings and restarting wicked.

    ```bash
    x3000c0s13b0n0:~ # grep -R ^DHCLIENT_SET_HOSTNAME= /etc/sysconfig/network/dhcp
    DHCLIENT_SET_HOSTNAME="yes"
    x3000c0s13b0n0:# systemctl restart wicked
    x3000c0s13b0n0:# hostnamectl
       Static hostname: x3000c0s13b0n0
    Transient hostname: app01
             Icon name: computer-server
               Chassis: server
            Machine ID: 9bd0aacf29d04dd4827bc464121b130b
               Boot ID: af753b4e6fa9419bb14d55a029d0f526
      Operating System: SUSE Linux Enterprise High Performance Computing 15 SP3
           CPE OS Name: cpe:/o:suse:sle_hpc:15:sp3
                Kernel: Linux 5.3.18-150300.59.43-default
          Architecture: x86-64
    x3000c0s13b0n0:# hostname
    app01
    ```

### Spire is not running

1. Check the spire-agent logs for error messages.

    ```bash
    app01# systemctl status spire-agent
    ```
