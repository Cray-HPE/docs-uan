# `uan_motd`

The `uan_motd` role appends text to the `/etc/motd` file.

## Requirements

None.

## Role Variables

Available variables are in the following list, including default values (see `defaults/main.yml`):

```yaml
uan_motd_content: []
```

`uan_motd_content`

: Contains text to be added to the end of the `/etc/motd` file.

## Dependencies

None.

## Example Playbook

```yaml
- hosts: Application_UAN
  roles:
      - { role: uan_motd, uan_motd_content: "MOTD CONTENT" }
```

This role is included in the UAN `site.yml` play.
