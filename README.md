# [KeyWave Chat Application](https://github.com/raresgoidescu/keywave)

Link to the repository: [keywave](https://github.com/raresgoidescu/keywave)

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Client Side](#client-side)
  - [Diffie-Hellman Key Exchange Protocol](#diffie-hellman-key-exchange-protocol)
  - [Encryption / Decryption](#encryption--decryption)
  - [Credits](#credits)
- [Server Side](#server-side)
  - [Functionality](#functionality)
  - [Client Connect / Disconnect and the server socket map](#client-connect--disconnect-and-the-server-socket-map)
  - [Event queue](#event-queue)
  - [Sending updates](#sending-updates)
  - [Account Login / Account Create requests](#account-login--account-create-requests)
  - [Inviting another user to a chat room](#inviting-another-user-to-a-chat-room)
  - [Diffie-Hellmann Key Exchange Events](#diffie-hellmann-key-exchange-events)
  - [Credits](#credits-1)
- [Database](#database)
  - [Main Functionalities](#main-functionalities)
  - [How it works](#how-it-works)
  - [Testing the database](#testing-the-database)
  - [Credits](#credits-2)
- [Interface (CLI)](#interface-cli)
  - [Configuration](#configuration)
  - [Authentication](#authentication)
  - [Main Interface Loop](#main-interface-loop)
  - [Chat Initialization](#chat-initialization)
  - [Error Handling](#error-handling)
  - [Platform Compatibility](#platform-compatibility)
  - [Credits](#credits-3)
- [Problems encountered along the way](#problems-encountered-along-the-way)
  - [Blocking Operations](#blocking-operations)
  - [Shortcomings](#shortcomings)
  - [Our Next Steps](#our-next-steps)
- [Contributors](#contributors)

<ins>***NOTE***</ins>: To make the imports work, run `source setup.sh` in the root dir of the project.

## Introduction

KeyWave is a privacy oriented chat application that allows users to communicate privately over a network with no security compromises.
The application uses the Diffie-Hellman key exchange protocol to establish a secure connection between users and encrypts messages using AES-256 in CBC mode.

The application consists of two main components:
- A client-side application that provides a secure chat interface for users.
- A server-side application that manages user connections, chat invitations, and message forwarding.

The client application provides a command-line interface for user interaction, including account creation, login, chat initiation, and message exchange.
The server application acts as a central node that connects users and forwards messages between them, ensuring secure communication.

The server is designed to be oblivious to the content of messages, only forwarding them to the intended recipient without decryption.

## Installation

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/raresgoidescu/keywave.git && cd keywave
```

Create a virtual environment and activate it:

```bash
python3 -m venv .
source bin/activate
```

We tried to keep the application as minimal as possible in terms of dependencies, so the only required package is `cryptography`.

To install the requirements, run:

```bash
pip install -r requirements.txt
```

## Usage

Before running the application, make sure to set up the `PYTHONPATH` environment variable to include the project root directory:

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

or source the `setup.sh` script:

```bash
source setup.sh
```

Sadly this needs to be done on any newly opened terminal.

To start the server, run:

```bash
./src/server/server.py
```

To start the client, run:

```bash
./main.py
```

## Client Side

### Diffie-Hellman Key Exchange Protocol

Our chat application uses this protocol to establish a secret key between two users. This protocol is based on five exchanges, explained quickly in this diagram: [drawio](https://static.cristimacovei.dev/drawio-key-exchange.png)

Assume the key exchange happens between two users `Alice` and `Bob`, and `Alice` is the one that initiates the exchange.

#### I. Sharing public data

- `Alice` chooses two integers `mod` and `base`, and sends them to `Bob`

#### II. Confirmation of public data

- `Bob` sends the public data back to `Alice` to confirm it has been received properly and they share the same values.

#### III. Key Sharing (Alice's side)

- `Alice` chooses her secret key `a` (an integer), computes the value `A` = `base ^ a % mod` and sends it to `Bob`.

#### IV. Key Sharing (Bob's side)

- `Bob` receives `Alice`'s key `A`, and does the same process: chooses his secret key `b`, computes `B` = `base ^ b % mod` and sends it to `Alice`.

#### V. Shared Secret

- `Alice` can now compute `key` = `a ^ B % mod`.
- `Bob` can now compute `key` = `b ^ A % mod`.
- Both keys are equal to `base ^ (a * b) % mod`.

#### Security

Although an eavesdropper can capture `mod` and `base`, and even both values of `A` and `B`, it is unable to compute the secret key. 

Computing `A * B` is useless since it would equal `base ^ (a + b) % mod`.

### Encryption / Decryption

After the key exchange was successfully completed, clients own secret keys that can be used to encrypt and decrypt messages.

The implementation uses AES-256 in CBC mode with HKDF key derivation for secure content encryption.

#### Encryption Algorithm

The encryption process takes a content string and an integer key as input, returning the encrypted content along with 
necessary decryption parameters. (`Client.__encrypt_content() -> Tuple[cipher_bytes, iv_bytes, salt_bytes]`)

##### Key Derivation

The implementation uses HKDF (HMAC-based Key Derivation Function) with SHA-256 to derive a 32-byte encryption key.
The process generates a random 16-byte salt which is combined with the input key.
The derived key provides enhanced security compared to using the raw input key directly.

##### Encryption Process

The encryption function performs the following steps:
- The input key is first converted to bytes using big-endian encoding.
- A cryptographically secure random salt is generated and used with HKDF to derive the encryption key.
- The function then generates a random 16-byte initialization vector (IV) required for CBC mode operation.

The encryption uses the Cipher implementation from the cryptography library, configured with AES in CBC mode.
The content is encoded as UTF-8 and padded using PKCS7 to ensure it meets the AES block size requirements.
The padded content is then encrypted using the derived key and IV.

#### Decryption Algorithm

The decryption process reverses the encryption steps to recover the original content. (`Client.__decrypt_content() -> str`)
It requires the encrypted content, original key, IV, and salt used during encryption.

##### Decryption Process

The decryption function reconstructs the encryption parameters using the provided key, IV, and salt.
It performs the same key derivation process as encryption to obtain the identical key.
The encrypted content is then decrypted using AES-CBC, unpadded using PKCS7, and decoded from UTF-8 to recover the original string.

#### Security Considerations

The implementation incorporates several security measures:
- Cryptographically secure random number generation for salt and IV
- HKDF key derivation to strengthen the input key
- Proper block cipher padding using PKCS7
- CBC mode operation to prevent pattern analysis

<ins>***Note***</ins>: It is perfectly secure to send the IV and salt alongside the ciphertext, as they are not considered secret information.
The real secret information lies in the key, which is never transmitted over the network.
So, this doesn't compromise the security of the encryption process and/or the obliviousness of the server to the content.

#### Credits

Cîrstian Daniel, Goidescu Rareș-Ștefan, Macovei Nicolae-Cristian

## Server Side

### Functionality

The server is used as a central node that redirects messages and chat invites from one user to the desired target user.
Therefore, the server **is not able to decrypt the messages** sent by the clients, its sole purpose is to forward them to the destination.
It is implemented using `Raw TCP Sockets` and uses `JSON` for communicating with the clients.

Here is a diagram of the requests the server is able to handle:
[server.png](https://static.cristimacovei.dev/drawio-server.png)

### Client Connect / Disconnect and the server socket map

We use a dictionary to map the client's username to its respective socket. This allows us to easily send messages to a specific client by looking up the socket associated with the username.

To do this, we wrote a wrapper class `GenericMap` that provides a generic way to map keys to values.
The class provides methods to add, remove, and get values associated with keys.

We then used this class to create a mapping of usernames to sockets (`client_id: int -> socket: socket.socket`) to be able to quickly retrieve the socket of a specific target user and forward a message to them.
This map is also used to check whether a given user is connected to the server right now, which helps, for example, when a user is trying to join a chat room with someone who is not online.

(<ins>*Note*</ins>: This was also tested in the `tests/test_client_socket_map.py` script using the `unittest` module)

The `client connected` and `client disconnected` events are received on the listener socket and are handled on the server by adding or removing an entry from the map.
For every `client connected` event, a `thread` is started to handle that client's requests.

### Event queue

The Event queue is a data structure used by the server to keep track of queued "notifications" that it's supposed to send to each user when they request updates.

The two main types of events that are stored in the queue are:
- `EVT_NEW_MESSAGE`: a new message is ready for this user
- `EVT_NEW_REQUEST`: a chat invite has been received for this user

Internally, it is implemented as a `map` of `queues`, storing a queue for each user.

### Sending updates

When a user sends a `get updates` request, all events stored in their queue will be sent via their socket and removed from the queue.

### Account Login / Account Create requests

When the user first connects, they are asked to provide username and password credentials, which are used to authenticate them in the [`database`](#database).

The server then responds via the same socket with a `JSON` response containing `status`, which is either `success` or `failure` and a list of friends, that the client will store locally in order to quickly select who to chat with.

### Inviting another user to a chat room

When user `A` wants to talk to user `B`, it first sends a request to the server to invite `B` to a chat room.

Using the `socket map`, the server checks if user `B` is online.
If they are online, the server queues an `EVT_NEW_REQUEST` update for user `B` and starts a 30-second timer for user `B` to accept the invite, otherwise, the server sends an error response to user `A`.
If user `B` rejects or accepts the invitation (ie. sends a `REQ_CHAT_INV_ACCEPT` or a `REQ_CHAT_INV_REJECT` request), the timer is stopped and a corresponding message is sent back to user `A`.
If `B` fails to accept in the 30-second window, an error response is sent to user `A` and the chat doesn't start. 

### Diffie-Hellmann Key Exchange Events

The server is **completely oblivious** to the key exchange, it just redirects any Diffie-Hellmann-related message to its target. 
While it is able to read the public shared data between the two clients (ie. `mod` and `base`), it is not able to compute the secret key.

### Credits

Macovei Nicolae-Cristian, Goidescu Rareș-Ștefan

## Database

The server sets up a simple database using SQLite3 to manage its users and their previous connections.
The database supports basic operations like adding, verifying, and deleting users, as well as managing connections between them.

The database has two tables:
- `users`: Contains id (unique identifier), username (must be unique), and password (hashed).
- `connections`:
    1. Stores pairs of connected users with `user1_id` and `user2_id`, ensuring no duplicates and referencing the users table.
    2. The pairs are saved as `user1_id`, `user2_id` if `user1_id` is lower than `user2_id`, and `user2_id`, `user1_id` if `user2_id` is lower than `user1_id`.

### Main Functionalities

- User Management
	- Add User (`add_user`): Adds a new user to the database with a username and hashed password. Returns the new user's ID or -1 if the username is already taken.
	- Delete User (`delete_user`): Deletes a user if the username and password match what's in the database.
	- Verify User (`verify_user`): Checks if the username and password are correct and returns the user ID if valid, or -1 otherwise.
	- Get User ID (`get_uid`): Finds the ID of a user based on their username.
- Connection Management
	- Add Connection (`add_connection`): Links two users together. It always stores connections as (smaller_id, larger_id) to maintain consistency.
	- Find Connection (`find_connection`): Checks if two users are connected.
	- Remove Connection (`remove_connection`): Deletes the link between two users.
	- List Friends (`list_friends`): Gets all usernames connected to a specific user.
- Password Security
	- Password Hashing (`_hash_password`): Uses SHA-256 to hash passwords before storing them in the database.
	Plain text passwords = big no-no.

### How it works

- Initializing the database
	- When the Database class is initialized, it creates two tables:
		- *users*: Stores user info (ID, username, hashed password).
		- *connections*: Keeps track of user connections, ensuring no duplicates.
- Simplicity and Error Handling
	- All user-related and connection-related actions are straightforward SQL commands wrapped in Python methods.
	This also ensures modularity.
	- The app handles errors (like duplicate usernames) gracefully and provides clear outputs.

### Testing the database

We tested the user management features using the `src/server/database/main.py` script, where we set up a basic menu to add and delete users.
For connection management, we tested it with the `src/server/database/test.py` script, where we created a simple menu for adding and deleting connections.

We also tested the successful running of the 2 scripts with `sqlitebrowser`, for example we added 3 users with the following usernames and passwords:
- `dani`   -> `1234`
- `rares`  -> `12345`
- `cristi` -> `123456`

This is the result:

<img src="https://static.cristimacovei.dev/test-database.png" alt="users.db" width="700"/>

The IDs should theoretically increase by 1 since the ID field has the autoincrement property.
However, in this demo, `ID = 2` is followed by 5 and 6 because we had previously deleted and added users.

If the credentials are correct and the authentication is successful, the server also queries the database to find a list of "friends", i.e. other users that this user has chatted with before.

### Credits

Cîrstian Daniel, Macovei Nicolae-Cristian

## Interface (CLI)

The interface provides user authentication, chat management, and message exchange functionality through an interactive console interface.

### Configuration

The application uses a global logging level configuration that can be set at startup:
- Level 0: No logs
- Level 1: Error logs only
- Level 2: All logs (verbose)

### Authentication

The interface provides two authentication options:
- Login with existing credentials
- Account creation

Both flows collect username and password inputs, with account creation requiring password confirmation.
Password input is secured using the `getpass` module to prevent **shoulder surfing**.

### Main Interface Loop

The interface presents three main options:
- Start a chat
- Refresh updates
- Exit application

### Chat Initialization

When starting a chat, the system provides two paths:
- Direct chat start with specified username
- Quick selection from previous connections list

The chat initialization process includes:
- Key exchange protocol
- Chat invitation handling
- Connection establishment verification

Command options:
`/r`: Refresh messages (request updates)
`/b`: Return to main menu

### Error Handling

The interface implements input validation and error handling for:
- Input validation
- Connection failures
- Invalid username/password combinations
- Failed chat initiations

### Platform Compatibility

The implementation includes cross-platform support for screen clearing operations, detecting the operating system type to use appropriate clear screen commands (`clear` for Unix-like systems, `cls` for Windows). XD

### Credits

Cîrstian Daniel, Goidescu Rareș-Ștefan

## Problems encountered along the way

#### Blocking Operations

- `socket.recv()` and `input()` are blocking operations so we can't update the interface while one of these is waiting for data

#### Shortcomings

- users have to refresh the chat room to get messages sent by others
- users have to refresh the main menu to get chat invites
- users have to type special (`/b` and `/r`) commands to exit and refresh

#### Our Next Steps

- We plan to use multithreading in the client interface by having the main thread render the UI and another thread to handle these blocking operations
- We also plan to create another client interface, based on GUI instead of CLI

## Contributors

- [CristiMacovei](https://github.com/CristiMacovei)
- [raresgoidescu](https://github.com/raresgoidescu)
- [DaniGM32](https://github.com/DaniGM32)
