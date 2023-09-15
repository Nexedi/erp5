"""
This script operates within a context provided by the portal object.
It takes a data chunk, unpacks it, and then creates a new MQTT message
object within the portal, using specific attributes from the unpacked
data such as "topic" and "payload" for the message content.
"""

portal = context.getPortalObject()
data = context.unpack(data_chunk)[0][1]

portal.mqtt_message_module.newContent(
    portal_type="MQTT Message",
    title=data["topic"],
    payload=data["payload"]
)
