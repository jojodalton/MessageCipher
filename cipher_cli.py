"""Interactive CLI for the message cipher module."""

from message_cipher import encode, decode
from version import VERSION, BUILD_TIMESTAMP


def main():
    print(f"Version: {VERSION}")
    print(f"Build: {BUILD_TIMESTAMP}")
    print("=== Message Cipher - Interactive Mode ===")
    print("Commands: encode, decode, quit")
    print("(Input must be printable ASCII characters only)\n")

    while True:
        command = input("Action (encode/decode/quit): ").strip().lower()

        if command in ("quit", "q", "exit"):
            print("Bye!")
            break
        elif command in ("encode", "e"):
            key = input("  Key: ")
            message = input("  Message: ")
            try:
                result = encode(key, message)
                print(f"  Ciphertext: {result}\n")
            except (TypeError, ValueError) as err:
                print(f"  Error: {err}\n")
        elif command in ("decode", "d"):
            key = input("  Key: ")
            ciphertext = input("  Ciphertext: ")
            try:
                result = decode(key, ciphertext)
                print(f"  Plaintext: {result}\n")
            except (TypeError, ValueError) as err:
                print(f"  Error: {err}\n")
        else:
            print("  Unknown command. Use encode, decode, or quit.\n")


if __name__ == "__main__":
    main()
