FCO REST client
===============

This repository contains minimalistic python client for FCO REST API, together
with command line client.


Quickstart
----------

At the moment, documentation is non existent, so the best way of learning to
use the tool is to experiment. Command line tool is configured to print help
messages on bad invocations, so you can safely execute any command without
risking doing any damage.

Installation
------------

Start with a new or an existing Python virtual environment (skip if you would
like to install the tool globally)::

    $ mkdir -p ~/fcoclient && cd ~/fcoclient
    $ virtualenv venv

    $ . venv/bin/activate

Install the package::

    $ pip install fcoclient

The `fco` tool should now become available::

    $ fco -h
    usage: fco [-h] [--config CONFIG]
               {configure,disk,firewalltemplate,image,job,network,nic,offer,server,sshkey,vdc}
               ...

Now we need to configure the client by running::

    $ fco configure

This will start an interactive process of providing the required information.
You can obtain this information from your FCO control panel under users section.

To test the configuration, issue some command, for instance::

    $ fco offer list
    [INFO] - Listing product offers
    SERVER: 0.5 GB / 1 CPU (1359c779-5b45-353a-895d-4b2bd317969f)
    SERVER: 1 GB / 1 CPU (65ea40ab-d96f-3d7c-84a0-cf6dd6ee9c67)
    ...
    [INFO] - Offers listed

Tutorial
--------

Prepare some environment variables. To get the values, you can help yourself
with various `fco ... list` commands::

    # UUID of the VDC. See "Information" tab of an existing Server
    export FCO_VDC_UUID=42bb54ac-4090-3caa-b730-e916b27daeff

    # UUID of the Network. See "Information" tab of an existing Server, open its
    #     NIC, see "Information" tab and look for "Network"
    export FCO_NETWORK_UUID=179a6319-3a74-3942-a59c-742d5eab43fe

    # Offer that should be used to create server
    export FCO_DISK_OFFER_UUID=0b54fac2-ce18-3b93-8285-5c827c00cf35
    export FCO_SERVER_OFFER_UUID=bcdbb396-6121-37c8-81ad-37b59a7b92e7

    # UUID of an image of your choice
    export FCO_IMAGE_UUID=00468b94-e602-3b96-9651-f430bec50f3a

    # Optional name of the SSH key pair
    export FCO_KEY_NAME=fco-servers

    # Firewall template name
    export FCO_FW_TEMPLATE_NAME=test-server-secgrp

Create an ssh key pair::

    ssh-keygen -f $FCO_KEY_NAME.pem -N "" -t rsa -q
    chmod 400 $FCO_KEY_NAME.pem

Submit the ssh key to the FCO::

    pubkey=$(echo -n $(cat $FCO_KEY_NAME.pem.pub)) # Remove trailing \n
    key_id=$(cat <<EOF | fco sshkey create -w - | jq -r .itemUUID
    {
      "globalKey": false,
      "publicKey": "$pubkey",
      "resourceName": "$FCO_KEY_NAME"
    }
    EOF
    )

The `key_id` variable now contains the UUID of the key at the FCO.

Next, create a firewall definition. The following commands will construct the
list of rules and store it in the variable `rules`::

    rules="{
      \"action\": \"ALLOW\",
      \"connState\": \"EXISTING\",
      \"direction\": \"IN\",
      \"icmpParam\": \"ECHO_REPLY_IPv4\",
      \"ipAddress\": \"\",
      \"ipCIDRMask\": 0,
      \"localPort\": 0,
      \"name\": \"handshake\",
      \"protocol\": \"ANY\",
      \"remotePort\": 0
    }"
    for port in 22 80 443 5672 8101 53229
    do
      rules="$rules, {
      \"action\": \"ALLOW\",
      \"connState\": \"ALL\",
      \"direction\": \"IN\",
      \"icmpParam\": \"ECHO_REPLY_IPv4\",
      \"ipAddress\": \"0.0.0.0\",
      \"ipCIDRMask\": 0,
      \"localPort\": $port,
      \"name\": \"rule-$port\",
      \"protocol\": \"TCP\",
      \"remotePort\": 0
    }"
    done


The following command creates a firewall template, storing the resulting ID
in the `firewall_id` variable::

    firewall_id=$(cat <<EOF | fco firewalltemplate create -w - \
      | jq -r .itemUUID
    {
      "defaultInAction": "REJECT",
      "defaultOutAction": "ALLOW",
      "firewallInRuleList": [
        $rules
      ],
      "resourceName": "$FCO_FW_TEMPLATE_NAME",
      "type": "IPV4"
    }
    EOF
    )

Now we have everything set up for creating one or more servers. We first set the
name of the server (and, implicitly, the derived names of the related resources
such as the NIC) in the `FCO_SERVER_NAME` variable::

    export FCO_SERVER_NAME=test-server

Then we run the actual creation of the server, storing its ID into the
`instance_id` variable::

    instance_id=$(cat <<EOF | fco server create -k $key_id -w - \
      | jq -r .itemUUID
    {
      "disks": [
        {
          "productOfferUUID": "$FCO_DISK_OFFER_UUID",
          "resourceName": "${FCO_SERVER_NAME}-disk",
          "size": 0,
          "storageCapabilities": [
            "CLONE",
            "CHILDREN_PERSIST_ON_DELETE",
            "CHILDREN_PERSIST_ON_REVERT"
          ],
          "vdcUUID": "$FCO_VDC_UUID"
        }
      ],
      "imageUUID": "$FCO_IMAGE_UUID",
      "nics": [
        {
          "networkUUID": "$FCO_NETWORK_UUID",
          "resourceName": "${FCO_SERVER_NAME}-nic"
        }
      ],
      "productOfferUUID": "$FCO_SERVER_OFFER_UUID",
      "resourceName": "$FCO_SERVER_NAME",
      "vdcUUID": "$FCO_VDC_UUID"
    }
    EOF
    )

The server will be now created, but it is stopped and the firewall is not
applied yet. The following steps will finish this::

    public_ip=$(fco server get $instance_id \
      | jq -r .nics[0].ipAddresses[0].ipAddress)
    fco firewalltemplate apply -w $firewall_id $public_ip
    fco server start -w $instance_id

The variables `FCO_SERVER_NAME`, `instance_id` and `public_ip` now all contain
the name, the UUID, and the public IP, respectively, of the server we have
just created. Once the server starts, we can connect to it using SSH, e.g.::

    username=$(fco server get $instance_id | jq -r .initialUser)
    ssh -i $FCO_KEY_NAME.pem $username@$public_ip

You can go ahead and create further servers. But make sure you note down these
details before overwriting them with the previous ones. E.g. like this::

    echo $instance_id >> my_fco_instance_ids.txt


Cleaning up
-----------

To stop any or all of the servers, you just need to know its UUID. If you have
created multiple servers, refer to the contents of `my_fco_instance_ids.txt`
and assign individual ones to `instance_id`.

Removing a server is done as follows::

    fco server delete -cw $instance_id

The `-cw` switch means that this command will also delete all the depending
resources, and it will only finish executing when the task finishes.

Next, we delete the firewall template::

    fco firewalltemplate delete -w $firewall_id

This too will wait for completion thanks to the `-w` switch.

Finally, if we want to, we can also delete the SSH key::

    fco sshkey delete -w $key_id
