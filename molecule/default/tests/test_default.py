import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_correct_directory(host):
    """This tests whether the instance has been installed to
       the correct directory. It also checks for the correctly
       named systemd unit file. Additionally, it checks whether
       the default instance_name has been used."""
    with host.sudo():
        assert host.file("/usr/local/locust/default").is_directory
        assert host.file("/etc/systemd/system/locust-default.service").exists
