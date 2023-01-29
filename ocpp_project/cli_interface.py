import asyncio
import typer
import questionary
import websockets
from cp_module import charge_point as Cp

app = typer.Typer()


async def connect_to_central_system(cp_serial_id: str):
    # Connect to central system
    ws = await websockets.connect(
        f"ws://0000:9000/{cp_serial_id}", subprotocols=["ocpp2.0.1"]
    )
    charge_point = Cp.ChargePoint(cp_serial_id, ws)
    loop = asyncio.get_event_loop()
    loop.create_task(charge_point.start())

    # Boot notification
    typer.secho("Boot notification", fg=typer.colors.RED, bold=True)
    message = await charge_point.send_boot_notification()
    typer.echo(message)

    # # Status notification
    # typer.secho("Status notification", fg=typer.colors.RED, bold=True)
    # message = await charge_point.send_status_notification()
    # typer.echo(message)

    return charge_point


async def send_message(cp, message: str):
    response = await cp.messages[message](cp)
    typer.echo(response)


@app.command()
def start():
    async def _start():
        # Start program
        # typer.prompt("Starting the Charge point")
        typer.echo("-------------Starting the Charge point-------------")
        cp_serial_id = typer.prompt("Ener charge point serial number", default="CP_1")

        charge_point = await connect_to_central_system(cp_serial_id)
        result = await questionary.select(
            "Select an activity from below: ",
            choices=["Send an OCPP message", "Exit"],
        ).ask_async()
        if result == "Quit":
            raise type.Abort()
        # Send message to a charge_point
        while True:
            message = await questionary.select(
                "What message do you want to send: ",
                choices=list(charge_point.messages.keys()),
            ).ask_async()
            await send_message(charge_point, message)
            continue_check = typer.confirm("Do you want to send another message?")
            if not continue_check:
                break

    asyncio.run(_start())


if __name__ == "__main__":
    typer.run(start)
