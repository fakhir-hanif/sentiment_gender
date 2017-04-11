HOST="http://ec2-54-xxxx.us-west-2.compute.amazonaws.com"
PORT=5000
STATS_KEY="sentiment_stats"
RHOST=''
RPORT=6379
RPASS=None
API_KEY = '1e4492805fad2db6b7b49f641ddf5c0b'
LOG_FILE = 'sentiment.log'
#  Yandex API-KEY for translation
TRANS_KEY = 'trnsl.1.1.20161122T053411Z.55a53e108a1a0f2d.4813918421a30324df363c83accac1189d73032c'
TRANS_KEY2 = 'trnsl.1.1.20161124T102639Z.c126dc6702266cf2.11f4cdffc302f6e62d1c93fa67ce95f90cd9323f'
NEG_WORDS = [
    'shame', 'corruption', 'theft', 'corrupt', 'thief', 'oblivious', 'fraud', 'criminal', 'pathetic',
    'crupt', 'bloody', 'maderchod', 'chutiya', 'bastard', 'bitch', 'saala kutta', 'kamina', 'kaminy', 'kamino',
    'bhen ke takke', 'bhonsri', 'bhadwe', 'khotey ki aulda', 'ullu ke pathe', "loot", "looto", "loots", "looted",
    "looters", "looting", 'criminals', 'against @kelectricpk', 'against you @kelectricpk', 'fucker', 'fuck', 'fucking',
    "haramkhor", "against the ke", 'lies', 'lie',
]

NEG_SUB_WORDS = [
    'shame', 'corruption', 'theft', 'corrupt', 'thief', 'oblivious', 'fraud', 'criminal', 'pathetic',
    'crupt', 'bloody', 'maderchod', 'chutiya', 'bastard', 'bitch', 'saala kutta', 'kamina', 'kaminy', 'kamino',
    'bhen ke takke', 'bhonsri', 'bhadwe', 'khotey ki aulda', 'ullu ke pathe', "loot", "looto", "loots", "looted",
    "looters", "looting", 'criminals', 'against @kelectricpk', 'against you @kelectricpk', 'fucker', 'fuck', 'fucking',
    "haramkhor", "against the ke",
]