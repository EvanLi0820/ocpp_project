import websockets
import pytest
from unittest.mock import patch
import asyncio
from faker import Faker
from ocpp_project.cp_module import charge_point as cp
from ocpp_project.central_system import start_mock_connection

fake = Faker()
pytest_plugins = ("pytest_asyncio",)


async def cancel_tasks():
    for task in asyncio.all_tasks():
        task.cancel()


@patch("ocpp_project.cp_module.charge_point.select_from_list")
@patch("typer.prompt")
@pytest.mark.asyncio
async def test_status_and_boot_notifications(mock_typer, mock_ask_question):
    server = await start_mock_connection()
    async with websockets.connect(
        f"ws://0.0.0.0:9000/CP_1", subprotocols=["ocpp2.0.1"]
    ) as ws:
        charge_point = cp.ChargePoint("CP_1", ws)
        loop = asyncio.get_running_loop()
        loop.create_task(charge_point.start())

        mock_typer.return_value = "CP_1"
        mock_ask_question.return_value = "PowerUp"
        result = await charge_point.send_boot_notification()
        assert result.status == "Accepted"
        assert result.interval == 10

        await cancel_tasks()
        server.close()


@pytest.mark.asyncio
async def test_clear_cache():
    server = await start_mock_connection()
    async with websockets.connect(
        f"ws://0.0.0.0:9000/123", subprotocols=["ocpp2.0.1"]
    ) as ws:
        charge_point = cp.ChargePoint("123", ws)
        loop = asyncio.get_running_loop()
        loop.create_task(charge_point.start())

        result = await charge_point.send_clear_cache()
        assert result.status == "Accepted"

        await cancel_tasks()
        server.close()


@patch("ocpp_project.cp_module.charge_point.select_from_list")
@pytest.mark.asyncio
async def test_cleared_charging_request(mock_ask_question):
    server = await start_mock_connection()
    async with websockets.connect(
        f"ws://0.0.0.0:9000/123", subprotocols=["ocpp2.0.1"]
    ) as ws:
        charge_point = cp.ChargePoint("123", ws)
        loop = asyncio.get_running_loop()
        loop.create_task(charge_point.start())

        mock_ask_question.return_value = "EMS"
        result = await charge_point.send_cleared_charging_request()
        assert str(result) == "ClearedChargingLimitPayload()"

        await cancel_tasks()
        server.close()
