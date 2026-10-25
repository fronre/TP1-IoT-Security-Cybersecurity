# TP1 IoT Security – BLS Aggregate Signature

This project implements a documented BLS aggregate signature scheme for an IoT sensor scenario using `py_ecc` 7.0.1.

## Environment

- Python 3.15.0
- py_ecc 7.0.1
- pytest 9.1.1

## Install

```powershell
python -m pip install -r requirements.txt
$env:PYTHONPATH = "$PWD\src"
```

## Run tests

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m pytest -q tests
```

## Run benchmark

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m tp1_bls.benchmark
```

## Notes

- The implementation uses the standard BLS12-381 `G2ProofOfPossession` ciphersuite from `py_ecc`.
- Aggregate verification checks public-key validity, but trusted proof-of-possession registration is not implemented yet; do not treat the prototype as fully protected from rogue-key attacks.
- Benchmark CSV is stored under `benchmarks/bls_aggregate_benchmark.csv`.

## ESP32-S3 + DHT11 hardware setup

See [docs/ESP32_DHT11_SETUP.md](docs/ESP32_DHT11_SETUP.md) for the single project runbook: Python install/tests, BLS demo and benchmark commands, wiring, Arduino CLI package installation, compile, upload, Serial Monitor, and current limitations. The hardware firmware has not yet been confirmed compiled or tested against real sensor readings.
