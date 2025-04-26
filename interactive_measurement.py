import time
from datetime import datetime

import rich
import rich.status
import serial

console = rich.get_console()

filename = console.input("Measuring input name: ")


def iter_data_from_serial(comport: str, baudrate: int = 115200):
    ser = serial.Serial(comport, baudrate, timeout=0.1)

    while 1:
        try:
            data = ser.readline().decode("utf-8").strip()
        except UnicodeDecodeError:
            continue

        if not data:
            continue

        yield int(data)


with rich.status.Status("Preparing") as status:
    current = time.perf_counter()

    while (delta := time.perf_counter() - current) < 5:
        status.update(f"Ready in {5 - delta:.2f}s")
        time.sleep(0.1)


with rich.status.Status("Preparing") as status:
    current = time.perf_counter()

    iterator = iter_data_from_serial("COM4")

    with open(f"measurement_{filename}.txt", "a") as file_writer:
        while (delta := time.perf_counter() - current) < 10:
            data = next(iterator)
            file_writer.write(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}] {data}\n"
            )
            status.update(f"Measuring for {10 - delta:.2f}s, last: {data}")

console.print("Completed successfully.")
