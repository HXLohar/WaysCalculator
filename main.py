import classes
import tkinter as tk
import tkinter.messagebox
import tkinter.simpledialog

class symbol_button_label_group:
    def __init__(self):
        self.frame = None
        self.button = None
        self.label = None
        self.reel_id = -1
        self.Y_position = 0
class window:
    def __init__(self, file_name = 'bonanza.txt'):
        self.selected_symbol = "Eraser"
        self.selected_symbol_label = None
        self.selected_symbol_button = None
        self.sample_button = None
        self.checkbox_flags = [False, False, False]
        self.window = tk.Tk()
        self.window.geometry('1200x900')
        # disable min/max button as well as not resizable
        self.window.resizable(False, False)
        # hide the main window
        self.window.withdraw()
        # ask to input config file name
        # use popup input box
        file_name = tk.simpledialog.askstring("Input", "Please input the file name of the config file:")
        # if file_name not ending in ".txt", add it
        if not file_name.endswith(".txt"):
            file_name += ".txt"
        # quit if file not found
        flag_found_file = False
        try:
            with open(file_name, 'r'):
                flag_found_file = True
        except FileNotFoundError:
            flag_found_file = False

        if not flag_found_file:
            # use message box
            tk.messagebox.showerror("Too bad", "Thank you for providing a file name that doesn't exist.\n"
                                               "The program will now exit.")
            exit()

        self.config = classes.config(file_name)
        self.label_paytable = None
        self.multiplier_textbox = None


        self.groups = [[symbol_button_label_group() for _ in range(self.config.max_size_per_reel)] for _ in range(self.config.reels)]
        # self.groups = [[symbol_button_label_group(i) for i in range(self.config.reels)] for _ in range(self.config.max_size_per_reel)]

        self.select_symbol_buttons = []
        self.select_symbol_entry = []

        self.create_pay_table()
        self.init_top_left()
        self.init_middle_left()
        self.init_bottom_left()

        self.symbols = [[''] * self.config.max_size_per_reel for _ in range(self.config.reels)]
        self.multipliers = [[1] * self.config.max_size_per_reel for _ in range(self.config.reels)]
        # set the window title to file name
        self.window.title(f"Config file: {file_name}")
        self.init_bottom_right()
        # display the main window after all the widgets are created
        self.window.deiconify()
        self.window.mainloop()

    def init_bottom_right(self):
        # Define the area for the buttons and text boxes
        area4 = tk.Frame(self.window, width=400, height=400)
        area4.place(x=800, y=500)


        # Create a text box at the bottom
        text_box = tk.Text(area4, font=("Helvetica", "14"))
        text_box.insert(tk.END, "Result will be displayed here.\n")

        # it cannot be edited
        text_box.config(state=tk.DISABLED)
        text_box.place(x=0, y=100, width=400, height=300)

        # Create a button above the text box
        # clicking it will call the calculate method, param = text_box
        button = tk.Button(area4, text="CALCULATE", font=("Helvetica", "16", "bold"), command=lambda: self.calculate(text_box))
        button.place(x=0, y=50, width=400, height=40)
    def calculate(self, output_text_box):
        high_multiplier_list = []
        # get the high multipliers from the text boxes
        for i in range(self.config.high):
            # if it's not number or empty, set it to 1
            if not self.select_symbol_entry[i].get().isdigit() or self.select_symbol_entry[i].get() == "":
                high_multiplier_list.append(1)
            else:
                high_multiplier_list.append(int(self.select_symbol_entry[i].get()))
        # update self.multiplier
        for obj in self.groups:
            for group in obj:
                # get the reel id and Y position
                reel_id = group.reel_id
                Y_position = group.Y_position
                # get the text of the button
                symbol_text = group.button.cget("text")
                # get the text of the entry
                entry_text = group.label.get()
                # if the text is not a number or empty, set it to 1
                if not entry_text.isdigit() or entry_text == "":
                    self.multipliers[reel_id][Y_position] = 1
                else:
                    self.multipliers[reel_id][Y_position] = max(int(entry_text), 1)
                # set the symbol to the symbol_text
                self.symbols[reel_id][Y_position] = symbol_text
        board_calculator = classes.board_calculator(self.symbols, self.multipliers, self.config, int(self.multiplier_textbox.get()),
                                                    high_multiplier_list)
        board_calculator.update_symbol_list(self.config.symbol_list)
        # clear the text box first

        output_text_box.config(state=tk.NORMAL)
        output_text_box.delete(1.0, tk.END)
        output_text_box.insert(tk.END, board_calculator.calculate_payout())
        output_text_box.config(state=tk.DISABLED)



    def remove_w_on_reel_1(self):
        button_default_bg = "#EEEEEE"

        for obj in self.groups:
            for index, group in enumerate(obj):
                if group.reel_id == 0 and group.button.cget("text") == "W":
                    group.button.config(text="", font=("Helvetica", "16", "bold"), bg=button_default_bg, fg="#000000")
                    group.label.delete(0, tk.END)
                    # set the symbol to "" and multiplier to 1
                    self.symbols[group.reel_id][index] = ""
                    self.multipliers[group.reel_id][index] = 1

    def init_top_left(self):
        # Define the area for the buttons and text boxes
        area1 = tk.Frame(self.window, width=600, height=200)
        area1.place(x=0, y=0)

        # Create a label at the top of the area
        self.selected_symbol_label = tk.Label(area1, text=f"Selected Symbol:",
                                              font=("Helvetica", "14", "bold"))
        self.selected_symbol_label.place(x=10, y=0, width=200, height=40)

        # create a sample button on the right
        # reference:
        # w_button = tk.Button(area3, text="W", bg=colors[6], fg="#FFFFFF", font=("Helvetica", "16", "bold"))
        #         w_button.config(command=lambda button=w_button: self.select_symbol("W", button))
        #         w_button.place(x=30, y=60, width=70, height=35)

        self.sample_button = tk.Button(area1, text="Eraser", font=("Helvetica", "16", "bold"))
        self.sample_button.place(x=220, y=0, width=70, height=40)




        # Create a checkbox at the top of the area
        self.checkbox_flags[0] = tk.BooleanVar()
        checkbox1 = tk.Checkbutton(area1, text="Allow W on reel 1", variable=self.checkbox_flags[0],
                                   font=("Helvetica", "14"), anchor='w')
        checkbox1.place(x=60, y=50, width=240, height=60)
        # when deselected, remove all W on reel 1

        checkbox1.config(command=self.remove_w_on_reel_1)

        # Create a checkbox at the top of the area
        self.checkbox_flags[1] = tk.BooleanVar()
        checkbox2 = tk.Checkbutton(area1, text="Both Ways", variable=self.checkbox_flags[1], font=("Helvetica", "14"),
                                   anchor='w')
        checkbox2.place(x=60, y=110, width=120, height=60)

        # Create a checkbox at the top of the area
        self.checkbox_flags[2] = tk.BooleanVar()
        checkbox3 = tk.Checkbutton(area1, text=f"Both Ways: \n{self.config.reels} OAKs counts twice",
                                   variable=self.checkbox_flags[2], font=("Helvetica", "14"), anchor='w')
        checkbox3.place(x=180, y=110, width=240, height=60)

        # Create a button at the top of the area

        button = tk.Button(area1, text="Reset Board...", font=("Helvetica", "14", "bold"), command=self.create_reset_menu)
        button.place(x=400, y=120, width=140, height=40)


        # Create a text box at the top of the area, with a default value of 1
        self.multiplier_textbox = tk.Entry(area1, validate="key",
                                           validatecommand=(area1.register(lambda P: len(P) <= 3), '%P'), font=("Helvetica", "18"))
        self.multiplier_textbox.place(x=400, y=60, width=180, height=40)
        self.multiplier_textbox.insert(0, "1")

        # create a label above it, with a text of "Global Multiplier"
        label = tk.Label(area1, text="Global Multiplier", font=("Helvetica", "14", "bold"))
        label.place(x=400, y=40, width=180, height=20)
    def create_reset_menu(self):

        # Reset Board button will create a popup menu (top left = clicked coordinates) with 3 choices
        # 1 Clear All
        # 2 Clear All W
        # 3 Clear All non W
        # all those button will call the reset_board method with different parameter
        menu = tk.Menu(self.window, tearoff=0)
        menu.add_command(label="Clear All", command=lambda: self.reset_board("all"))
        menu.add_command(label="Clear All W", command=lambda: self.reset_board("W"))
        menu.add_command(label="Clear All non W", command=lambda: self.reset_board("non W"))
        # display the menu
        menu.post(self.window.winfo_pointerx(), self.window.winfo_pointery())
    def reset_board(self, param=""):
        # if param is "all", clear all symbols and multipliers
        if param == "all":
            for obj in self.groups:
                for group in obj:
                    group.button.config(text="", font=("Helvetica", "16", "bold"), bg="#EEEEEE", fg="#000000")
                    group.label.delete(0, tk.END)
                    group.label.insert(0, "1")
        # if param is "W", clear all W symbols and multipliers
        elif param == "W":
            for obj in self.groups:
                for group in obj:
                    if group.button.cget("text") == "W":
                        group.button.config(text="", font=("Helvetica", "16", "bold"), bg="#EEEEEE", fg="#000000")
                        group.label.delete(0, tk.END)
                        group.label.insert(0, "1")
        # if param is "non W", clear all non W symbols and multipliers
        elif param == "non W":
            for obj in self.groups:
                for group in obj:
                    if group.button.cget("text") != "W":
                        group.button.config(text="", font=("Helvetica", "16", "bold"), bg="#EEEEEE", fg="#000000")
                        group.label.delete(0, tk.END)
                        group.label.insert(0, "1")

    def init_middle_left(self):
        # Define the area for the middle left
        area2 = tk.Frame(self.window, width=700, height=450)
        area2.place(x=0, y=200)

        # Define the size of each group based on the number of reels
        group_width = {4: 130, 5: 100, 6: 85}[self.config.reels]
        group_height = 380 / (self.config.max_size_per_reel + max(self.config.reel_offset))
        # print(self.config.reel_offset)

        # Define the size of the button and text box
        button_width = int(group_width * 0.7)
        text_box_width = group_width - button_width

        # Define the Tcl command for validating the Entry widget's value
        validate_cmd = area2.register(lambda P: len(P) <= 4)

        # Create the groups
        for i in range(self.config.reels):
            x = i * (group_width + 20) + 10

            y = 10 + self.config.reel_offset[i] * (group_height + 5)

            for j in range(self.config.max_size_per_reel):
                # Calculate the position of the group

                # Create the button
                button = tk.Button(area2, width=button_width, height=40)
                button.config(command=lambda button=button: self.paint_button(button))
                button.place(x=x, y=y, width=button_width, height=40)

                # Create the text box with a font of 12 bold
                text_box = tk.Entry(area2, validate="key", validatecommand=(validate_cmd, '%P'), font=("Helvetica", "12", "bold"))
                text_box.place(x=x + button_width, y=y, width=text_box_width, height=40)
                # default value being 1
                text_box.insert(0, "1")

                # Create a symbol_button_label_group instance and store the button and text box
                group = symbol_button_label_group()
                group.frame = area2
                group.button = button
                group.label = text_box
                group.reel_id = i
                group.Y_position = j

                # Store the group in self.groups
                self.groups[i][j] = group
                y += group_height + 5

    def init_bottom_left(self):
        # Define the area for the buttons and text boxes
        area3 = tk.Frame(self.window, width=700, height=250)
        area3.place(x=0, y=650)

        # Create a label at the top of the area
        label = tk.Label(area3, text="Click to select symbol, then click on the board to place it.\n"
                                     "Use the text box to adjust symbol payout multiplier",
                         font=("Helvetica", "14", "bold"))
        label.place(x=0, y=0, width=600, height=50)

        # Define the colors for the buttons
        colors = ["#7C51B0", "#B04642", "#4780BC", "#66A040", "#C6A336", "#6EA3A7", "#000000"]

        # Create the W button
        w_button = tk.Button(area3, text="W", bg=colors[6], fg="#FFFFFF", font=("Helvetica", "16", "bold"))
        w_button.config(command=lambda button=w_button: self.select_symbol("W", button))
        w_button.place(x=30, y=60, width=70, height=35)
        self.select_symbol_buttons.append(w_button)

        eraser_button = tk.Button(area3, text="Eraser", font=("Helvetica", "16", "bold"))
        eraser_button.config(command=lambda button=eraser_button: self.select_symbol("Eraser", button))
        eraser_button.place(x=140, y=60, width=110, height=35)
        self.select_symbol_buttons.append(eraser_button)
        self.selected_symbol_button = eraser_button

        y_position = 100

        # Create the H buttons and text boxes
        for i in range(self.config.high):
            button = tk.Button(area3, text=f"H{i + 1}", bg=colors[i], fg="#FFFFFF", font=("Helvetica", "16", "bold"))
            button.config(command=lambda i=i, button=button: self.select_symbol(f"H{i + 1}", button))
            button.place(x=i * 110 + 30, y=y_position, width=70, height=35)
            self.select_symbol_buttons.append(button)
            # then create the text boxes
            text_box = tk.Entry(area3, validate="key", validatecommand=(area3.register(lambda P: len(P) <= 4), '%P'), font=("Helvetica", "12", "bold"))
            # input a 1 for each
            text_box.insert(0, "1")
            text_box.place(x=i * 110 + 100, y=y_position, width=30, height=35)
            self.select_symbol_entry.append(text_box)

        y_position += 40

        # Create the M buttons
        for i in range(self.config.medium):
            button = tk.Button(area3, text=f"M{i + 1}", bg="#D3D3D3", fg=colors[i], font=("Helvetica", "15", "bold"))
            button.config(command=lambda i=i, button=button: self.select_symbol(f"M{i + 1}", button))
            button.place(x=i * 110 + 30, y=y_position, width=70, height=35)
            self.select_symbol_buttons.append(button)
        y_position += 40

        # Create the L buttons
        for i in range(self.config.low):
            button_text = f"L{i + 1}"
            if self.config.low_alias and i < 6:
                button_text = ["A", "K", "Q", "J", "10", "9"][i]
            button = tk.Button(area3, text=button_text, bg="#D3D3D3", fg=colors[i], font=("Helvetica", "14"))
            button.config(
                command=lambda button_text=button_text, button=button: self.select_symbol(button_text, button))
            button.place(x=i * 110 + 30, y=y_position, width=70, height=35)
            self.select_symbol_buttons.append(button)
    def create_pay_table(self):
        # Create a label or something like rich text, on the right 1/3 side of the window,
        # using absolute coordinate and size.
        # Format example is given.
        # head: 4 characters (including [])
        # each other param after: 6 characters (including [])
        # total param is equal to "Reels" in the loaded config file
        # also replace 0 with blank.
        # EXAMPLE:
        #     [    ][  2 ][  3 ][  4 ][  5 ][  6 ]
        # [H1]        200   500  1000  2500  5000
        # [H2]              100   200   250   750
        # ...
        # [10]               15    25    50   100
        # [ 9]               15    25    50   100
        # Note [  5 ] and [  6 ] is might not be necessary, depending on the value of self.config.reels
        self.label_paytable = tk.Label(self.window, text='paytable place test', font=('Courier', 12), justify='left')
        self.label_paytable.place(x=750, y=0, width=450, height=500)
        self.label_paytable.config(text=self.get_paytable())

    def get_paytable(self):
        paytable = "Paytable\nUnit: Coins (1x Base bet = 100 Coins)\n    "
        for i in range(1, self.config.reels + 1):
            paytable += f'[{i:>4}]'
        paytable += '\n'

        # Generate symbol names
        symbol_names = [f'H{i + 1}' for i in range(self.config.high)]
        symbol_names += [f'M{i + 1}' for i in range(self.config.medium)]
        if self.config.low_alias:
            symbol_names += ['A', 'K', 'Q', 'J', '10', '9'][:self.config.low]
        else:
            symbol_names += [f'L{i + 1}' for i in range(self.config.low)]

        for i in range(0, self.config.symbol_count):
            paytable += f'[{symbol_names[i]:>2}]'
            for j in range(self.config.reels):
                if j < len(self.config.symbols[i]):
                    paytable += f'{self.config.symbols[i][j]:>6}' if self.config.symbols[i][j] != 0 else '      '
                else:
                    paytable += '      '
            paytable += '\n'
        return paytable

    def select_symbol(self, symbol_name, symbol_button):

        # Set the selected symbol to the given symbol name
        # and update the selected symbol label
        self.selected_symbol = symbol_name
        self.selected_symbol_button = symbol_button
        symbol_text = self.selected_symbol_button.cget("text")
        symbol_font = self.selected_symbol_button.cget("font")
        symbol_bg = self.selected_symbol_button.cget("background")
        symbol_fg = self.selected_symbol_button.cget("foreground")
        self.sample_button.config(text=symbol_text, font=symbol_font, bg=symbol_bg, fg=symbol_fg)

    def paint_button(self, clicked_button):
        # Initialize reel_id and entry
        reel_id = None
        entry = None

        # get the reel id of the clicked button, left most = 0
        for obj in self.groups:
            for group in obj:
                if group.button == clicked_button:
                    reel_id = group.reel_id
                    entry = group.label
                    # Break the inner loop
                    break
            # Break the outer loop if the button was found
            if reel_id is not None:
                break

        # if allow W on reel 1 not selected, and W is selected, and a button reel 1 ls clicked, return
        if not self.checkbox_flags[0].get() and self.selected_symbol == "W" and reel_id == 0:
            return

        # Get the text, font, background color, and foreground color of the selected symbol button
        symbol_text = self.selected_symbol_button.cget("text")
        symbol_font = self.selected_symbol_button.cget("font")
        symbol_bg = self.selected_symbol_button.cget("background")
        symbol_fg = self.selected_symbol_button.cget("foreground")

        if symbol_text == "Eraser":
            symbol_text = ""

        # Set the text, font, background color, and foreground color of the clicked button to the selected symbol button's properties
        clicked_button.config(text=symbol_text, font=symbol_font, bg=symbol_bg, fg=symbol_fg)

        Y_position = group.Y_position
        self.symbols[reel_id][Y_position] = symbol_text



# load the window
window()