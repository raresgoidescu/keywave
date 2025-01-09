To make the import work, run `source setup.sh` in the root dir of the project.

## Diffie-Hellman Key Exchange Protocol

Our chat application uses this protocol to establish a secret key between two users. This protocol is based on five exchanges, explained quickly in this diagram: [drawio](https://static.cristimacovei.dev/drawio-key-exchange.png)

Assume the key exchange happens between two users `Alice` and `Bob`, and `Alice` is the one that initiates the exchange.

### I. Sharing public data
- `Alice` chooses two integers `mod` and `base`, and sends them to `Bob`

### II. Confirmation of public data
- `Bob` sends the public data back to `Alice` to confirm it has been received properly and they share the same values

### III. Key Sharing (Alice's side)
- `Alice` chooses her secret key `a` (an integer), computes the value `A` = `base ^ a % mod` and sends it to `Bob`.

### IV. Key Sharing (Bob's side)
- `Bob` receives `Alice`'s key `A`, and does the same process: chooses his secret key `b`, computes `B` = `base ^ b % mod` and sends it to alice.

### V. Shared Secret
- `Alice` can now compute `key` = `a ^ B % mod`
- `Bob` can now compute `key` = `b ^ A % mod`
- both keys are equal to `base ^ (a * b) % mod`

### Security

Although an eavesdropper can capture `mod` and `base`, and even both values of `A` and `B`, it is unable to compute the secret key. 

Computing `A * B` is useless since it would equal `base ^ (a + b) % mod`.

## Server 

#### Written by Nicolae-Cristian MACOVEI and Rares-Stefan GOIDESCU

### Functionality

The `server` is used as a central node that redirects messages and chat invites from one user to the desired target user. Therefore, the server **is not able to decrypt the messages** sent by the clients, its sole purpose is to forward them to the destination. It is implemented using `Raw TCP Sockets` and uses `JSON` for communicating with the clients.

Here is a diagram of the requests the server is able to handle:
[server.png](https://static.cristimacovei.dev/drawio-server.png)

### Client connect / disconnect and the server socket map

The server uses a `map` to store `client_id -> client_socket` records, to be able to quickly retrieve the socket of a specific target user and forward a message to them. This map is also used to check whether a given user is connected to the server right now, which helps, for example, when a user is trying to join a chat room with someone who is not online.

The `client connected` and `client disconnected` events are received on the listener socket and are handled on the server by adding or removing an entry from the map. For every `client connected` event, a `thread` is started to handle that client's requests.

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

When user `A` wants to talk to user `B`, it first sends a request to the server to invite `B` to a 
chat room.

Using the `socket map`, the server checks if user `B` is online. If they are online, the server queues an `EVT_NEW_REQUEST` update for user `B` and starts a 30-second timer for user `B` to accept the invite, otherwise, the server sends an error response to user `A`. If user `B` rejects or accepts the invitation (ie. sends a `REQ_CHAT_INV_ACCEPT` or a `REQ_CHAT_INV_REJECT` request), the timer is stopped and a corresponding message is sent back to user `A`. If `B` fails to accept in the 30-second window, an error response is sent to user `A` and the chat doesn't start. 

### Diffie-Hellmann Key Exchange Events

The server is **completely oblivious** to the key exchange, it just redirects any diffie-hellmann-related message to its target. While it is able to read the public shared data between the two clients (ie. `mod` and `base`), it is not able to compute the secret key.
