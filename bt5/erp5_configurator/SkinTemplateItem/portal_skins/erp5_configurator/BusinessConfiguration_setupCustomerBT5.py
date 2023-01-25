configuration_save = context.restrictedTraverse(configuration_save_url)
configuration_save.addConfigurationItem("Customer BT5 Configurator Item",
                                        bt5_title='_'.join(context.getTitle().strip().lower().split()))
