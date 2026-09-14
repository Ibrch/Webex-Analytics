Vagrant.configure("2") do |config|

  config.vm.box = "bento/ubuntu-24.04"

  config.vm.provider "virtualbox" do |vb|
    vb.name = "webex-analytics-dev"
    vb.memory = 4096
    vb.cpus = 2
  end

  config.vm.provision "ansible_local" do |ansible|
    ansible.playbook = "ansible/site.yml"
  end

end
