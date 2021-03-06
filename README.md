# Ansible Role `locust`

Manages Locust.io instances.

## Requirements

Locust.io requires ZeroMQ. This role will therefor install the
ZeroMQ library.

On Ubunto, libzmq-devel will be installed.

On CentOS, zeromq-devel and gcc will be installed to compile the
necessary python pips for Locust.io. The upstream ZeroMQ yum
repository will be registered and enabled to do this.

All python related software requirements will be auto-installed
inside a virtualenv.

## Role Parameters

### Common parameters for all modes

| Variable        | Default   | Comments (type)                              |
| :---            | :---      | :---                                         |
| `instance_name` | `default` | Name to distiguish instances.                |
| `mode`          | `slave`   | Must be either master, slave or stand-alone  |
| `state`         | `started` | State of Locust.io on the host.              |
| `enabled`       | `false`   | If true, start this instance after reboots   |
| `run_as_user`   | `root`    | Which unix user to launch Locust.io as       |
| `run_as_group`  | `root`    | Which unix group to launch Locust.io under   |
| `instance_data` |           | Path to data to be copied into instance dir  |
| `locust_classes`| `[]`      | List of client classes to run                |
| `locustfile`    |           | The Locust.io scenario file to play          |
| `logfile`       |           | Filename of the Locust.io logfile            |
| `loglevel`      |           | Locust.io log level                          |
| `base_dir`      | `/opt/locust.io` | Where to put Locust.io & instance data |

### Master Mode and Stand-Alone Mode Parameters

| Variable        | Default   | Comments (type)                              |
| :---            | :---      | :---                                         |
| `host`          |           | URL of the host to load test                 |
| `web_host`      |           | IP address to bind the web interface to      |
| `web_port`      |           | Port to bind the web interface to            |
| `csv`           |           | Base name of CSV report files                |

### Master Mode Parameters

| Variable        | Default   | Comments (type)                              |
| :---            | :---      | :---                                         |
| `bind_host`     |           | IP address to bind the master instance to    |
| `bind_port`     |           | TCP port number of the Locust.io master      |
| `no_web`        | `true`    | No web interface, start tests immediately    |
| `expect_slaves` |           | How many slaves to wait for before starting  |
| `clients`       |           | Number of clients. Required for `no_web`     |
| `hatch_rate`    |           | Spawn rate of clients. Required for `no_web` |
| `num_request`   |           | Number of requests to perform; for `no_web`  |
| `run_time`      |           | How long to test, e.g. '1h30m'; for `no_web` |

### Slave Mode Parameters

| Variable        | Default   | Comments (type)                              |
| :---            | :---      | :---                                         |
| `master_host`   |           | IP, hostname or FQDN of the Locust.io master |
| `master_port`   | 5557      | TCP port number of the Locust.io master      |

The `state` parameter can be one of:

* `started` - Locust.io should be up and running
* `restarted` - Locust.io should be freshly restarted
* `stopped` - Locust.io should be present but should not be running
* `absent` - Locust.io should not be installed

A directory named `/opt/locust.io` will be created. Inside of it, a
subdirectory per instance will be created. If `state` is set to `absent`,
this subdirectory will be removed. The location can be changed with the
`base_dir` parameter, but if you do you will have to specify the `base_dir`
parameter again on all future plays controlling this instance, as otherwise
it will not be found. The `base_dir` itself will be removed along with the
last instance.

The `instance_data` parameter can point to a file or directory to
be copied into the instance subdirectory. For example, `instance_data: data/`
would copy the `data/` directory inside your playbook's `files/` directory
to the instance subfolder.

You can specify the `locustfile` parameter as a path relative to the
`instance_data` content root. (see example below)

Note: the `run_time` parameter requires Locust.io v0.9, which is not
available via pip, as of this writing.

Note: for reasons unknown Locust.io requires specifying `bind_host: '*'` but `web_host: ''` to bind to all available interfaces, respectively.

## Operating Systems

This role was developed and tested for CentOS 7.4. It was also
tested for Ubuntu 16.04. (Xenial)

## Dependencies

None

## Example Playbook

To have a running Locust.io master/slave setup you could do this:

    - hosts: locust_master
      tasks:
      - include_role:
           name: tinx.locust
        vars:
           mode: master
           instance_data: data/
           locustfile: 'stresstest-prod.py'

    - hosts: locust_slaves
      tasks:
      - include_role:
           name: tinx.locust
        vars:
           mode: slave
           master_host: locust-master.example.com
           instance_data: data/
           locustfile: 'stresstest-prod.py'

The master would wait for at least one slave to connect and would
then start testing.

### Examples

There are further examples in the `examples/` directory:
 - running a master/slave setup inside two docker containers
 - building docker images using `ansible-container`

## Testing

Molecule tests are provided. Naturally, they require additional dependencies.

## License

BSD

## Author Information

 - [Andreas Jaekel](https://github.com/tinx/)
