# Basic UAN Configuration

## UAN configuration overview

Configuration of UAN nodes is performed by the Configuration Framework Service \(CFS\). CFS can apply configuration to both images and nodes. When the configuration is applied to nodes, the nodes must be booted and accessible through SSH over the Node Management Network \(NMN\).

The preferred method of creating CFS configurations is to use the Shasta Admin Toolkit (SAT) `sat bootprep` command.  This command automates the creation of IMS images, CFS configurations, and BOS session templates. See [Create UAN Boot Images](Create_UAN_Boot_Images.md) for more details.

CFS uses configuration layers. Configuration layers allow the sharing of Ansible roles provided by other products, and by the site.  Non-root user access may be blocked during node configuration by enabling the `uan-set-nologin` and `uan-unset-nologin` configuration layers shown in the example bootprep file below. The parameterized fields are defined in a `products_vars.yml` file.

**IMPORTANT** Do not remove or reorder the first three layers. The UAN product requires these layers and this specific order. Also, keep the required `cos-application-last` layer, is as the last or second to last layer in the configuration if `uan-set-nologin` and `uan-unset-nologin` are active.

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

The Ansible roles involved in the UAN layer of the configuration are listed in the site.yml file in the uan-config-management git repository in VCS. Most of the roles that are specific to image configuration are required for the operation as a UAN and must not be removed from site.yml.

The UAN-specific roles involved in post-boot UAN node configuration are:

- [`uan_disk_config`](uan_disk_config.md): this role configures the last disk found on the UAN that is smaller than 1TB, by default. That disk will be formatted with a scratch and swap partition mounted at /scratch and /swap, respectively. Each partition is 50% of the disk.
- [`uan_packages`](uan_packages.md): this role installs any RPM packages listed in the uan-config-management repo.
- [`uan_interfaces`](uan_interfaces.md): this role configures the UAN node networking. By default, this role does not configure a default route or the Customer Access Network \(CAN or CHN\) connection for the HPE Cray EX supercomputer. If CAN or CHN is enabled, the default route will be on the CAN or CHN. Otherwise, a default route must be set up in the customer interfaces definitions. Without the CAN or CHN, there will not be an external connection to the customer site network unless one is defined in the customer interfaces. See [Configure Interfaces on UANs](Configure_Interfaces_on_UANs.md).

  ***NOTE:*** If a UAN layer is used in the Compute node CFS configuration, the `uan_interfaces` role will configure the default route on Compute nodes to be on the HSN, if the BICAN System Default Route is set to `CHN`.
- [`uan_motd`](uan_motd.md): this role Provides a default message of the day that can be customized by the administrator.
- [`uan_ldap`](uan_ldap.md): this optional role configures the connection to LDAP servers. To disable this role, the administrator must set 'uan_ldap_setup:no' in the 'uan-config-management' VCS repository.
- [`uan_hardening`](uan_hardening.md): This role configures site/customer-defined network security of UANs, for example, preventing ssh out of the UAN over the NMN to NCN nodes.

The UAN roles in site.yml are required and must not be removed, with exception of `uan_ldap` if the site is using some other method of user authentication. The `uan_ldap` may also be skipped by setting the value of `uan_ldap_setup` to `no` in a `group_vars` or `host_vars` configuration file.
