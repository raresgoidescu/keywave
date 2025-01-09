To make the import work, run `source setup.sh` in the root dir of the project.

## Client Side

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

### Interface (CLI)

The interface provides user authentication, chat management, and message exchange functionality through an interactive console interface.

#### Configuration

The application uses a global logging level configuration that can be set at startup:
- Level 0: No logs
- Level 1: Error logs only
- Level 2: All logs (verbose)

#### Authentication

The interface provides two authentication options:
- Login with existing credentials
- Account creation

Both flows collect username and password inputs, with account creation requiring password confirmation.
Password input is secured using the getpass module to prevent **shoulder surfing**.

#### Main Interface Loop

The interface presents three main options:
- Start a chat
- Refresh updates
- Exit application

#### Chat Initialization

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

#### Error Handling

The interface implements input validation and error handling for:
- Input validation
- Connection failures
- Invalid username/password combinations
- Failed chat initiations

#### Platform Compatibility

The implementation includes cross-platform support for screen clearing operations, detecting the operating system type to use appropriate clear screen commands (`clear` for Unix-like systems, `cls` for Windows). XD