# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

    # Use the precised64 box, change this for 32 bit, or other distro
    config.vm.box = "ubuntu/trusty64"

    # Set the box host-name
    config.vm.hostname = "bca-webtools"

    # Run the provisioning script       
    config.vm.provision :shell, :path => "./provision/bootstrap.sh"

    # Port forward HTTP (80) to host 2020
    config.vm.network :forwarded_port, :host => 2020, :guest => 80

    config.vm.provider :virtualbox do |vb|
      vb.name = "bca-webtools-dev"
      vb.memory = 4096
      vb.cpus = 2
    end
end

