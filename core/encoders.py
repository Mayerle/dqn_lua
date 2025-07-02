import torch

joker_names = [
    "8 Ball",
    "Abstract Joker",
    "Acrobat",
    "Ancient Joker",
    "Arrowhead",
    "Astronomer",
    "Banner",
    "Baron",
    "Baseball Card",
    "Blackboard",
    "Bloodstone",
    "Blue Joker",
    "Blueprint",
    "Bootstraps",
    "Brainstorm",
    "Bull",
    "Burglar",
    "Burnt Joker",
    "Business Card",
    "Canio",
    "Campfire",
    "Card Sharp",
    "Cartomancer",
    "Castle",
    "Cavendish",
    "Ceremonial Dagger",
    "Certificate",
    "Chaos the Clown",
    "Chicot",
    "Clever Joker",
    "Cloud 9",
    "Constellation",
    "Crafty Joker",
    "Crazy Joker",
    "Credit Card",
    "Delayed Gratification",
    "Devious Joker",
    "Diet Cola",
    "DNA",
    "Driver's License",
    "Droll Joker",
    "Drunkard",
    "The Duo",
    "Dusk",
    "Egg",
    "Erosion",
    "Even Steven",
    "Faceless Joker",
    "The Family",
    "Fibonacci",
    "Flash Card",
    "Flower Pot",
    "Fortune Teller",
    "Four Fingers",
    "Gift Card",
    "Glass Joker",
    "Gluttonous Joker",
    "Golden Joker",
    "Greedy Joker",
    "Green Joker",
    "Gros Michel",
    "Hack",
    "Half Joker",
    "Hallucination",
    "Hanging Chad",
    "Hiker",
    "Hit the Road",
    "Hologram",
    "Ice Cream",
    "The Idol",
    "Invisible Joker",
    "Joker",
    "Jolly Joker",
    "Juggler",
    "Loyalty Card",
    "Luchador",
    "Lucky Cat",
    "Lusty Joker",
    "Mad Joker",
    "Madness",
    "Mail-In Rebate",
    "Marble Joker",
    "Matador",
    "Merry Andy",
    "Midas Mask",
    "Mime",
    "Misprint",
    "Mr. Bones",
    "Mystic Summit",
    "Obelisk",
    "Odd Todd",
    "Onyx Agate",
    "Oops! All 6s",
    "The Order",
    "Pareidolia",
    "Perkeo",
    "Photograph",
    "Popcorn",
    "Raised Fist",
    "Ramen",
    "Red Card",
    "Reserved Parking",
    "Ride the Bus",
    "Riff-Raff",
    "Riff-raff",
    "Showman",
    "Rocket",
    "Rough Gem",
    "Runner",
    "Satellite",
    "Scary Face",
    "Scholar",
    "Seance",
    "Seeing Double",
    "Seltzer",
    "Shoot the Moon",
    "Shortcut",
    "Sixth Sense",
    "Sly Joker",
    "Smeared Joker",
    "Smiley Face",
    "Sock and Buskin",
    "Space Joker",
    "Splash",
    "Square Joker",
    "Steel Joker",
    "Joker Stencil",
    "Stone Joker",
    "Stuntman",
    "Supernova",
    "Superposition",
    "Swashbuckler",
    "Throwback",
    "Golden Ticket",
    "To the Moon",
    "To Do List",
    "Trading Card",
    "The Tribe",
    "Triboulet",
    "The Trio",
    "Troubadour",
    "Spare Trousers",
    "Turtle Bean",
    "Vagabond",
    "Vampire",
    "Walkie Talkie",
    "Wee Joker",
    "Wily Joker",
    "Wrathful Joker",
    "Yorick",
    "Zany Joker"
]

vouchers_names = [
    "Antimatter",
    "Blank",
    "Clearance Sale",
    "Crystal Ball",
    "Director's Cut",
    "Glow Up",
    "Grabber",
    "Hieroglyph",
    "Hone",
    "Illusion",
    "Liquidation",
    "Magic Trick",
    "Money Tree",
    "Nacho Tong",
    "Observatory",
    "Omen Globe",
    "Overstock",
    "Overstock Plus",
    "Paint Brush",
    "Palette",
    "Petroglyph",
    "Planet Merchant",
    "Planet Tycoon",
    "Recyclomancy",
    "Reroll Glut",
    "Reroll Surplus",
    "Retcon",
    "Seed Money",
    "Tarot Merchant",
    "Tarot Tycoon",
    "Telescope",
    "Wasteful"

]
suits = ["Hearts","Diamonds","Spades","Clubs"]

effects = ["Base","Bonus Card","Glass Card","Gold Card",
               "Lucky Card","Mult Card","Steel Card",
               "Stone Card","Wild Card"
               ]


def encode_joker(joker):
    if(joker == None):
        return [-1, -1]
    return [joker_names.index(joker["ability"]), joker["cost"]]

def encode_card(card):
    if(card == None):
        return [-1, -1]
    
    return [card["id"], suits.index(card["suit"])] #, effects.index(card["effect"])


def encode_shop(shop):
    shop_data = []

    if(len(shop) == 0):
        shop_data = [[-1,-1] for _ in range(5)]
        return shop_data
    else:
    
        if(len(shop["vouchers"]) > 0):
            voucher = shop["vouchers"][0]
            shop_data.append([vouchers_names.index(voucher["ability"]), voucher["cost"]])
        else:
            shop_data.append([-1,-1])

        cards = shop["cards"]

        for card in cards:
            if(card["type"] == "Joker"):
                shop_data.append(encode_joker(card))
            else:
                shop_data.append(encode_joker(None))

        for _ in range(5-len(shop_data)):
            shop_data.append(encode_joker(None))
        return shop_data


def encode_game(G, selected, device = "cuda"):
    if(len(G) == 0):
        return torch.tensor([-1 for _ in range(24)], device = device, dtype=torch.float)
    # jokers = G["jokers"][:5]
    # jokers_data = []
    # for i in range(len(jokers)):
    #     jkr_data = encode_joker(jokers[i])
    #     jokers_data.append(jkr_data)

    # for i in range(5-len(jokers_data)):
    #     jokers_data.append(encode_joker(None))


    hand_data = []
    if(len(G["hand"]) == 0):
        hand_data = [encode_card(None) for _ in range(8)]
    else:
        hand = G["hand"][:8]
        for i in range(len(hand)):
            card_data = encode_card(hand[i])
            hand_data.append(card_data)

        for i in range(8-len(hand_data)):
            hand_data.append(encode_card(None))



    # general_data = [G["game"]["dollars"],G["game"]["round"], G["game"]["chips"], G["current_round"]["hands_left"], G["current_round"]["discards_left"]]
    # shop_data = encode_shop(G["shop"])
    
    
    selected_vector = []
    for i in range(1,9):
        if(i in selected):
            selected_vector.append(1)
        else:
            selected_vector.append(0)



    data_vector = []
    #for d in jokers_data:
    #    data_vector.extend(d) # 5*2 = 16
    for d in hand_data:
        data_vector.extend(d) # 8*2 =16
    #for d in shop_data:
    #    data_vector.extend(d) # 4*2+2 =10
    #data_vector.extend(general_data)  #2 
    data_vector.extend(selected_vector) # 8

    

    return torch.tensor(data_vector, device = device,dtype=torch.float)