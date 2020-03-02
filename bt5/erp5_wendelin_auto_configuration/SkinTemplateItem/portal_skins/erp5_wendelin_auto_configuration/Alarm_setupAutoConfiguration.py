"""
This script will setup the default Wendelin's configuration as saved in erp5_wendelin_scalability_test business template.
As this modifies your site care must be taken!
"""
context.ERP5Site_bootstrapScalabilityTest(user_quantity=0, setup_activity_tool=False, create_test_data=False, set_id_generator=False)
