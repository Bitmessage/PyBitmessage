"""Various sample data"""

from binascii import unhexlify


magic = 0xE9BEB4D9

# These keys are from addresses test script
sample_pubsigningkey = unhexlify(
    '044a367f049ec16cb6b6118eb734a9962d10b8db59c890cd08f210c43ff08bdf09d'
    '16f502ca26cd0713f38988a1237f1fc8fa07b15653c996dc4013af6d15505ce')
sample_pubencryptionkey = unhexlify(
    '044597d59177fc1d89555d38915f581b5ff2286b39d022ca0283d2bdd5c36be5d3c'
    'e7b9b97792327851a562752e4b79475d1f51f5a71352482b241227f45ed36a9')
sample_privsigningkey = \
    b'93d0b61371a54b53df143b954035d612f8efa8a3ed1cf842c2186bfd8f876665'
sample_privencryptionkey = \
    b'4b0b73a54e19b059dc274ab69df095fe699f43b17397bca26fdf40f4d7400a3a'

sample_ripe = b'003cd097eb7f35c87b5dc8b4538c22cb55312a9f'
# stream: 1, version: 2
sample_address = 'BM-onkVu1KKL2UaUss5Upg9vXmqd3esTmV79'

sample_factor = 66858749573256452658262553961707680376751171096153613379801854825275240965733
# G * sample_factor
sample_point = (
    33567437183004486938355437500683826356288335339807546987348409590129959362313,
    94730058721143827257669456336351159718085716196507891067256111928318063085006
)

sample_seed = 'TIGER, tiger, burning bright. In the forests of the night'
# Deterministic addresses with stream 1 and versions 3, 4
sample_deterministic_ripe = b'00cfb69416ae76f68a81c459de4e13460c7d17eb'
sample_deterministic_addr3 = 'BM-2DBPTgeSawWYZceFD69AbDT5q4iUWtj1ZN'
sample_deterministic_addr4 = 'BM-2cWzSnwjJ7yRP3nLEWUV5LisTZyREWSzUK'
sample_daddr3_512 = 18875720106589866286514488037355423395410802084648916523381
sample_daddr4_512 = 25152821841976547050350277460563089811513157529113201589004

sample_statusbar_msg = "new status bar message"
sample_inbox_msg_ids = ['27e644765a3e4b2e973ee7ccf958ea20', '51fc5531-3989-4d69-bbb5-68d64b756f5b',
                        '2c975c515f8b414db5eea60ba57ba455', 'bc1f2d8a-681c-4cc0-9a12-6067c7e1ac24']
# second address in sample_test_subscription_address is for the announcement broadcast
sample_test_subscription_address = ['BM-2cWQLCBGorT9pUGkYSuGGVr9LzE4mRnQaq', 'BM-GtovgYdgs7qXPkoYaRgrLFuFKz1SFpsw']
sample_subscription_name = 'test sub'
