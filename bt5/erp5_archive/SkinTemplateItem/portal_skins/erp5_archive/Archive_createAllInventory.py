# This script is intended to be call at archive creation
# It will launch one activity per group of 10 node uid in order
# to create inventory and same for payment_uid

account_uid_list = [x.uid for x in context.Archive_getBankAccountUidList()]
node_uid_list = [x.node_uid for x in context.Archive_getNodeUidList(connection_id=source_connection_id,
                                                                    account_uid_list=account_uid_list)]

#context.log("node_uid_list", node_uid_list)
while len(node_uid_list):
  activity_node_list = node_uid_list[:10]
  node_uid_list = node_uid_list[10:]
  context.portal_simulation.activate(activity="SQLQueue", round_robin_scheduling=1,
                                     tag=tag).Archive_createInventory(node_uid_list=activity_node_list,
                                                                      source_connection_id=source_connection_id,
                                                                      destination_sql_catalog_id=destination_sql_catalog_id,
                                                                      inventory_date=inventory_date,
                                                                      tag=tag)

payment_uid_list = [x.payment_uid for x in context.Archive_getPaymentUidList(connection_id=source_connection_id,
                                                                             account_uid_list=account_uid_list)]

#context.log("payment_uid_list", payment_uid_list)
while len(payment_uid_list):
  activity_payment_list = payment_uid_list[:10]
  payment_uid_list = payment_uid_list[10:]
  context.portal_simulation.activate(activity="SQLQueue", round_robin_scheduling=1,
                                     tag=tag).Archive_createInventory(payment_uid_list=activity_payment_list,
                                                                      source_connection_id=source_connection_id,
                                                                      destination_sql_catalog_id=destination_sql_catalog_id,
                                                                      inventory_date=inventory_date,
                                                                      tag=tag)
