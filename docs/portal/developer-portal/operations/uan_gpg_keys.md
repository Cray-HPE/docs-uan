# `uan_gpg_keys`

The `uan_gpg_keys` role installs the CSM GPG signing public key. This role is a dependency of the
`uan_packages` role.

## Requirements

The Kubernetes secret must be available in the namespace and field specified
by the following `uan_gpg_key_*` variables. The key must be stored as a base64-encoded
string.

## Role Variables

Available variables are in the following list, including default values (defined in
`defaults/main.yml`):

`uan_gpg_key_k8s_secret`

: The Kubernetes secret which contains the GPG public key.

  Example:

  ```yaml
     uan_gpg_key_k8s_secret: "hpe-signing-key"
  ```

`uan_gpg_key_k8s_namespace`

: The Kubernetes namespace which contains the secret.

  Example:

  ```yaml
     uan_gpg_key_k8s_namespace: "services"
  ```

`uan_gpg_key_k8s_field`

: The field in the Kubernetes secret that holds the GPG public key.

  Example:

  ```yaml
     uan_gpg_key_k8s_field: "gpg-pubkey"
  ```

## Dependencies

None.

### Example Playbook

```yaml
   - hosts: Application
      roles:
         - role: uan_gpg_key
```

This role is included in the UAN `site.yml` play.
