"""Testing samples"""

from binascii import unhexlify

# pubkey K
sample_pubkey = unhexlify(
    '0409d4e5c0ab3d25fe048c64c9da1a242c7f19417e9517cd266950d72c755713585c6178e9'
    '7fe092fc897c9a1f1720d5770ae8eaad2fa8fcbd08e9324a5dde1857'
)

sample_iv = unhexlify(
    'bddb7c2829b08038'
    '753084a2f3991681'
)

# Private key r
sample_ephem_privkey = unhexlify(
    '5be6facd941b76e9'
    'd3ead03029fbdb6b'
    '6e0809293f7fb197'
    'd0c51f84e96b8ba4'
)
# Public key R
sample_ephem_pubkey = unhexlify(
    '040293213dcf1388b61c2ae5cf80fee6ffffc049a2f9fe7365fe3867813ca81292df94686c'
    '6afb565ac6149b153d61b3b287ee2c7f997c14238796c12b43a3865a'
)

# First 32 bytes of H called key_e
sample_enkey = unhexlify(
    '1705438282678671'
    '05263d4828efff82'
    'd9d59cbf08743b69'
    '6bcc5d69fa1897b4'
)

# I could not found padding in the code ):
sample_data = b'The quick brown fox jumps over the lazy dog.'

sample_ciphertext = unhexlify(
    '64203d5b24688e25'
    '47bba345fa139a5a'
    '1d962220d4d48a0c'
    'f3b1572c0d95b616'
    '43a6f9a0d75af7ea'
    'cc1bd957147bf723'
)
