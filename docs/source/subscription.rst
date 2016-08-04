Subscribe to Red Hat Subscription Management
===========================================

The section 'RH-subscription' can be used to register the system to RHSM,
attach to a pool, enable repos, disable repos, and unregister from RHSM.


**Step 1:**

Create an empty file and give it any arbitrary name. For the purpose of this
demonstration, let's call our file ``subscription.conf``. Add the following
lines to your newly created config file.
(lines beginning with # are comments for your information and can be ignored)::

 # Registering the system
 #
 # To register the system use the 'action' register and specify 'password' and
 # 'username'.
 # Set 'auto-attach' option as 'true' if the product certificates
 # are are available at /etc/pki/product/
 # 'disable-repos', if set to "yes", will disable all the repos currently
 # enabled in the system.
 # 'repos' can also be specified in the same configuration section to
 # specify which all repos it should subscribe to, at the time of
 # registration itself.
 # We can even make subscription-manager attach this system to a subscription
 # pool at this section itself. Use the option 'pool' for this.

 [RH-subscription]
 action=register
 username=bilbobaggins
 # use a valid username in place of bilbobaggins
 password=shire46
 # use a valid password in place of shire46
 auto-attach=true
 disable-repos=yes
 repos=rhel-7-cool-server
 pool=a_big_pool_id_with_numbers
 # Replace above placeholder string with appropriate pool id

 # Instead of using username and password, one could even use an
 # activationkey
 #
 # [RH-subscription]
 # action=register
 # activationkey=my_big_activation_key
 # Replace above activationkey with appropriate activation key you may have
 # received.

 # The options: auto-attach, disable-repos, repos, and pools applies here
 # as well
 #
 # Attaching to the Red Hat subscription
 #
 # If not auto-attached, then attaching to the subscription needs to be done
 # explicitly. One could either give the option 'pool' with the pool id as value
 # along with the register action or can be separately provided as follows
 #
 # [RH-subscription]
 # action=attach-pool
 # pool=a_big_pool_id_with_numbers
 #
 #  
 # Enabling repos

 # To enable repos, provide the repo names as value to option 'repos'. This can
 # be provided with register action as well or separately as follows
 #
 # [RH-subscription]
 # action=enable-repos
 # repos=fancy_repo1,fancy_repo2
 #
 #
 # Registering, subscribing and enabling repos together
 #
 # These 3 can be done together in a single config block leaving the action empty as
 # follows
 #
 # [RH-subscription]
 # action=register
 # username=bilbobaggins
 # password=shire46
 # pool=a_big_pool_id_with_numbers
 # repos=fancy_repo1,fancy_repo2
 #
 # Disabling repos
 #
 # To disable enabled repos, use the action 'disable-repos'. The required repos
 # should be passed as value to repos option.
 # NOTE: If repos are not provided all the enabled  repos will be disabled
 #
 # [RH-subscription]
 # action=disable-repos
 # repos=fancy_repo1,fancy_repo2
 #
 #
 # Unregister from RHSM
 #
 # To unregister the system from RHSM just provide the action 'unregister'
 #
 # [RH-subscription]
 # action=unregister
 
**Step 2:**

Make sure you have appropriate values in all the placeholders shown in the
sample above, namely, ``username``, ``password``, ``activation key`` and etc.
Invoke gdepoy as follows to run the file::
  
  $ gdeploy -c subscription.conf


