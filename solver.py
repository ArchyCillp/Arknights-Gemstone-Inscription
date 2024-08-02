'''
cards 
class card:
    type (enum): notopen, empty, cred, cblue, cpur, cyel
    step (int): 1, 2, 3, 4
    level (int): 1, 2, 3
cred1, cred2, cred3, cred4
cblue1, cblue2, cblue3
cpur1, cpur2, cpur3
cyel1, cyel2, cyel3

class stone:
    type: red, blue, pur
    level: 0, 1, 2, 3
materials:
red0, red1, red2, red3, red4
blue0, blue1, blue2, blue3
pur0, pur1, pur2, pur3
yel0

specialEffects:
1. cred123: work outside of hand
2. cred has duplicated power, and 2.4x is ceil.
2. cred has extra credit for empty slots.
2. cblue123: generate yel1, ceil for blue, floor for yel1, yel1(max) give 1x yel1, yel2(max) and yel3(max) give 2x yel1
3. cpur is ceil 
3. cpur has extra credit only one type stone left
4. price may change


prunes:
1. If outside of hand is activated successfully, dont choose it.
2. cyel always choose the largest product.

input format:
work(slots[6] : card, init_stone_cnt[r,b,p,y], cred_deck[4] : card)
'''

from math import ceil
from math import floor


from enum import Enum
from collections import defaultdict

class CardType(Enum):
    CRED = "cred"
    CBLUE = "cblue"
    CPUR = "cpur"
    CYEL = "cyel"
    NOT_OPEN = "notopen"
    EMPTY = "empty"

def get_card_type(value):
    for card_type in CardType:
        if card_type.value == value:
            return card_type
    return None  # or raise an exception if preferred

class StoneType(Enum):
    RED = "red"
    BLUE = "blue"
    PUR = "pur"
    YEL = "yel"

class Card:
    def __init__(self, card_type: CardType, step: int):
        self.card_type = card_type
        self.step = step
        # level is record in dict

    def __str__(self):
        return f"{self.card_type.value}_{self.step}"
    
    def cn_str(self):
        step_cn = ["I","II","III","IV"]
        if self.card_type == CardType.CRED:
            print(self.card_type, self.step)
            return "红色 {}".format(step_cn[self.step-1])
        elif self.card_type == CardType.CBLUE:
            return "蓝色 {}".format(step_cn[self.step-1])
        elif self.card_type == CardType.CPUR:
            return "紫色 {}".format(step_cn[self.step-1])
        elif self.card_type == CardType.CYEL:
            return "黄色 {}".format(step_cn[self.step-1])
        elif self.card_type == CardType.NOT_OPEN:
            return "未解锁"
        elif self.card_type == CardType.EMPTY:
            return "留空"
        
class Stone:
    def __init__(self, stone_type: StoneType, level: int):
        self.stone_type = stone_type
        self.level = level

    def __str__(self):
        return f"{self.stone_type.value}_{self.level}"
    
    def price(self, pur_stone_price_add, pur_3_stone_price_add, yel_stone_price_add):
        if self.stone_type == StoneType.RED:
            prices = [1,2,10,35,85]
            return prices[self.level]
        elif self.stone_type == StoneType.PUR:
            prices = [1,3,22,105]
            return prices[self.level] + pur_stone_price_add + (pur_3_stone_price_add if self.level == 3 else 0)
        elif self.stone_type == StoneType.BLUE:
            prices = [1,5,50,500]
            return prices[self.level]
        elif self.stone_type == StoneType.YEL:
            return 1 + yel_stone_price_add
        else:
            exit(-1)


def check_prework(cred_step, cred_level):
    # TODO return true if this red card preworks
    '''
    cred1: f, t, t
    cred2: f, f, t
    cred3: f, f, t
    cred4: f, f, f
    '''
    # print("RED PRE CHECK?{} {}".format(cred_step, cred_level))
    if cred_level == 0: return False
    res_table = [
        [False, True, True],
        [False, False, True],
        [False, False, True],
        [False, False, False]
    ]
    return res_table[cred_step-1][cred_level-1]

def get_duplicate_cred_ratio(cred_step, cred_level):
    # TODO return the duplicate ratio for the red card
    '''
    cred1: 1, 1, 2
    cred2: 1, 2, 2
    cred3: 1, 2.4, 2.4
    cred4: 1, 1, 1
    '''
    # print("RED CHECK?{} {}".format(cred_step, cred_level))
    if cred_level == 0: return 0
    res_table = [
        [1, 1, 2],
        [1, 2, 2],
        [1, 2.4, 2.4],
        [1, 1, 1]
    ]
    return res_table[cred_step-1][cred_level-1]


def get_blue_and_yellow_outcome(cblue_step, cblue_level, input_blue_cnt):
    # TODO return the blue and yel output for the blue card '
    '''
    cblue1: 0.5:0.5, 0.8:0.2, 1:1
    cblue2: 0.4:0.6, 0.6:0.4, 0.8:0.2 + 0.8*2
    cblue3: 0.3:0.7, 0.5:0.5, 0.7:0.3 + 0.7*2
    '''
    blue_ratio_table = [
        [0.5,0.8,1],
        [0.4,0.6,0.8],
        [0.3,0.5,0.7]
    ]
    yellow_ratio_table = [
        [0.5,0.2,0],
        [0.6,0.4,0.2],
        [0.7,0.5,0.3]
    ]
    yellow_extra_table = [
        [0,0,1],
        [0,0,2],
        [0,0,2]
    ]
    output_blue_cnt = int(ceil(input_blue_cnt * blue_ratio_table[cblue_step-1][cblue_level-1]))
    output_yel_cnt = int(floor(input_blue_cnt * (yellow_ratio_table[cblue_step-1][cblue_level-1]))) + int(ceil(output_blue_cnt * yellow_extra_table[cblue_step-1][cblue_level-1]))
    return (output_blue_cnt, output_yel_cnt)

def get_pur_input(cpur_step, cpur_level, input_pur_cnt, input_other_cnt):
    # TODO calculate the purple output 
    '''
    divide level
    cpur1: f, t, t
    cpur2: f, f, t
    cpur3: f, t, t
    '''
    divide_table = [
        [False, True, True],
        [False, False, True],
        [False, True, True]
    ]
    is_divide = divide_table[cpur_step-1][cpur_level-1]
    if (input_other_cnt == 0 or input_pur_cnt == 0):
        return input_pur_cnt, input_other_cnt, 0
    if (is_divide):
        output_cnt = int(ceil((input_pur_cnt+input_other_cnt) * 0.5))
        return 0, 0, output_cnt
    else:
        less_one = min(input_pur_cnt, input_other_cnt)
        return input_pur_cnt - less_one, input_other_cnt - less_one, less_one

def get_pur_price_add(cpur_step, cpur_level):
    # TODO purple price add 
    '''
    price add
    cpur1: 0, 0, 5
    cpur2: 0, 15, 15
    cpur3: 0, 0, 100
    '''
    # for pur 1 2 3(pur3stone)
    price_add_table = [
        [0,0,5],
        [0,15,15],
        [0,0,100]
    ]
    return price_add_table[cpur_step-1][cpur_level-1]

def get_cyel_duplicate_ratio(cyel_step, cyel_level):
    # TODO yellow card duplicate ratio
    '''
    cyel1: 2, 3, 5
    cyel2: 3, 5, 8
    cyel3: 5, 9, 9
    '''
    table = [
        [2,3,5],
        [3,5,8],
        [5,9,9]
    ]
    return  table[cyel_step-1][cyel_level-1]

def get_cyel_add_price(cyel_step, cyel_level):
    #TODO yellow card add price
    '''
    cyel1: 0, 0, 0
    cyel2: 0, 0, 0
    cyel3: 0, 0, 1
    '''
    return 1 if cyel_step == 3 and cyel_level == 3 else 0


'''
input format:
work(slots[6] : card, init_stone_cnt[r,b,p,y], deck: dict {card.str() -> 0(notexist), 1, 2 ,3})
'''
def workSlots(slots: list, init_stone_cnt: list, deck_dict: dict, shown_init_predict_scores=0):
    assert(len(slots)==6 and len(init_stone_cnt)==4)
    # quick prune prework conflict
    cred1_level = deck_dict["{}_{}".format(CardType.CRED.value, 1)]
    cred2_level = deck_dict["{}_{}".format(CardType.CRED.value, 2)]
    cred3_level = deck_dict["{}_{}".format(CardType.CRED.value, 3)]

    slots_dict = defaultdict(int)
    for slot in slots:
        if slot.card_type != CardType.EMPTY and slot.card_type != CardType.NOT_OPEN: 
            slots_dict[str(slot)] = deck_dict[str(slot)] 

    if check_prework(1, cred1_level):
        if slots_dict["{}_{}".format(CardType.CRED.value, 1)] > 0: return 0,0
        if check_prework(2, cred2_level):
            if slots_dict["{}_{}".format(CardType.CRED.value, 2)] > 0: return 0,0
            if check_prework(3, cred3_level):
                if slots_dict["{}_{}".format(CardType.CRED.value, 3)] > 0: return 0,0

    stone_dict = defaultdict(int)
    stone_dict["{}_{}".format(StoneType.RED.value, 0)] = init_stone_cnt[0]
    stone_dict["{}_{}".format(StoneType.BLUE.value, 0)] = init_stone_cnt[1]
    stone_dict["{}_{}".format(StoneType.PUR.value, 0)] = init_stone_cnt[2]
    stone_dict["{}_{}".format(StoneType.YEL.value, 0)] = init_stone_cnt[3]

    # prework cred
    if check_prework(1, cred1_level):
        stone_dict["{}_{}".format(StoneType.RED.value, 1)] += int(ceil(stone_dict["{}_{}".format(StoneType.RED.value, 0)] * get_duplicate_cred_ratio(1, cred1_level)))
        stone_dict["{}_{}".format(StoneType.RED.value, 0)] = 0
        if check_prework(2, cred2_level):
            stone_dict["{}_{}".format(StoneType.RED.value, 2)] += int(ceil(stone_dict["{}_{}".format(StoneType.RED.value, 1)] * get_duplicate_cred_ratio(2, cred2_level)))
            stone_dict["{}_{}".format(StoneType.RED.value, 1)] = 0
            if check_prework(3, cred3_level):
                stone_dict["{}_{}".format(StoneType.RED.value, 3)] += int(ceil(stone_dict["{}_{}".format(StoneType.RED.value, 2)] * get_duplicate_cred_ratio(3, cred3_level)))
                stone_dict["{}_{}".format(StoneType.RED.value, 2)] = 0
    # print(stone_dict)
    pur_stone_price_add = 0
    pur_3_stone_price_add = 0
    yel_stone_price_add = 0
    empty_slot = 0
    empty_slot_price = 0

    for slot in slots:
        level = deck_dict[str(slot)]
        if slot.card_type == CardType.CRED:
            # print("RED CARD?????")
            if slot.step == 1:
                stone_dict["{}_{}".format(StoneType.RED.value, 1)] += int(ceil(stone_dict["{}_{}".format(StoneType.RED.value, 0)] * get_duplicate_cred_ratio(1, level)))
                stone_dict["{}_{}".format(StoneType.RED.value, 0)] = 0
            elif slot.step == 2:
                stone_dict["{}_{}".format(StoneType.RED.value, 2)] += int(ceil(stone_dict["{}_{}".format(StoneType.RED.value, 1)] * get_duplicate_cred_ratio(2, level)))
                stone_dict["{}_{}".format(StoneType.RED.value, 1)] = 0
            elif slot.step == 3:
                stone_dict["{}_{}".format(StoneType.RED.value, 3)] += int(ceil(stone_dict["{}_{}".format(StoneType.RED.value, 2)] * get_duplicate_cred_ratio(3, level)))
                stone_dict["{}_{}".format(StoneType.RED.value, 2)] = 0
            elif slot.step == 4:
                if level == 2: empty_slot_price = 1500
                elif level == 3: empty_slot_price = 5000
                stone_dict["{}_{}".format(StoneType.RED.value, 4)] += int(ceil(stone_dict["{}_{}".format(StoneType.RED.value, 3)] * get_duplicate_cred_ratio(4, level)))
                stone_dict["{}_{}".format(StoneType.RED.value, 3)] = 0
        elif slot.card_type == CardType.CBLUE:
            if slot.step == 1:
                output_blue_cnt, output_yel_cnt = get_blue_and_yellow_outcome(1, level, stone_dict["{}_{}".format(StoneType.BLUE.value, 0)])
                stone_dict["{}_{}".format(StoneType.BLUE.value, 1)] += output_blue_cnt
                stone_dict["{}_{}".format(StoneType.BLUE.value, 0)] = 0
                stone_dict["{}_{}".format(StoneType.YEL.value, 0)] += output_yel_cnt
            elif slot.step == 2:
                output_blue_cnt, output_yel_cnt = get_blue_and_yellow_outcome(2, level, stone_dict["{}_{}".format(StoneType.BLUE.value, 1)])
                stone_dict["{}_{}".format(StoneType.BLUE.value, 2)] += output_blue_cnt
                stone_dict["{}_{}".format(StoneType.BLUE.value, 1)] = 0
                stone_dict["{}_{}".format(StoneType.YEL.value, 0)] += output_yel_cnt
            elif slot.step == 3:
                output_blue_cnt, output_yel_cnt = get_blue_and_yellow_outcome(3, level, stone_dict["{}_{}".format(StoneType.BLUE.value, 2)])
                stone_dict["{}_{}".format(StoneType.BLUE.value, 3)] += output_blue_cnt
                stone_dict["{}_{}".format(StoneType.BLUE.value, 2)] = 0
                stone_dict["{}_{}".format(StoneType.YEL.value, 0)] += output_yel_cnt
        elif slot.card_type == CardType.CPUR:
            if slot.step == 1:
                pur_stone_price_add += get_pur_price_add(1, level)
                p0, y0, p1 = get_pur_input(1, level, stone_dict["{}_{}".format(StoneType.PUR.value, 0)], stone_dict["{}_{}".format(StoneType.YEL.value, 0)])
                stone_dict["{}_{}".format(StoneType.PUR.value, 0)] = p0
                stone_dict["{}_{}".format(StoneType.YEL.value, 0)] = y0
                stone_dict["{}_{}".format(StoneType.PUR.value, 1)] = p1
            if slot.step == 2:
                pur_stone_price_add += get_pur_price_add(2, level)
                p1, b1, p2 = get_pur_input(1, level, stone_dict["{}_{}".format(StoneType.PUR.value, 1)], stone_dict["{}_{}".format(StoneType.BLUE.value, 1)])
                stone_dict["{}_{}".format(StoneType.PUR.value, 1)] = p1
                stone_dict["{}_{}".format(StoneType.BLUE.value, 1)] = b1
                stone_dict["{}_{}".format(StoneType.PUR.value, 2)] = p2
            if slot.step == 3:
                pur_3_stone_price_add += get_pur_price_add(3, level)
                p2, r3, p3 = get_pur_input(1, level, stone_dict["{}_{}".format(StoneType.PUR.value, 2)], stone_dict["{}_{}".format(StoneType.RED.value, 3)])
                stone_dict["{}_{}".format(StoneType.PUR.value, 2)] = p2
                stone_dict["{}_{}".format(StoneType.RED.value, 3)] = r3
                stone_dict["{}_{}".format(StoneType.PUR.value, 3)] = p3
        elif slot.card_type == CardType.CYEL:
            ratio = get_cyel_duplicate_ratio(slot.step, level)
            yel_stone_price_add += get_cyel_add_price(slot.step, level)
            stone_dict["{}_{}".format(StoneType.YEL.value, 0)] = int(ceil(stone_dict["{}_{}".format(StoneType.YEL.value, 0)] * ratio))
        elif slot.card_type == CardType.EMPTY:
            empty_slot += 1
        # print("After {}\t{}".format(slot, stone_dict))
    
    res = 0
    res += empty_slot_price * empty_slot

    stone_type = StoneType.RED
    for level in [0,1,2,3,4]:
        stone = Stone(stone_type, level)
        # print("Price of {} is {}".format(stone, stone.price(pur_stone_price_add, pur_3_stone_price_add, yel_stone_price_add) ))
        amnt = stone_dict[str(stone)]
        res += stone.price(pur_stone_price_add, pur_3_stone_price_add, yel_stone_price_add) * amnt
        if amnt > 0: pur_3_stone_price_add = 0

    stone_type = StoneType.BLUE
    for level in [0,1,2,3]:
        stone = Stone(stone_type, level)
        # print("Price of {} is {}".format(stone, stone.price(pur_stone_price_add, pur_3_stone_price_add, yel_stone_price_add) ))
        amnt = stone_dict[str(stone)]
        res += stone.price(pur_stone_price_add, pur_3_stone_price_add, yel_stone_price_add) * amnt
        if amnt > 0: pur_3_stone_price_add = 0
        
    stone_type = StoneType.YEL
    for level in [0]:
        stone = Stone(stone_type, level)
        # print("Price of {} is {}".format(stone, stone.price(pur_stone_price_add, pur_3_stone_price_add, yel_stone_price_add) ))
        amnt = stone_dict[str(stone)]
        res += stone.price(pur_stone_price_add, pur_3_stone_price_add, yel_stone_price_add) * amnt
        if amnt > 0: pur_3_stone_price_add = 0

    stone_type = StoneType.PUR
    for level in [0,1,2,3]:
        stone = Stone(stone_type, level)
        # print("Price of {} is {}".format(stone, stone.price(pur_stone_price_add, pur_3_stone_price_add, yel_stone_price_add) ))
        amnt = stone_dict[str(stone)]
        if amnt > 0 and level != 3: pur_3_stone_price_add = 0 
        res += stone.price(pur_stone_price_add, pur_3_stone_price_add, yel_stone_price_add) * amnt
        
    return res, (shown_init_predict_scores + res - (init_stone_cnt[0]+init_stone_cnt[1]+init_stone_cnt[2]+init_stone_cnt[3]))

