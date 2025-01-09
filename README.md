# KeyWave Chat Application

## Table of Contents

- [Introduction](#introduction)
- [How to install?](#how-to-install)
- [How to use?](#how-to-use)
- [Client Side](#client-side)
	- [Diffie-Hellman Key Exchange Protocol](#diffie-hellman-key-exchange-protocol)
    - [Encryption / Decryption](#encryption--decryption)
- [Server Side](#server-side)
    - [Functionality](#functionality)
    - [Client Connect / Disconnect and the server socket map](#client-connect--disconnect-and-the-server-socket-map)
    - [Event queue](#event-queue)
    - [Sending updates](#sending-updates)
    - [Account Login / Account Create requests](#account-login--account-create-requests)
    - [Inviting another user to a chat room](#inviting-another-user-to-a-chat-room)
    - [Diffie-Hellmann Key Exchange Events](#diffie-hellmann-key-exchange-events)
- [Interface (CLI)](#interface-cli)
    - [Configuration](#configuration)
    - [Authentication](#authentication)
    - [Main Interface Loop](#main-interface-loop)
    - [Chat Initialization](#chat-initialization)
    - [Error Handling](#error-handling)
    - [Platform Compatibility](#platform-compatibility)

<ins>***NOTE***</ins>: To make the imports work, run `source setup.sh` in the root dir of the project.

## How to install?

## How to use?

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

## Server Side

### Functionality

The server is used as a central node that redirects messages and chat invites from one user to the desired target user.
Therefore, the server **is not able to decrypt the messages** sent by the clients, its sole purpose is to forward them to the destination.
It is implemented using `Raw TCP Sockets` and uses `JSON` for communicating with the clients.

Here is a diagram of the requests the server is able to handle:
[server.png](https://static.cristimacovei.dev/drawio-server.png)

### Client Connect / Disconnect and the server socket map

The server uses a `map` to store `client_id -> client_socket` records, to be able to quickly retrieve the socket of a specific target user and forward a message to them.
This map is also used to check whether a given user is connected to the server right now, which helps, for example, when a user is trying to join a chat room with someone who is not online.

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

When the user first connects, they are asked to provide username and password credentials, which are used to authenticate them in the `database`.

### TODO baga partea lu dani aici

If the credentials are correct and the authentication is successful, the server also queries the database to find a list of "friends", ie. other users that this user has chatted with before.

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
Password input is secured using the getpass module to prevent **shoulder surfing**.

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