## Setup

Clone the source code to all the VMs that you want to test. There are many ways to do it efficiently. One way is to use sshpass. 

```bash
sshpass -p "password" rsync -a /your_directory_name address_of_vm
```

## Start

Start by launching the script with `python Talker.py` on each of the VM.

One machine will be the introducer. The address of introducer can be configured in  `Util.py`

In the beginning, the daemon will ask you to select a heart-beating style `gossip` or `all-to-all`, select `unknown` if you want that daemon to follow the style of other machines in the network. 

## Others

The heart-beating style can be switched without exiting the process. Type either `gossip` or `alltoall`, then the style of all the VMs will be switched seamlessly to the new type you just entered.

You can choose to terminate the process by typing `control + c` or type `leave` 

