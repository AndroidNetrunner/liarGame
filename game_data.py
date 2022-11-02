class game_data:
    def __init__(self):
        self.members = []
        self.already = set()
        self.round = 3
        self.hints = {}
        self.words = open("word_list.txt", 'r', encoding='UTF-8').read().split('\n')
        self.liar = None
        self.main_channel = None
        self.guess = None
        self.start = False
        self.vote_time = False
        self.starter = None
        self.word = None
        self.current_round = 0
        self.vote = {}
        self.vote_message = {}
  
        self.emojis = {
        "0\u20E3" : None,
        "1\u20E3" : None,
        "2\u20E3" : None,
        "3\u20E3" : None,
        "4\u20E3" : None,
        "5\u20E3" : None,
        "6\u20E3" : None,
        "7\u20E3" : None,
        "8\u20E3" : None,
        "9\u20E3" : None
        }

        
active_game = {}