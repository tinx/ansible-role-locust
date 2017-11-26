import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_only_one_virtualenv(host):
    """This veryfies that there is only one virtualenv installed under
       /opt/locust.io, to make sure all instances use the same instead
       of having received their individual copies or something."""
    with host.sudo():
        cmd = host.run("find /opt/locust.io -type f -name activate | wc -l")
    assert cmd.rc == 0
    assert cmd.stdout == '1'


def test_correct_directory(host):
    """This tests whether the correct set of instances is installed
       by checking whether their instance directories and systemd
       unit filed exists or do not exist."""
    with host.sudo():
        assert host.file("/opt/locust.io/master").is_directory
        assert host.file("/etc/systemd/system/locust-master.service").exists
        assert not host.file("/opt/locust.io/locust-1").exists
        assert not host.file(
          "/etc/systemd/system/locust-locust-1.service").exists
        assert host.file("/opt/locust.io/locust-2").is_directory
        assert host.file("/etc/systemd/system/locust-locust-2.service").exists
        assert host.file("/opt/locust.io/locust-3").is_directory
        assert host.file("/etc/systemd/system/locust-locust-3.service").exists
        assert host.file("/opt/locust.io/locust-4").is_directory
        assert host.file("/etc/systemd/system/locust-locust-4.service").exists
        assert host.file("/opt/locust.io/locust-5").is_directory
        assert host.file("/etc/systemd/system/locust-locust-5.service").exists


def test_instances_running(host):
    """This tests that only the expected three instances are running,
       (master, locust-3 and locust-5) and that they are running
       using the base virtualenv."""
    pythons = host.process.filter(user="root")
    locusts = [proc for proc in pythons if 'locust.io' in proc.args]
    assert len(locusts) == 3
    assert len(list(filter(
      lambda x: '/opt/locust.io/master/locustfile.py' in x.args, locusts
      ))) == 1
    assert len(list(filter(
      lambda x: '/opt/locust.io/locust-3/locustfile.py' in x.args, locusts
      ))) == 1
    assert len(list(filter(
      lambda x: '/opt/locust.io/locust-5/./locustfile.py' in x.args, locusts
      ))) == 1
    assert len(list(filter(
      lambda x: '/opt/locust.io/base/virtenv/bin/python' in x.args, locusts
      ))) == 3


def test_services_running(host):
    """This tests whether the correct set of services is running from
       a systemd point of view."""
    assert host.service("locust-master").is_running
    # service "locust-locust-1" does not exist since the
    # instance locust-1 has been de-installed with "state=absent"
    assert not host.service("locust-locust-2").is_running
    assert host.service("locust-locust-3").is_running
    assert not host.service("locust-locust-4").is_running
    assert host.service("locust-locust-5").is_running


def test_locust_2_optional_parameters(host):
    """This verifies that instance locust-2 has only the minimum required
       set of parameters, as no optional parameters were used to create it."""
    unit = host.file(
      '/etc/systemd/system/locust-locust-2.service').content_string
    assert "--master" in unit
    assert "--master-bind-host=" not in unit
    assert "--master-bind-port=" in unit
    assert "--web-host=" not in unit
    assert "--web-port=" not in unit
    assert "--no-web" in unit
    assert "--clients=" not in unit
    assert "--hatch-rate=" not in unit
    assert "--num-request=" not in unit
    # assert "--run-time=" not in unit
    assert "--host=" not in unit
    assert "--expect-slaves=" not in unit
    assert "--csv=" not in unit
    assert "--loglevel=" not in unit
    assert "--logfile=" not in unit


def test_locust_3_optional_parameters(host):
    """This verifies that instance locust-3 has all optional parameters,
       as they were used to create it."""
    unit = host.file(
      '/etc/systemd/system/locust-locust-3.service').content_string
    assert "--master " not in unit
    assert "--master-bind-host=" in unit
    assert "--master-bind-port=" in unit
    assert "--web-host=" in unit
    assert "--web-port=" in unit
    assert "--no-web" not in unit
    assert "--clients=" in unit
    assert "--hatch-rate=" in unit
    assert "--num-request=" in unit
    # assert "--run-time=" in unit
    assert "--host=" in unit
    assert "--expect-slaves=" in unit
    assert "--csv=" in unit
    assert "--loglevel=" in unit
    assert "--logfile=" in unit
    assert "MyLocust" in unit


def locust_5_uses_absolute_path_locustfile(host):
    """This verifies that instance locust-5 was created using the
       absolute path to the locustfile that was explicitly given
       as a parameter, instead of the relative path as with the other."""
    unit = host.file(
      '/etc/systemd/system/locust-locust-5.service').content_string
    assert "--locustfile=/opt/locust.io/locust-5/./locustfile.py" in unit
