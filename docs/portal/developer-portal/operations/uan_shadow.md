# `uan_shadow`

The `uan_shadow` role configures the root password on UAN nodes.

## Requirements

The root password hash has to be installed in HashiCorp Vault at `secret/uan root_password`.

## Role Variables

Available variables are in the following list, including default values (see `defaults/main.yml`):

`uan_vault_url`

: The URL for the HashiCorp Vault

  Example:

  ```yaml
  uan_vault_url: "http://cray-vault.vault:8200"
  ```

`uan_vault_role_file`

: The required Kubernetes role file for HashiCorp Vault access.

  Example:

  ```yaml
  uan_vault_role_file: /var/run/secrets/kubernetes.io/serviceaccount/namespace
  ```

`uan_vault_jwt_file`

: The path to the required Kubernetes token file for HashiCorp Vault access.

  Example:

  ```yaml
  uan_vault_jwt_file: /var/run/secrets/kubernetes.io/serviceaccount/token
  ```

`uan_vault_path`

: The path to use for storing data for UANs in HashiCorp Vault.

  Example:

  ```yaml
  uan_vault_path: secret/uan
  ```

`uan_vault_key`

: The key used for storing the root password in HashiCorp Vault.

  Example:

  ```yaml
  uan_vault_key: root_password
  ```

## Dependencies

None.

## Example Playbook

```yaml
- hosts: Application_UAN
  roles:
      - { role: uan_shadow }
```

This role is included in the UAN `site.yml` play.
