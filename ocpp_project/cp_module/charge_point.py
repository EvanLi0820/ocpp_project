from ocpp.v201 import ChargePoint as cp, call, call_result, datatypes, enums
import logging
import typer
import questionary
import asyncio
from datetime import datetime, timedelta
from faker import Faker

import uuid

logging.basicConfig(level=logging.INFO)


async def select_from_list(enum_type, question: str):
    options = [option.value for option in enum_type]
    result = await questionary.select(question, choices=list(options)).ask_async()
    return result


fake = Faker()


class ChargePoint(cp):
    async def send_heartbeat(self):
        request = call.HeartbeatPayload()
        response = await self.call(request)
        return response

    async def send_boot_notification(self):
        model = typer.prompt("Enter charge point model", default="model_test")
        vendor_name = typer.prompt("Enter charge point vendor name", default="SEE_TEST")
        reason_type = await select_from_list(
            enums.BootReasonType, "Select a reason type:"
        )
        request = call.BootNotificationPayload(
            charging_station={"model": model, "vendor_name": vendor_name},
            reason=reason_type,
        )
        response = await self.call(request)

        # if response.status == "Accepted":
        #     print("Connected to central system.")
        #     await self.send_heartbeat(response.interval)

        return response

    async def send_clear_cache(self):
        request = call.ClearCachePayload()
        response = await self.call(request)
        return response

    async def send_firmware_status_notification(self):
        firmware_status = await select_from_list(
            enums.FirmwareStatusType, "Select firmware status notification:"
        )
        request = call.FirmwareStatusNotificationPayload(status=firmware_status)
        response = await self.call(request)
        return response

    async def send_get_display_messages(self):
        request_id = typer.prompt("Enter request id", fake.random_int(min=0, max=10))
        request = call.GetDisplayMessagesPayload(request_id=request_id)
        response = await self.call(request)
        return response

    async def send_authorize(self):
        id_type = await select_from_list(enums.IdTokenType, "Which ID token type:")
        request = call.AuthorizePayload(
            id_token={"idToken": str(uuid.uuid4()), "type": id_type},
        )
        response = await self.call(request)
        return response

    async def send_cleared_charging_request(self):
        charging_limit_source = await select_from_list(
            enums.ChargingLimitSourceType, "Which charging limit source:"
        )
        request = call.ClearedChargingLimitPayload(
            charging_limit_source=charging_limit_source
        )
        response = await self.call(request)
        return response

    async def send_meter_value(self):
        unit = await select_from_list(
            enums.UnitOfMeasureType, "Select measure unit type:"
        )
        evse_id = int(typer.prompt("Enter EVSE ID", default=fake.random_int()))
        value = int(typer.prompt("Enter sample value", default=fake.random_int()))
        value_context = await select_from_list(
            enums.ReadingContextType, "Select value context type:"
        )
        value_measurand = await select_from_list(
            enums.MeasurandType, "Select value measurand type:"
        )
        value_phase = await select_from_list(
            enums.PhaseType, "Select value phase type:"
        )
        request = call.MeterValuesPayload(
            evse_id=evse_id,
            meter_value=[
                datatypes.MeterValueType(
                    timestamp=str(datetime.now()),
                    sampled_value=[
                        datatypes.SampledValueType(
                            value=value,
                            context=value_context,
                            measurand=value_measurand,
                            phase=None,
                            location=None,
                            unit_of_measure=datatypes.UnitOfMeasureType(unit=unit),
                        ),
                        datatypes.SampledValueType(
                            value=value,
                            context=value_context,
                            measurand=value_measurand,
                            phase=value_phase,
                            location=None,
                            unit_of_measure=datatypes.UnitOfMeasureType(unit=unit),
                        ),
                    ],
                ),
                datatypes.MeterValueType(
                    timestamp=str(datetime.now() + timedelta(seconds=5)),
                    sampled_value=[
                        datatypes.SampledValueType(
                            value=value,
                            context=value_context,
                            measurand=value_measurand,
                            phase=None,
                            location=None,
                            unit_of_measure=datatypes.UnitOfMeasureType(unit=unit),
                        ),
                        datatypes.SampledValueType(
                            value=value,
                            context=value_context,
                            measurand=value_measurand,
                            phase=value_phase,
                            location=None,
                            unit_of_measure=datatypes.UnitOfMeasureType(unit=unit),
                        ),
                    ],
                ),
            ],
        )
        response = await self.call(request)
        return response

    async def send_notify_charging_limit(self):
        charging_limit_source = await select_from_list(
            enums.ChargingLimitSourceType, "Which charging limit source:"
        )
        request = call.NotifyChargingLimitPayload(
            charging_limit={
                "charging_limit_source": charging_limit_source,
                "is_grid_critical": True,
            }
        )
        response = await self.call(request)
        return response

    messages = {
        "Authorize": send_authorize,
        "Clear cache": send_clear_cache,
        "Cleared Charging Limit": send_cleared_charging_request,
        "Firmware Status Notification": send_firmware_status_notification,
        # 'Get 15118 EV Certificate': send_get_15118ev_certificate,
        # 'Get Certificate Status': send_get_certificate_status,
        "Get Display Messages": send_get_display_messages,
        # 'Log Status Notification': send_log_status_notification,
        "Meter Value": send_meter_value,
        "Notify Charging Limit": send_notify_charging_limit,
        # 'Notify Customer Information': send_notify_customer_information,
        # 'Notify Display Messages': send_notify_display_messages,
        # 'Notify EV Charging Needs': send_notify_ev_charging_needs,
        # 'Notify EV Charging Schedule': send_notify_ev_charging_schedule,
        # 'Notify Event': send_notify_event,
        # 'Notify Monitoring Report': send_notify_monitoring_report,
        # 'Notify Report': send_notify_report,
        # 'Publish Firmware Status': send_publish_firmware_status_notification,
        # 'Report Charging Profiles': send_report_charging_profiles,
        "Heartbeat": send_heartbeat,
        # 'Start transaction': send_start_transaction,
        # 'Stop transaction': send_stop_transaction,
        # 'Reservation Status Update': send_reservation_status_update,
        # 'Security Event Notification': send_security_event_notification,
        # 'Sign Certificate': send_sign_certificate,
        # 'Transaction Event': send_transaction_event
    }
    # async def send_status_notification(self):
