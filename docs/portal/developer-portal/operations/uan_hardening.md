# `uan_hardening`

The `uan_hardening` role configures site or customer-defined network security
 of UANs, for example preventing SSH access from the UAN over the NMN to NCN nodes.

## Requirements

None.

## Role Variables

Available variables are in the following list, including default values (see `defaults/main.yml`):

`disable_ssh_out_nmn_to_management_ncns`

: Boolean variable controlling whether firewall rules are applied at the UAN to
prevent SSH outbound over the NMN to the NCN management nodes.

The default value of `disable_ssh_out_nmn_to_management_ncns` is `yes`.

```yaml
disable_ssh_out_nmn_to_management_ncns: yes
```

`disable_ssh_out_uan_to_nmn_lb`

: Boolean variable controlling whether firewall rules are applied at the UAN to
prevent SSH outbound over the NMN to NMN LB IP addresses.

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
