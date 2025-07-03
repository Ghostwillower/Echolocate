# EchoLocate

EchoLocate passively tracks where everyday objects were last heard using the computer's microphone.

## Features

- **Room fingerprinting** using short mel-spectrogram averages.
- **Item sound recognition** with MFCC templates and DTW matching.
- **Event logging** to a local SQLite database.
- **CLI**: `teach`, `run`, `where <item>` commands.
- **HTTP API**: `/where/<item>` endpoint reporting last zone and time.

## Installation

1. Install Python 3.12 or later.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To run commands use `python echolocate_cli.py <command>`.
### Teach an item
You can provide a recording or let EchoLocate capture one from the microphone.

Record automatically (3 seconds by default):
```bash
echolocate teach keys
```

Or use an existing WAV file:
```bash
echolocate teach keys --file keys.wav
```

### Run the listener
```bash
echolocate run --port 8000
```
This starts listening in the background and exposes the HTTP API.

### Query an item
```bash
echolocate where keys
```

You can also query via HTTP:
```
GET http://localhost:8000/where/keys
```

## Tests

Run unit tests with:
```bash
python -m pytest
```
