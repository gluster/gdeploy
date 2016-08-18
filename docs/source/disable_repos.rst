How to disable repos
=====================

 To disable enabled repos, use the action 'disable-repos'. The required repos
 should be passed as value to repos option.

**NOTE :** If repos are not provided all the enabled  repos will be disabled.

**Step 1:**

Create an empty file and give it any arbitrary name. For the purpose of this
demonstration, let's call our file ``disable.conf``. Add the following
lines to your newly created config file::


 [RH-subscription]
 action=disable-repos
 repos=fancy_repo1,fancy,repo2

**Step 2:**

Invoke gdeploy and run the following command::

  $ gdeploy -c disable.conf

