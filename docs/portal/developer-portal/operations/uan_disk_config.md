# `uan_disk_config`

The `uan_disk_config` role configures swap and scratch disk partitions on UAN
nodes.

## Requirements

There must be disk devices found on the UAN node by the `device_filter` module
or this role will exit with failure. This condition can be ignored by setting
`uan_require_disk` to `false`. See the following list for variable definitions.

See the `library/device_filter.py` file for more information on this module.

The device that is found will be unmounted if mounted and a swap partition will
be created on the first half of the disk. A scratch partition will be created on the second
half. ext4 filesystems are created on each partition.

## Role Variables

Available variables are in the following list, including default values (see `defaults/main.yml`):

`uan_require_disk`

: Boolean to determine if this role continues to setup disk if no disks were found
by the device filter. Set to `true` to exit with error when no disks are found.

  Example:

  ```yaml
  uan_require_disk: false
  ```

`uan_device_name_filter`

: Regular expression of disk device name for this role to filter.
Input to the `device_filter` module.

  Example:

  ```yaml
  uan_device_name_filter: "^sd[a-f]$"
  ```

`uan_device_name_exclude_filter`

: Regular expression of disk device name to exclude for this role to filter.
Input to the `device_filter` module.

  Example:

  ```yaml
  uan_device_name_exclude_filter: ""
  ```

`uan_device_host_filter`

: List of hosts for this role to filter.
Input to the `device_filter` module.

  Example:

  ```yaml
  uan_device_host_filter: []
  ```

`uan_device_host_exclude_filter`

: List of hosts for this role to exclude.
Input to the `device_filter` module.

  Example:

  ```yaml
  uan_device_host_exclude_filter: []
  ```

`uan_device_model_filter`

: List of the device models for this role to filter.
Input to the `device_filter` module.

  Example:

  ```yaml
  uan_device_model_filter: []
  ```

`uan_device_model_exclude_filter`

: List of the device models for this role to exclude.
Input to the `device_filter` module.

  Example:

  ```yaml
  uan_device_model_exclude_filter: []
  ```

`uan_device_vendor_filter`

: List of the disk vendors for this role to filter.
Input to the `device_filter` module.

  Example:

  ```yaml
  uan_device_vendor_filter: []
  ```

`uan_device_vendor_exclude_filter`

: List of the disk vendors for this role to exclude.
Default is `"LIO-ORG"` and  must be excluded
if Scalable Boot Projection Service, SBPS, is used for
the image projection service.
Input to the `device_filter` module.

  Example:

  ```yaml
  uan_device_vendor_exclude_filter:
    - "LIO-ORG"
  ```

`uan_device_size_filter`

: Regular expression of disk size for this role to filter.
Input to the `device_filter` module.

  Example:
  
  ```yaml
  uan_device_size_filter: "<1TB"
  ```

`uan_swap`

: Filesystem location to mount the swap partition.

  Example:

  ```yaml
  uan_swap: "/swap"
  ```

`uan_scratch`

: Filesystem location to mount the scratch partition.

  Example:

  ```yaml
  uan_scratch: "/scratch"
  ```

`swap_file`

: Name of the swap file to create. Full path is `<uan_swap>/<swapfile>`.

  Example:

  ```yaml
  swap_file: "swapfile"
  ```

`swap_dd_command`

: `dd` command to create the `swapfile`.

  Example:

  ```yaml
  swap_dd_command: "/usr/bin/dd if=/dev/zero of={{ uan_swap }}/{{ swap_file }} bs=1GB count=10"
  ```

`swap_swappiness`

: Value to set the `swapiness` in `sysctl`.

  Example:

  ```yaml
  swap_swappiness: "10"
  ```

## Dependencies

`library/device_filter.py` is required to find eligible disk devices.

### Example Playbook

```yaml
- hosts: Application_UAN
  roles:
      - { role: uan_disk_config }
```

This role is included in the UAN `site.yml` play.
