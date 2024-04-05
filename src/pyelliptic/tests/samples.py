"""Testing samples"""

from binascii import unhexlify


# These keys are from addresses test script
sample_pubsigningkey = (
    b'044a367f049ec16cb6b6118eb734a9962d10b8db59c890cd08f210c43ff08bdf09d'
    b'16f502ca26cd0713f38988a1237f1fc8fa07b15653c996dc4013af6d15505ce')
sample_pubencryptionkey = (
    b'044597d59177fc1d89555d38915f581b5ff2286b39d022ca0283d2bdd5c36be5d3c'
    b'e7b9b97792327851a562752e4b79475d1f51f5a71352482b241227f45ed36a9')
sample_privsigningkey = \
    b'93d0b61371a54b53df143b954035d612f8efa8a3ed1cf842c2186bfd8f876665'
sample_privencryptionkey = \
    b'4b0b73a54e19b059dc274ab69df095fe699f43b17397bca26fdf40f4d7400a3a'

# [chan] bitmessage
sample_privsigningkey_wif = \
    b'5K42shDERM5g7Kbi3JT5vsAWpXMqRhWZpX835M2pdSoqQQpJMYm'
sample_privencryptionkey_wif = \
    b'5HwugVWm31gnxtoYcvcK7oywH2ezYTh6Y4tzRxsndAeMi6NHqpA'
sample_wif_privsigningkey = \
    b'a2e8b841a531c1c558ee0680c396789c7a2ea3ac4795ae3f000caf9fe367d144'
sample_wif_privencryptionkey = \
    b'114ec0e2dca24a826a0eed064b0405b0ac148abc3b1d52729697f4d7b873fdc6'

sample_factor = \
    66858749573256452658262553961707680376751171096153613379801854825275240965733
# G * sample_factor
sample_point = (
    33567437183004486938355437500683826356288335339807546987348409590129959362313,
    94730058721143827257669456336351159718085716196507891067256111928318063085006
)

sample_deterministic_addr3 = b'2DBPTgeSawWYZceFD69AbDT5q4iUWtj1ZN'
sample_deterministic_addr4 = b'2cWzSnwjJ7yRP3nLEWUV5LisTZyREWSzUK'
sample_daddr3_512 = 18875720106589866286514488037355423395410802084648916523381
sample_daddr4_512 = 25152821841976547050350277460563089811513157529113201589004


# pubkey K
sample_pubkey = unhexlify(
    '0409d4e5c0ab3d25fe'
    '048c64c9da1a242c'
    '7f19417e9517cd26'
    '6950d72c75571358'
    '5c6178e97fe092fc'
    '897c9a1f1720d577'
    '0ae8eaad2fa8fcbd'
    '08e9324a5dde1857'
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
    '040293213dcf1388b6'
    '1c2ae5cf80fee6ff'
    'ffc049a2f9fe7365'
    'fe3867813ca81292'
    'df94686c6afb565a'
    'c6149b153d61b3b2'
    '87ee2c7f997c1423'
    '8796c12b43a3865a'
)

# First 32 bytes of H called key_e
sample_enkey = unhexlify(
    '1705438282678671'
    '05263d4828efff82'
    'd9d59cbf08743b69'
    '6bcc5d69fa1897b4'
)

# Last 32 bytes of H called key_m
sample_mackey = unhexlify(
    'f83f1e9cc5d6b844'
    '8d39dc6a9d5f5b7f'
    '460e4a78e9286ee8'
    'd91ce1660a53eacd'
)

# No padding of input!
sample_data = b'The quick brown fox jumps over the lazy dog.'

sample_ciphertext = unhexlify(
    '64203d5b24688e25'
    '47bba345fa139a5a'
    '1d962220d4d48a0c'
    'f3b1572c0d95b616'
    '43a6f9a0d75af7ea'
    'cc1bd957147bf723'
)

sample_mac = unhexlify(
    'f2526d61b4851fb2'
    '3409863826fd2061'
    '65edc021368c7946'
    '571cead69046e619'
)
