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
        assert host.file("/opt/locust.io/slave").is_directory
        assert host.file("/etc/systemd/system/locust-slave.service").exists
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
       (slave, locust-3 and locust-5) and that they are running
       using the base virtualenv. It also tests that instance locust-3
       is running under the expected ownership and has been restarted
       with changed locust_classes."""
    pythons = host.process.filter()
    locusts = [proc for proc in pythons
               if '/opt/locust.io/base/virtenv/bin/locust' in proc.args]
    assert len(locusts) == 3
    with host.sudo():
        cmd = host.run("pwdx {} {} {}".format(locusts[0].pid,
                                              locusts[1].pid,
                                              locusts[2].pid))
    assert '/opt/locust.io/slave' in cmd.stdout
    assert '/opt/locust.io/locust-3' in cmd.stdout
    assert '/opt/locust.io/locust-5' in cmd.stdout
    l3 = list(filter(
      lambda x: '--logfile=locust-3.log' in x.args, locusts
      ))
    assert len(l3) == 1
    assert l3[0].user == 'daemon'
    assert l3[0].group == 'daemon'
    assert 'MyOtherLocust' in l3[0].args
    assert len(list(filter(
      lambda x: '/opt/locust.io/locust-5/./locustfile.py' in x.args, locusts
      ))) == 1
    assert len(list(filter(
      lambda x: '/opt/locust.io/base/virtenv/bin/python' in x.args, locusts
      ))) == 3


def test_services_running(host):
    """This tests whether the correct set of services is running from
       a systemd point of view."""
    assert host.service("locust-slave").is_running
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
      '/opt/locust.io/locust-2/start_script').content_string
    assert "--csv=" not in unit
    assert "--loglevel=" not in unit
    assert "--logfile=" not in unit


def test_locust_3_optional_parameters(host):
    """This verifies that instance locust-3 has all optional parameters,
       as they were used to create it."""
    unit = host.file(
      '/opt/locust.io/locust-3/start_script').content_string
    assert "--csv=" in unit
    assert "--loglevel=" in unit
    assert "--logfile=" in unit
    assert "MyLocust" in unit
    assert "MyOtherLocust" in unit


def test_locust_3_is_enabled(host):
    """Checks whether instance-3 is enabled to start at boot-time
       from systemd's perspective."""
    assert host.service('locust-locust-3').is_enabled


def test_locust_3_has_correct_owner(host):
    """Have a look at the owner and group of the instance directory
       and data files of locust-3"""
    with host.sudo():
        f = host.file("/opt/locust.io/locust-3")
        assert f.user == 'daemon'
        assert f.group == 'daemon'
        f = host.file("/opt/locust.io/locust-3/locustfile.py")
        assert f.user == 'daemon'
        assert f.group == 'daemon'


def locust_5_uses_absolute_path_locustfile(host):
    """This verifies that instance locust-5 was created using the
       absolute path to the locustfile that was explicitly given
       as a parameter, instead of the relative path as with the other."""
    unit = host.file(
      '/opt/locust.io/locust-5/start_script').content_string
    assert "--locustfile=/opt/locust.io/locust-5/./locustfile.py" in unit
