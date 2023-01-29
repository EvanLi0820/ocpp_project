import asyncio
import logging
from datetime import datetime

try:
    import websockets
except ModuleNotFoundError:
    print("This example relies on the 'websockets' package.")
    print("Please install it by running: ")
    print()
    print(" $ pip install websockets")
    import sys

    sys.exit(1)

from ocpp.routing import on
from ocpp.v201 import ChargePoint as cp
from ocpp.v201 import call_result, enums, call, datatypes

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):
    @on(enums.Action.BootNotification)
    def on_boot_notification(self, charging_station, reason, **kwargs):
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(), interval=10, status="Accepted"
        )

    @on(enums.Action.Heartbeat)
    def on_heartbeat(self):
        print("Got a Heartbeat!")
        return call_result.HeartbeatPayload(
            current_time=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        )

    @on(enums.Action.ClearCache)
    async def on_clear_cache(self):
        return call_result.ClearCachePayload(status=enums.ClearCacheStatusType.accepted)

    @on(enums.Action.FirmwareStatusNotification)
    async def on_firmware_status_notification(self):
        return call_result.FirmwareStatusNotificationPayload()

    @on(enums.Action.GetDisplayMessages)
    async def on_get_display_messages(self, **kwargs):
        return call_result.GetDisplayMessagesPayload(
            status=enums.GetDisplayMessagesStatusType.accepted
        )

    @on(enums.Action.MeterValues)
    async def on_meter_value(self, **kwargs):
        return call_result.MeterValuesPayload()

    @on(enums.Action.NotifyChargingLimit)
    async def on_notify_charging_limit(self, **kwargs):
        return call_result.NotifyChargingLimitPayload()

    @on(enums.Action.ClearedChargingLimit)
    async def on_cleared_charging_limit(self, **kwargs):
        return call_result.ClearedChargingLimitPayload()


async def on_connect(websocket, path):
    """For every new charge point that connects, create a ChargePoint
    instance and start listening for messages.
    """
    try:
        requested_protocols = websocket.request_headers["Sec-WebSocket-Protocol"]
    except KeyError:
        logging.info("Client hasn't requested any Subprotocol. " "Closing Connection")
        return await websocket.close()

    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        # In the websockets lib if no subprotocols are supported by the
        # client and the server, it proceeds without a subprotocol,
        # so we have to manually close the connection.
        logging.warning(
            "Protocols Mismatched | Expected Subprotocols: %s,"
            " but client supports %s | Closing connection",
            websocket.available_subprotocols,
            requested_protocols,
        )
        return await websocket.close()

    charge_point_id = path.strip("/")
    charge_point = ChargePoint(charge_point_id, websocket)

    await charge_point.start()


async def connect_to_central_system():
    #  deepcode ignore BindToAllNetworkInterfaces: <Example Purposes>
    server = await websockets.serve(
        on_connect, "0.0.0.0", 9000, subprotocols=["ocpp2.0.1"]
    )

    logging.info("Server Started listening to new connections...")
    await server.wait_closed()


async def start_mock_connection():
    server = await websockets.serve(
        on_connect, "0.0.0.0", 9000, subprotocols=["ocpp2.0.1"]
    )

    logging.info("WebSocket Server Started")
    return server


if __name__ == "__main__":
    # asyncio.run() is used when running this example with Python >= 3.7v
    asyncio.run(connect_to_central_system())
