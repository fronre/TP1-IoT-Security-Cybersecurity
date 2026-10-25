from tp1_bls.bls_core import aggregate, aggregate_verify, keygen_from_seed, sign, sk_to_pk, verify


def test_valid_signature_and_key_pair():
    sk_a = keygen_from_seed(b"sensor-a-seed")
    pk_a = sk_to_pk(sk_a)
    msg = b"temperature=22.5C"
    sig = sign(sk_a, msg)

    assert verify(pk_a, msg, sig) is True


def test_tampered_message_is_rejected():
    sk = keygen_from_seed(b"sensor-b-seed")
    pk = sk_to_pk(sk)
    msg = b"humidity=48%"
    sig = sign(sk, msg)

    assert verify(pk, b"humidity=49%", sig) is False


def test_aggregate_signature_verifies():
    sk1 = keygen_from_seed(b"sensor-1")
    sk2 = keygen_from_seed(b"sensor-2")
    pk1 = sk_to_pk(sk1)
    pk2 = sk_to_pk(sk2)

    msg1 = b"sensor-1: 20.0"
    msg2 = b"sensor-2: 21.5"
    sig1 = sign(sk1, msg1)
    sig2 = sign(sk2, msg2)

    agg = aggregate([sig1, sig2])
    assert aggregate_verify([pk1, pk2], [msg1, msg2], agg) is True
