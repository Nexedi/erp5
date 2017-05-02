"""Run all upgrader steps:

 - pre-upgrade
 - upgrade
 - post-upgrade

"""
portal = context.getPortalObject()
portal_alarms = portal.portal_alarms

pre_upgrade_tag = '%s-preupgrade' % tag
upgrade_tag = '%s-upgrade' % tag
post_upgrade_tag = '%s-postupgrade' % tag

active_process = context.newActiveProcess()


portal_alarms.upgrader_check_pre_upgrade.activate(
  activity='SQLQueue',
  tag=pre_upgrade_tag,
).activeSense(fixit=fixit, params={'tag': pre_upgrade_tag})

portal_alarms.upgrader_check_upgrader.activate(
  activity='SQLQueue',
  tag=upgrade_tag,
  after_tag=pre_upgrade_tag,
 ).activeSense(fixit=fixit, params={'tag': upgrade_tag})

if fixit:
  portal_alarms.upgrader_check_post_upgrade.activate(
    activity='SQLQueue',
    tag=post_upgrade_tag,
    after_tag=upgrade_tag,
  ).activeSense(fixit=fixit, params={'tag': post_upgrade_tag})


# start another activity to collect the results from each upgrader step
context.activate(after_tag=post_upgrade_tag).Alarm_postFullUpgradeNeed(
  active_process=active_process.getRelativeUrl())

# Nothing else to do, so we can disable.
context.setEnabled(False)
