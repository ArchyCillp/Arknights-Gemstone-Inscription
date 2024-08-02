import tkinter as tk
from tkinter import messagebox
from solver import *


class SimpleUI:
    def __init__(self, master):
        self.master = master
        master.title("宝石铭刻(数据大的时候可能会未响应30秒之内，属正常现象);最上面的是你的全部手牌，左下的颜色是这局初始的材料数量，全填完确认暴力计算本局最佳出牌方式")

        # Drop-down menus
        self.dropdown_labels = []
        self.dropdowns = []
        Item_name = [
            "红色淬雕I",
            "红色淬雕II",
            "红色淬雕III",
            "红色淬雕IV",
            "蓝色滤纯I",
            "蓝色滤纯II",
            "蓝色滤纯III",
            "紫色交糅I",
            "紫色交糅II",
            "紫色交糅III",
            "黄色落晶I",
            "黄色落晶II",
            "黄色落晶III",
        ]
        for i in range(1, 14):
            label = tk.Label(master, text=Item_name[i-1])
            label.grid(row=0, column=i-1)

            dropdown = tk.StringVar(master)
            dropdown.set("没有")  # default value
            dropdown_menu = tk.OptionMenu(master, dropdown, "没有", "初级", "中级", "高级")
            dropdown_menu.grid(row=1, column=i-1)

            self.dropdown_labels.append(label)
            self.dropdowns.append(dropdown)

        # Text input for the number of slots opened
        self.slots_label = tk.Label(master, text="已开启的工作台数:")
        self.slots_label.grid(row=2, column=0, columnspan=2)

        self.slots_entry = tk.Entry(master)
        self.slots_entry.grid(row=2, column=2)

        self.score_label = tk.Label(master, text="没出牌时的预估分数:")
        self.score_label.grid(row=2, column=4, columnspan=2)

        self.score_entry = tk.Entry(master)
        self.score_entry.grid(row=2, column=6)

        # Input boxes for red, blue, purple, yellow
        colors = ["红", "蓝", "紫", "黄"]
        self.color_entries = {}
        for idx, color in enumerate(colors):
            color_label = tk.Label(master, text=color.capitalize() + ":")
            color_label.grid(row=3 + idx, column=0)

            color_entry = tk.Entry(master)
            color_entry.grid(row=3 + idx, column=1)
            self.color_entries[color] = color_entry

        # Okay button
        self.ok_button = tk.Button(master, text="确认", command=self.collect_info)
        self.ok_button.grid(row=7, column=0, columnspan=2)

        # Output message area
        self.output_text = tk.Text(master, height=10, width=50)
        self.output_text.grid(row=8, column=0, columnspan=13)

    def check_entry_string(self, string: str, x, y):
        if not string.isdigit():
            self.output_text.insert(tk.END,"{} 非法，必须输入数字".format(string))
        n = int(string)
        if n < x or n > y:
            self.output_text.insert(tk.END,"{} 非法，必须在[{},{}]范围内".format(string, x, y))


    def solve(self, deck, open_slot, stones_cnt, original_predict_score):
        from itertools import permutations
        deck_list = deck.keys()
        print(deck_list)
        max_score = 0
        for i in range(open_slot, 0, -1):
            perlist = list(permutations(deck_list, i))
            # print("{} permunations need to be tried".format(len(perlist)))
            for per in perlist:
                slots = []
                for card in per:
                    name, step = card.split("_")
                    card_name = get_card_type(name)
                    step = int(step)
                    slots.append(Card(card_name, step))
                while len(slots) < open_slot:
                    slots.append(Card(CardType.EMPTY, 1))
                while len(slots) < 6:
                    slots.append(Card(CardType.NOT_OPEN, 1))
                for key in list(deck.keys()):  # Create a list to avoid modifying the dictionary while iterating
                    if deck[key] == 0:
                        del deck[key]
                res, show_score = workSlots(slots, stones_cnt, deck, original_predict_score)
                if res > max_score:
                    max_score = res
                    self.output_text.insert(tk.END,"当前发现最佳方案: {}(总分 {})\n{}\n\n\n".format(max_score, show_score, ",".join(c.cn_str() for c in slots)))

    def collect_info(self):
        # Collecting data from dropdowns
        deck_names = ["{}_1".format(CardType.CRED.value),
        "{}_2".format(CardType.CRED.value),
        "{}_3".format(CardType.CRED.value),
        "{}_4".format(CardType.CRED.value),
        "{}_1".format(CardType.CBLUE.value),
        "{}_2".format(CardType.CBLUE.value),
        "{}_3".format(CardType.CBLUE.value),
        "{}_1".format(CardType.CPUR.value),
        "{}_2".format(CardType.CPUR.value),
        "{}_3".format(CardType.CPUR.value),
        "{}_1".format(CardType.CYEL.value),
        "{}_2".format(CardType.CYEL.value),
        "{}_3".format(CardType.CYEL.value)]

        deck = defaultdict(int)

        for i, dropdown in enumerate(self.dropdowns):
            sel = dropdown.get()
            deck_name = deck_names[i]
            if sel == "初级":
                deck[deck_name] = 1
            elif sel == "中级":
                deck[deck_name] = 2
            elif sel == "高级":
                deck[deck_name] = 3

        dropdown_values = [dropdown.get() for dropdown in self.dropdowns]

        slots_opened = self.slots_entry.get()

        self.check_entry_string(slots_opened, 2, 6)

        open_slot = int(slots_opened)

        for value in self.color_entries.values():
            self.check_entry_string(value.get(), 0, 10000)

        color_cnt = [int(self.color_entries["红"].get()),
            int(self.color_entries["蓝"].get()),
            int(self.color_entries["紫"].get()),
            int(self.color_entries["黄"].get())
        ]

        self.check_entry_string(self.score_entry.get(), 0, 100000000000)
        original_predict_score = int(self.score_entry.get())

        # Displaying the output message
        self.output_text.delete(1.0, tk.END)  # Clear previous output
        self.output_text.insert(tk.END, "计算中,请稍等...\n")
        print(deck)
        self.solve(deck, open_slot, color_cnt, original_predict_score)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleUI(root)
    root.mainloop()