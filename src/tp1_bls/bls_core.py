from __future__ import annotations

from collections.abc import Sequence

from py_ecc.bls.ciphersuites import G2ProofOfPossession


def keygen_from_seed(seed: bytes, key_info: bytes = b"") -> int:
    """Generate a secret key from a deterministic byte seed."""
    if not isinstance(seed, (bytes, bytearray)):
        raise TypeError("seed must be bytes-like")
    return G2ProofOfPossession.KeyGen(bytes(seed), key_info)


def sk_to_pk(sk: int) -> bytes:
    """Derive the public key from a secret key."""
    if not isinstance(sk, int):
        raise TypeError("secret key must be an integer")
    return G2ProofOfPossession.SkToPk(sk)


def validate_public_key(pk: bytes) -> bool:
    """Validate a BLS public key using the standard subgroup check."""
    if not isinstance(pk, (bytes, bytearray)):
        return False
    return G2ProofOfPossession.KeyValidate(bytes(pk))


def sign(sk: int, message: bytes) -> bytes:
    """Return a BLS signature for a message."""
    if not isinstance(sk, int):
        raise TypeError("secret key must be an integer")
    if not isinstance(message, (bytes, bytearray)):
        raise TypeError("message must be bytes-like")
    return G2ProofOfPossession.Sign(sk, bytes(message))


def verify(pk: bytes, message: bytes, signature: bytes) -> bool:
    """Validate one message/signature pair."""
    if not isinstance(pk, (bytes, bytearray)):
        return False
    if not isinstance(message, (bytes, bytearray)):
        return False
    if not isinstance(signature, (bytes, bytearray)):
        return False
    return G2ProofOfPossession.Verify(bytes(pk), bytes(message), bytes(signature))


def aggregate(signatures: Sequence[bytes]) -> bytes:
    """Aggregate multiple BLS signatures."""
    if not isinstance(signatures, Sequence) or len(signatures) == 0:
        raise ValueError("at least one signature is required")
    normalized = [bytes(sig) for sig in signatures]
    return G2ProofOfPossession.Aggregate(normalized)


def aggregate_verify(pks: Sequence[bytes], messages: Sequence[bytes], sig: bytes) -> bool:
    """Validate an aggregate signature over multiple key/message pairs."""
    if not isinstance(pks, Sequence) or not isinstance(messages, Sequence):
        return False
    if len(pks) != len(messages) or len(pks) == 0:
        return False
    if not isinstance(sig, (bytes, bytearray)):
        return False

    normalized_pks = []
    for pk in pks:
        if not isinstance(pk, (bytes, bytearray)):
            return False
        pk_bytes = bytes(pk)
        if not validate_public_key(pk_bytes):
            return False
        normalized_pks.append(pk_bytes)

    normalized_messages = []
    for message in messages:
        if not isinstance(message, (bytes, bytearray)):
            return False
        normalized_messages.append(bytes(message))

    return G2ProofOfPossession.AggregateVerify(normalized_pks, normalized_messages, bytes(sig))
