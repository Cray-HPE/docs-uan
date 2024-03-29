# `uan_interfaces`

The `uan_interfaces` role configures site or customer-defined network interfaces
and Customer Access Network (CAN) network interfaces on UAN nodes.

## Requirements

None.

## Role Variables

Available variables are in the following list, including default values (see `defaults/main.yml`):

`uan_nmn_bond`

: A Boolean variable controlling the configuration of the Node Management Network (NMN).
When true, the NMN network connection will be configured as a bonded pair of interfaces defined by the members of the
`uan_nmn_bond_slaves` variable. The bonded NMN interface is named `nmnb0`. When false, the NMN network connection
will be configured as a single interface named `nmn0`.

The default value of `uan_nmn_bond` is `no`.

```yaml
uan_nmn_bond: no
```

`uan_nmn_bond_slaves`

: A list of the interfaces to use as the bond slave pair when `uan_nmn_bond` is true.

The interface names must be in a format which does not change between reboots of the node, such as `ens10f0`
which is the first port of the NIC in slot 10.  

**NOTE:** `ens10f0` is typically the first port of the OCP 25Gb card that
the node PXE boots.

**IMPORTANT:** The first interface in the list must be the `nmn0` interface which is configured during the
initial image boot, typically `ens10f0`. This interface order is required because the MAC address of the `nmn0` interface
is the MAC associated with the IP address of the UAN. The bonded `nmnb0` interface and the bond slaves
will assume this MAC and the IP address of `nmn0` to preserve connectivity.

The second interface is typically the first port of a different 25Gb NIC for resiliency.

The default values of `uan_nmn_bond_slaves` are shown here. Change them as needed to match the actual
node cabling and NIC configuration.

```yaml
uan_nmn_bond_slaves:
  - "ens10f0"
  - "ens1f0"
```

`uan_can_setup`

: Boolean variable controlling the configuration of user
access to UAN nodes. When true, user access is configured over either the
Customer Access Network (CAN) or Customer High Speed Network (CHN), depending on which is configured on the system.

When `uan_can_setup` is false, user access over the CAN or CHN is not configured
on the UAN nodes, and no default route is configured. The Admin must then specify
the default route in `customer_uan_routes`.

The default value of `uan_can_setup` is `no`.

```yaml
uan_can_setup: no
```

`uan_can_bond_slaves`

: A list of the interfaces to use as the bond slave pair when `uan_can_setup` is true, `uan_nmn_bond` is true, and the Customer Access Network (CAN) is configured on the system. This variable is ignored if `uan_nmn_bond` is false.

The interface names must be in a format which does not change between reboots of the node, such as `ens10f1`
which is the second port of the NIC in slot 10.  

**NOTE:** `ens10f1` is typically the second port of the OCP 25Gb card and is used as one of the bond
slaves in the CAN `bond0` interface.

The second interface is typically the second port of a different 25Gb NIC for resiliency.

The default values of `uan_can_bond_slaves` are shown here. They may need to be changed to match the actual
node cabling and NIC configuration.

```yaml
uan_can_bond_slaves:
  - "ens10f1"
  - "ens1f1"
```

`uan_chn_device`

: The default CHN device on the UAN nodes. Overwrite the default value to use a different device for the CHN on UAN nodes.

The default value of `uan_chn_device` is shown here.

```yaml
uan_chn_device: "hsn0"
```

`uan_customer_default_route`

: Boolean variable that allows the default route
to be set by the `customer_uan_routes` data when `uan_can_setup` is true.

By default, no default route is setup unless `uan_can_setup` is true, which sets the default route to the CAN or CHN.

```yaml
uan_customer_default_route: no
```

`sls_nmn_name`

: Node Management Network name used by SLS.
This value must not be changed.

```yaml
sls_nmn_name: "NMN"
```

`sls_nmn_svcs_name`

: Node Management Services Network name used by SLS.
This value must not be changed.

```yaml
sls_nmn_svcs_name: "NMNLB"
```

`sls_mnmn_svcs_name`

: Mountain Node Management Services Network name used
by SLS. This value must not be changed.

```yaml
sls_mnmn_svcs_name: "NMN_MTN"
```

`uan_required_dns_options`

: List of DNS options. By default, `single-request` is set and must not be removed.

```yaml
uan_required_dns_options:
  - 'single-request'
  ```

`customer_uan_interfaces`

: List of interface names used for constructing
`ifcfg-<customer_uan_interfaces.name>` files. Define the ifcfg fields for each
interface here. Field names are converted to uppercase in the generated
`ifcfg-<name>` file or files.

Interfaces must be defined in order of dependency.

```yaml
customer_uan_interfaces: []

# Example:
customer_uan_interfaces:
  - name: "net1"
    settings:
      bootproto: "static"
      device: "net1"
      ipaddr: "1.2.3.4"
      startmode: "auto"
  - name: "net2"
    settings:
      bootproto: "static"
      device: "net2"
      ipaddr: "5.6.7.8"
      startmode: "auto"
```

`customer_uan_routes

: List of interface routes used for constructing
`ifroute-<customer_uan_routes.name>` files.

```yaml
customer_uan_routes: []

# Example
customer_uan_routes:
  - name: "net1"
    routes:
      - "10.92.100.0 10.252.0.1 255.255.255.0 -"
      - "10.100.0.0 10.252.0.1 255.255.128.0 -"
  - name: "net2"
    routes:
      - "default 10.103.8.20 255.255.255.255 - table 3"
      - "10.103.8.128/25 10.103.8.20 255.255.255.255 net2"
```

`customer_uan_rules`

: List of interface rules used for constructing
`ifrule-<customer_uan_routes.name>` files.

```yaml
customer_uan_rules: []

# Example
customer_uan_rules:
  - name: "net1"
    rules:
      - "from 10.1.0.0/16 lookup 1"
  - name: "net2"
    rules:
      - "from 10.103.8.0/24 lookup 3"
```

`customer_uan_global_routes`

: List of global routes used for constructing
the "routes" file.

```yaml
customer_uan_global_routes: []

# Example
customer_uan_global_routes:
  - routes: 
    - "10.92.100.0 10.252.0.1 255.255.255.0 -"
    - "10.100.0.0 10.252.0.1 255.255.128.0 -"
```

`external_dns_searchlist`

: List of customer-configurable fields to be added
to the `/etc/resolv.conf` DNS search list.

```yaml
external_dns_searchlist: [ '' ] 

# Example
external_dns_searchlist:
  - 'my.domain.com'
  - 'my.other.domain.com'
```

`external_dns_servers`

: List of customer-configurable fields to be added
to the `/etc/resolv.conf` DNS server list.

```yaml
external_dns_servers: [ '' ] 

# Example
external_dns_servers:
  - '1.2.3.4'
  - '5.6.7.8'
```

`external_dns_options`

: List of customer-configurable fields to be added
to the `/etc/resolv.conf` DNS options list.

```yaml
external_dns_options: [ '' ]

# Example
external_dns_options:
  - 'single-request'
```

`uan_access_control`

: Boolean variable to control whether non-root access
control is enabled. Default is `no`.

```yaml
uan_access_control: no
```

`api_gateways`

: List of API gateway DNS names to block non-user access

```yaml
api_gateways:
  - "api-gw-service"
  - "api-gw-service.local"
  - "api-gw-service-nmn.local"
  - "kubeapi-vip"
```

`api_gw_ports`

: List of gateway ports to protect.

```yaml
api_gw_ports: "80,443,8081,8888"
```

`sls_url`

: The SLS URL.

```yaml
sls_url: "http://cray-sls"
```

### Dependencies

None.

### Example Playbook

```yaml
- hosts: Application_UAN
  roles:
      - { role: uan_interfaces }
```

This role is included in the UAN `site.yml` play.
