# NextBridge

A minimal peer-to-peer chat and file transfer application for the terminal, built directly on raw TCP sockets in pure Python — no frameworks, no external dependencies.

NextBridge is a learning project: every layer, from the wire protocol to the threading model, is written by hand so the mechanics of network programming stay visible instead of being hidden behind a library.

## How it works

Each running instance is both a server and a client at the same time — that is what makes it peer-to-peer rather than client/server.

- **`P2PServer`** binds to your chosen port, listens for incoming connections, and handles each connected peer in its own daemon thread. It decodes whatever arrives: chat packets or incoming files.
- **`P2PClient`** opens an outbound connection to another peer's port and sends chat messages and files over it.
- **`protocol.py`** defines the message format shared by both sides.

Because a single TCP connection is used in one direction only, a full two-way conversation requires both peers to connect to each other.

### Wire protocol

Two kinds of traffic travel over the socket:

**Chat messages** are UTF-8 encoded JSON objects:

```json
{ "type": "CHAT", "content": "hello", "sender": "Peer-5000" }
```

**File transfers** use a plain-text header, followed by the raw bytes of the file in 4096-byte chunks, terminated by a sentinel:

```
FILE_START:<filename>:<size_in_bytes>
<raw file bytes …>
FILE_END
```

Received files are written to the `received_files/` directory, which is created automatically on first use.

## Requirements

- Python 3.8 or newer
- No third-party packages (`requirements.txt` is intentionally empty; everything comes from the standard library: `socket`, `threading`, `json`, `os`)

## Running it

Start the first peer:

```bash
python3 app.py
```

```
--- NEXTBRIDGE ---
Enter your own listening port: 5000
Do you want to connect to a peer? (y/n): n
```

Then start a second peer in another terminal and point it at the first one:

```bash
python3 app.py
```

```
--- NEXTBRIDGE ---
Enter your own listening port: 5001
Do you want to connect to a peer? (y/n): y
Peer port to connect to: 5000
```

Peer 5001 can now send to peer 5000. For a two-way chat, answer `y` on both sides and have each peer connect to the other's port.

## Commands

| Input | Effect |
| --- | --- |
| `<any text>` | Send the text to the connected peer as a chat message |
| `/file <path>` | Send the file at `<path>` to the connected peer |
| `exit` | Shut the peer down |

Example:

```
> hello there
> /file ~/Documents/notes.pdf
> exit
```

## Project layout

```
NextBridge/
├── app.py                      # Entry point: prompts, session loop, command parsing
├── app/
│   └── networking/
│       ├── server.py           # P2PServer: listen, accept, receive chat and files
│       ├── client.py           # P2PClient: connect, send chat, send files
│       └── protocol.py         # Packet creation and parsing (JSON)
├── received_files/             # Destination for incoming files
├── requirements.txt            # Empty: standard library only
└── LICENSE
```

## Current limitations

These are known and deliberately documented, since the project is a study of the underlying networking concepts:

- **No message framing.** TCP is a byte stream, not a message stream. Two chat packets that arrive in a single `recv()` call, or one packet split across two calls, will fail to parse. A length-prefixed header (for example `struct.pack('!I', len(payload))`) would fix this properly.
- **File transfer relies on timing and a sentinel.** `time.sleep()` is used to keep the header separate from the file body, and the literal bytes `FILE_END` mark the end of a transfer. Both are fragile: a binary file that happens to contain `FILE_END` will be truncated.
- **Connections are one-directional.** Each socket carries traffic only from the connecting peer to the listening peer.
- **Localhost only.** The client connects to `127.0.0.1`; the host argument passed to the server is currently ignored in favour of `0.0.0.0`.
- **No encryption or authentication.** All traffic is sent in the clear, and any peer that can reach the listening port can send files that get written to disk. Do not expose this to an untrusted network.
- **Duplicate input loop.** `app.py` contains a second, redundant input loop, so `exit` currently has to be entered twice.

## Roadmap

- Length-prefixed binary framing to replace the current ad-hoc parsing
- A single duplex connection per peer pair, so one link carries both directions
- Peer discovery on the local network instead of manual port entry
- Transfer progress reporting and checksum verification for files
- Optional TLS for encrypted transport

## License

See [LICENSE](LICENSE).
