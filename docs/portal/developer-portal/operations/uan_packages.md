# `uan_packages`

The `uan_packages` role adds or removes additional repositories and RPMs on UANs
using the Ansible `zypper_repository` and `zypper` module.

Repositories and packages added to this role will be installed or removed during
image customization. Installing RPMs during post-boot node configuration can
cause high system loads on large systems so these tasks run only during image
customizations.

This role will only run on SLES-based nodes.

## Requirements

Zypper must be installed.

The `csm.gpg_keys` Ansible role must be installed if `uan_disable_gpg_check`
is false.

## Role Variables

Available variables are in the following list, including default values (see defaults/main.yml):

This role uses the `zypper_repository` module. The `name`, `description`, `repo`,
`disable_gpg_check`, and `priority` fields are supported.

This role uses the `zypper` modules. The `name` and `disable_gpg_check` fields are supported.

`uan_disable_gpg_check`

: Sets the `disable_gpg_check` field on Zypper repos and
packages listed in the `uan_sles15_repositories add` and `uan_sles15_packages_add`
lists. The `disable_gpg_check` field can be overridden for each repo or package.

`uan_sles15_repositories_add`

: List of repositories to add.

`uan_sles15_packages_add`

: List of RPM packages to add.

## Dependencies

None.

## Example Playbook

```yaml
- hosts: Application_UAN
  roles:
     - role: uan_packages
       vars:
         uan_sles15_packages_add:
           - name: "foo"
             disable_gpg_check: yes
           - name: "bar"
         uan_sles15_packages_remove:
           - baz
         uan_sles15_repositories_add:
           - name: "uan-2.5.0-sle-15sp4"
             description: "UAN SUSE Linux Enterprise 15 SP4 Packages"
             repo: "https://packages.local/repository/uan-2.5.0-sle-15sp4"
             disable_gpg_check: no
             priority: 2
```

This role is included in the UAN `site.yml` play.
