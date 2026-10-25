# TP1 project guide: setup and run

This single runbook covers the current BLS prototype and ESP32-S3 + DHT11 firmware. Commands are for Windows PowerShell. Arduino commands use the CLI bundled with the already-installed Arduino IDE; they do not reinstall the IDE.

## 1. Python project: install and run tests

Open PowerShell in the project root and install the Python dependencies:

```powershell
python -m pip install -r requirements.txt
$env:PYTHONPATH = "$PWD\src"
```

Run all current automated tests:

```powershell
python -m pytest -q tests
```

At the time this guide was updated, the observed result was `7 passed in 4.50s`. Run the command again on your machine to verify your environment.

## 2. Run the current BLS software examples

Run the software-only sensor simulation:

```powershell
python -m tp1_bls.mqtt_demo
```

Despite the module name, this is **not an MQTT demo**: it does not connect to Mosquitto or send messages over a network. It simulates sensors locally. Also, its current tampering example signs the changed message with the sensor's secret key before verification, so it does **not** demonstrate rejection of a modified existing signed message. Do not report it as a successful tampering-security experiment.

Run the BLS benchmark:

```powershell
python -m tp1_bls.benchmark
```

This runs batch sizes 2, 8, 32, and 128, then writes `benchmarks\bls_aggregate_benchmark.csv`. The current script uses three measured rounds and reports medians. Batch key generation/signing/individual verification times cover the whole batch, while aggregate verification covers one aggregate operation for that batch. The pure-Python pairing operations can take several minutes; allow it to finish. This is not yet an Ed25519 comparison or a benchmark plot.

## 3. ESP32-S3 + DHT11 wiring

With the board unplugged:

- DHT11 `VCC` → ESP32-S3 `3V3`
- DHT11 `GND` → ESP32-S3 `GND`
- DHT11 `DATA` → ESP32-S3 `GPIO 4`

Check the labels on the sensor module: pin order can differ between modules. Connect the grounds together. Do not power the sensor while changing wires.

## 4. Prepare Arduino CLI

In VS Code, open the project folder, then choose **Terminal → New Terminal**. Run:

```powershell
$cli = "$env:LOCALAPPDATA\Programs\arduino-ide\resources\app\lib\backend\resources\arduino-cli.exe"
$sketch = "$PWD\firmware\esp32_dht11"
```

Confirm that the CLI is accessible:

```powershell
& $cli version
```

## 5. Install the missing Arduino packages

The ESP32 platform was not installed when this guide was written. The ESP32 platform download can be large and take a while. Run these commands only with a reliable internet connection:

```powershell
& $cli core update-index
& $cli core install "esp32:esp32@3.3.12"
& $cli lib install "DHT sensor library"
& $cli lib install "Adafruit Unified Sensor"
```

Verify the installation:

```powershell
& $cli core list
& $cli lib list
```

The core list should contain `esp32:esp32` version `3.3.12`; the library list should contain `DHT sensor library` and `Adafruit Unified Sensor`. If a command reports an error, stop and resolve that error before compiling. A previous install attempt was interrupted, so check the lists before retrying; do not assume the partial download completed.

## 6. Compile the firmware

The board selected here is the generic ESP32-S3 Dev Module (`esp32:esp32:esp32s3`):

```powershell
& $cli compile --fqbn "esp32:esp32:esp32s3" $sketch
```

Continue only if the command reports a successful compile.

## 7. Connect the board and find its COM port

Connect the ESP32-S3 to the computer with a USB data cable. List detected boards:

```powershell
& $cli board list
```

You can also inspect Windows serial ports:

```powershell
[System.IO.Ports.SerialPort]::GetPortNames()
```

Use the new port that appears when the board is connected (for example, `COM5`). Do not use `COM1` unless Windows identifies that as the ESP32-S3. If no new port appears, check the USB cable, board USB connector, and the USB-to-serial driver for the board.

## 8. Upload

Replace `COM5` with the actual port found above:

```powershell
$port = "COM5"
& $cli upload -p $port --fqbn "esp32:esp32:esp32s3" $sketch
```

If upload fails, confirm the selected port and board. Some ESP32-S3 boards require holding **BOOT** while upload starts; follow the instructions for the specific board.

## 9. Read the serial output

Open the monitor at 115200 baud:

```powershell
& $cli monitor -p $port --config 115200
```

The firmware should print one JSON line approximately every two seconds, for example:

```json
{"device_id":"esp32s3-01","seq":1,"status":"ok","temperature_c":24.0,"humidity_percent":50.0,"firmware":"1.0"}
```

The numbers above are an example of the output format, **not measured sensor readings**. A successful real-hardware check requires seeing values from the connected sensor. If the sensor read fails, the firmware prints a JSON line with `"status":"sensor_error"` instead of inventing readings.

To stop the monitor, press `Ctrl+C`.

## Current project status and limitations

The firmware source is in `firmware/esp32_dht11/esp32_dht11.ino`. It has not been confirmed compiled, uploaded, or tested with physical readings yet. Previously, Arduino CLI reported no installed platforms or libraries, and Windows exposed only `COM1`; check the current state because it may have changed. Record the actual compile output and serial output when you run the steps above.

The ESP32 sends unsigned readings. Signing a reading later on the computer can detect changes made after signing, but does not prove that the original reading came from this physical sensor or was not altered before it reached the computer.

The Python BLS code is a learning prototype. Although it uses the `G2ProofOfPossession` ciphersuite and validates public-key points, the project does not yet implement a trusted key-registration flow that verifies and records each participant's proof of possession. Do not claim complete rogue-key protection or production readiness until that trust flow and its tests are implemented.

Still to implement and verify for the overall assignment: serial receiver and GUI, actual MQTT if required by the instructor, robust tampering/replay experiments, authenticated key registration, Ed25519 baseline, benchmark plot, design/threat-model documents, final report, and oral-defense material.
