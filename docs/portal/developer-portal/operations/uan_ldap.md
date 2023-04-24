# `uan_ldap`

The `uan_ldap` role configures LDAP and AD groups on UAN nodes.

## Requirements

NSCD, pam-config, sssd.

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

`uan_ldap_setup`

: A boolean variable to selectively skip the setup of LDAP on nodes it would otherwise be configured due to `uan_ldap_config` being defined.  The default setting is to setup LDAP when `uan_ldap_config` is not empty.

  Example:

  ```yaml
  uan_ldap_setup: yes
  ```

`uan_ldap_config`

: Configures LDAP domains and servers. If this list is empty, no LDAP configuration will be applied to the UAN targets and all role tasks will be skipped.

  Example:

  ```yaml
  uan_ldap_config:
    - domain: "mydomain-ldaps"
      search_base: "dc=...,dc=..."
      servers: ["ldaps://123.123.123.1", "ldaps://213.312.123.132"]
      chpass_uri: ["ldaps://123.123.123.1"]

    - domain: "mydomain-ldap"
      search_base: "dc=...,dc=..."
      servers: ["ldap://123.123.123.1", "ldap://213.312.123.132"]
  ```

`uan_ad_groups`

: Configures active directory groups on UAN nodes.

  Example:

  ```yaml
  uan_ad_groups:
    - { name: admin_grp, origin: ALL }
    - { name: dev_users, origin: ALL }
  ```

`uan_pam_modules`

: Configures PAM modules on the UAN nodes in `/etc/pam.d`.

  Example:

  ```yaml
  uan_pam_modules:
    - name: "common-account"
      lines:
        - "account required\tpam_access.so"
  ```

## Dependencies

None.

## Example Playbook

```yaml
- hosts: Application_UAN
  roles:
      - { role: uan_ldap }
```

This role is included in the UAN `site.yml` play.
