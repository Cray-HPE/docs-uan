# Basic UAN Configuration

## UAN configuration overview

The Configuration Framework Service \(CFS\) performs the configuration of UAN nodes. CFS can apply configuration to both images and nodes. When the configuration is applied to nodes, the nodes must be booted and accessible through SSH over the Node Management Network \(NMN\).

The preferred method of creating CFS configurations is to use the Shasta Admin Toolkit (SAT) `sat bootprep` command. This command automates the manual process described in [Create UAN Boot Images](Create_UAN_Boot_Images.md). That process includes creating IMS images, CFS configurations, and BOS session templates.

CFS uses configuration layers. Configuration layers allow the sharing of Ansible roles provided by other products, and by the site. Non-root user access may be blocked during node configuration by enabling the `uan-set-nologin` and `uan-unset-nologin` configuration layers shown in the following example bootprep file. The parameterized fields are defined in a `product_vars.yml` file.

**IMPORTANT** Do not remove or reorder the first three layers. The HPE Cray Supercomputing UAN product requires these layers and this specific order. Also, keep the required `cos-application-last` layer as the last or second to last layer in the configuration if `uan-set-nologin` and `uan-unset-nologin` are active.

```bash
- name: "{{default.note}}uan-{{recipe.version}}{{default.suffix}}"
  layers:
  # The first three layers are required and must not be reordered.
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
# Optional layer to prevent non-root logins during configuration
#  - name: uan-set-nologin-{{uan.working_branch}}
#    playbook: set_nologin.yml
#    product:
#      name: uan
#      version: "{{uan.version}}"
#      branch: "{{uan.working_branch}}"
  - name: uan-{{uan.working_branch}}
    playbook: site.yml
    product:
      name: uan
      version: "{{uan.version}}"
      branch: "{{uan.working_branch}}"

### additional CFS layers here... 

# cos-application-last is required to be the last or second to last layer
# when uan-set-nologin and uan-unset-nologin layers are active.
  - name: cos-application-last-{{cos.working_branch}}
    playbook: cos-application-after.yml
    product:
      name: cos
      version: "{{cos.version}}"
      branch: "{{cos.working_branch}}"
# Optional layer to allow non-root logins after configuration
#  - name: uan-unset-nologin-{{uan.working_branch}}
#    playbook: unset_nologin.yml
#    product:
#      name: uan
#      version: "{{uan.version}}"
#      branch: "{{uan.working_branch}}"
```

## Required CFS Layers for UAN Configuration

### Slingshot Host Software (playbook: shs_{{default.network_type}}_install.yml)

The first CFS Layer installs the Slingshot Host Software for the Slingshot network type of the system. The `default.network_type` is:

- `mellanox` for ConnectX-5 NICs used in Slingshot 10
- `cassini` for Slingshot NICs in Slingshot 11

The name of the playbook must match the name of the HSN NICs (Mellanox or Cassini) in the UAN nodes. Additionally, the HSN NICs must be of the same type as the NCN and Compute nodes.

### COS (playbook: cos-application.yml)

The second CFS Layer runs the following roles from the `cos-config-management` VCS repository. Any configuration changes needed for these roles must be made in the `cos-config-management` `group_vars` or `host_vars` subdirectories of that repository.

The following Ansible roles are run during UAN image configuration:

- **Standard UNIX configuration**

  - `cos-config-map`
  - `rsyslog`
  - `localtime`
  - `ntp`
  - `limits`
  - `kdump`

- **Allow trust of CSM generated keys for elective passwordless SSH during image customization**

  - `trust-csm-ssh-keys`

- **HPE Cray EX system configurations**

  - `overlay-preload`

- **Install COS rpms**

  - `cos-services-install`

- **DVS/LNET/FS

  - `cray_lnet_install`
  - `cray_dvs_install`
  - `cray_lnet_load`
  - `cray_dvs_load`

The following Ansible roles are run during UAN post-boot configuration:

- **Standard UNIX configuration**

  - `rsyslog`

- **HPE Cray EX system configurations**

  - `ca-cert`
  - `overlay-preload`

- **GPU deploy support**

  - `cray_gpu_deploy`

### CMS Layer (playbook: csm_packages.yml)

The third CFS Layer installs the Cray Management System packages. These packages are normally not modified.

### Optional UAN Layer (playbook: set_nologin.yml)

This optional layer is recommended when the nodes will host non-root users. The layer touches the `/etc/nologin` file preventing non-root users from logging into the node while it is being configured. Be sure to include the optional UAN layer which calls the `unset_nologin.yml` playbook as indicated in this document if non-root users are to be allowed to login after the node is configured.

### UAN Layer (playbook: site.yml)

The Ansible roles involved in the UAN layer of the configuration are listed in the site.yml file in the uan-config-management git repository in VCS. Most of the roles that are specific to image configuration are required for the operation as a UAN and must not be removed from site.yml.

The UAN-specific roles involved in post-boot UAN node configuration are:

- [`uan_disk_config`](uan_disk_config.md): this role configures the last disk found on the UAN that is smaller than 1TB, by default. That disk will be formatted with a scratch and swap partition mounted at `/scratch` and `/swap`, respectively. Each partition is 50% of the disk.
- [`uan_packages`](uan_packages.md): this role installs any RPM packages listed in the uan-config-management repo.
- [`uan_interfaces`](uan_interfaces.md): this role configures the UAN node networking. By default, this role does not configure a default route or the Customer Access Network \(CAN or CHN\) connection for the HPE Cray EX supercomputer. If CAN or CHN is enabled, the default route will be on the CAN or CHN. Otherwise, a default route must be set up in the customer interfaces definitions. Without the CAN or CHN, there will not be an external connection to the customer site network unless one is defined in the customer interfaces. See [Configure Interfaces on UANs](Configure_Interfaces_on_UANs.md).

  ***NOTE:*** If a UAN layer is used in the Compute node CFS configuration, the `uan_interfaces` role will configure the default route on Compute nodes to be on the HSN, if the BICAN System Default Route is set to `CHN`.
- [`uan_motd`](uan_motd.md): this role Provides a default message of the day that the administrator can customize.
- [`uan_ldap`](uan_ldap.md): this optional role configures the connection to LDAP servers. To disable this role, the administrator must set `uan_ldap_setup:no` in the `uan-config-management` VCS repository.
- [`uan_hardening`](uan_hardening.md): This role configures site or customer-defined network security of UANs, for example, preventing SSH access from the UAN over the NMN to NCN nodes.

The UAN roles in `site.yml` are required and must not be removed, with exception of `uan_ldap` if the site is using some other method of user authentication. The `uan_ldap` may also be skipped by setting the value of `uan_ldap_setup` to `no` in a `group_vars` or `host_vars` configuration file. Configuration of this layer is made in the `uan-config-management` VCS repository.

### COS (playbook: cos-application-after.yml)

This CFS Layer runs the following roles from the `cos-config-management` VCS repository. Any configuration changes needed for these roles must be made in the `group_vars` or `host_vars` subdirectories of that repository.

The following Ansible roles are run during UAN image configuration:

- `rebuilt-initrd`

The following Ansible roles are run during UAN post-boot configuration:

- `configure_fs`

### Optional UAN Layer (playbook: unset_nologin.yml)

This UAN layer deletes the `/etc/nologin` file allowing non-root users to log into the UAN. If the optional UAN layer that runs `set_nologin.yml` was used, this layer must be used or only the root user will have access to the node.
