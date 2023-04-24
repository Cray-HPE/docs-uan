# `uan_hardening`

The `uan_hardening` role configures site/customer-defined network security
 of UANs, for example preventing ssh out of UAN over NMN to NCN nodes.

## Requirements

None.

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

`disable_ssh_out_nmn_to_management_ncns`

: Boolean variable controlling whether or not firewall rules are applied at the UAN to
prevent ssh outbound over the NMN to the NCN management nodes.

The default value of `disable_ssh_out_nmn_to_management_ncns` is `yes`.

```yaml
disable_ssh_out_nmn_to_management_ncns: yes
```

`disable_ssh_out_uan_to_nmn_lb`

: Boolean variable controlling whether or not firewall rules are applied at the UAN to
prevent ssh outbound over the NMN to NMN LB IPs.

The default value of `disable_ssh_out_uan_to_nmn_lb` is `yes`.

```yaml
disable_ssh_out_uan_to_nmn_lb: yes
```

## Dependencies

None.

## Example Playbook

```yaml
- hosts: Application_UAN
  roles:
      - { role: uan_hardening}
```

This role is included in the UAN `site.yml` play.
