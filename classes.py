# So first, there's a config file. Load it into a config class.
# Example of "bonanza.txt":
# (Beginning of example)
# Reels: 6 # Reel size, between 3-6
# Max_Size_Per_Reel: 7 # Max symbols on a single reel, between 2-12
# High: 4 # Number of high value symbols (0-6)
# Medium: 0 # Number of medium value symbols (0-6)
# Low: 6 # Number of low value symbols (0-6)
# # sum of all 3 value above should be in between 5 and 15.
# Low_Alias: True # True: use A/K/Q/... instead of L1/L2/L3...
# H1: 0, 200, 500, 1000, 2500, 5000
# H2: 0, 0, 100, 200, 250, 750
# H3: 0, 0, 40, 100, 150, 250
# H4: 0, 0, 30, 50, 100, 200
# A: 0, 0, 25, 40, 70, 175
# K: 0, 0, 25, 40, 70, 175
# Q: 0, 0, 20, 30, 60, 120
# J: 0, 0, 20, 30, 60, 120
# 10: 0, 0, 15, 25, 50, 100
# 9: 0, 0, 15, 25, 50, 100
# (End of example)
# Now, load it into a class named config.

class config:
    def __init__(self, filename='bonanza.txt'):
        self.filename = filename
        self.reels = 0
        self.max_size_per_reel = 0
        self.high = 0
        self.medium = 0
        self.low = 0
        self.low_alias = False
        self.symbols = []
        self.reel_offset = [0.0] * 6
        self.reel_setup = []
        self.load_config()
        # print(self.reel_offset)
        self.check_config()
        self.symbol_count = self.high + self.medium + self.low
        # symbol list = a list of each symbol's name that's involved, from highest to lowest.
        # example, for a game with 4 H 6 L and low_alias=true, it's ["H1", "H2", "H3", "H4", "A", "K", ...]
        self.symbol_list = [f'H{i + 1}' for i in range(self.high)]
        self.symbol_list += [f'M{i + 1}' for i in range(self.medium)]
        if self.low_alias:
            self.symbol_list += ['A', 'K', 'Q', 'J', '10', '9'][:self.low]
        else:
            self.symbol_list += [f'L{i + 1}' for i in range(self.low)]

    def load_config(self):
        with open(self.filename, 'r') as f:
            flag_setup_found = False
            for line in f:
                if line.startswith('Reel_Setup:'):
                    # Reel_Setup: 2, 3, 3, 3, 2 means 5 reels with 2, 3, 3, 3, 2 symbols.
                    values = line.split(":")[1].split('#')[0].strip()
                    self.reel_setup = [int(x) for x in values.split('-')]
                    self.reels = len(self.reel_setup)
                    self.max_size_per_reel = max(self.reel_setup)
                    flag_setup_found = True
                    # print("The setup is: ", self.reel_setup)
                elif line.startswith('Reels:') and not flag_setup_found:
                    self.reels = int(line.split()[1])
                elif line.startswith('Max_Size_Per_Reel:') and not flag_setup_found:
                    self.max_size_per_reel = int(line.split()[1])
                    self.reel_setup = [self.max_size_per_reel] * self.reels
                elif line.startswith('High:'):
                    self.high = int(line.split()[1])
                elif line.startswith('Medium:'):
                    self.medium = int(line.split()[1])
                elif line.startswith('Low:'):
                    self.low = int(line.split()[1])
                elif line.startswith('Low_Alias:'):
                    self.low_alias = line.split()[1].lower() == 'true'
                # load the reel offset
                elif line.startswith('Reel_Offset:'):
                    values = line.split(":")[1].split('#')[0].strip()  # split at '#' and keep only the first part
                    self.reel_offset = [float(x) for x in values.split(',')]
                elif line.startswith('#'):
                    pass
                else:
                    if ":" in line:
                        values = line.split(":")[1].strip()
                        self.symbols.append([int(x) for x in values.split(',')])
    def check_config(self):
        # If anything incorrect (input not a number, or not in range, or other types of invalid input)
        # pop up a msgbox then quit the program.
        if not 3 <= self.reels <= 6:
            raise ValueError('Reels must be between 3 and 6')
        if not 2 <= self.max_size_per_reel <= 12:
            raise ValueError('Max_Size_Per_Reel must be between 2 and 12')
        if not 5 <= self.high + self.medium + self.low <= 15:
            raise ValueError('Sum of High, Medium and Low must be between 5 and 15')
        if not 0 <= self.high <= 6:
            raise ValueError('High must be between 0 and 6')
        if not 0 <= self.medium <= 6:
            raise ValueError('Medium must be between 0 and 6')
        if not 0 <= self.low <= 6:
            raise ValueError('Low must be between 0 and 6')
        if len(self.symbols) != self.high + self.medium + self.low:
            raise ValueError('Number of symbols does not match High, Medium and Low')
        for symbol in self.symbols:

            for value in symbol:
                if not 0 <= value:
                    raise ValueError('Symbol value must be non-negative')

    def get_payout(self, symbol, OAKs):
        # get the payout of a symbol with a certain OAKs (use OAKs-1 as the index)
        return self.symbols[self.symbol_list.index(symbol)][OAKs - 1]
class board_calculator:
    def __init__(self, board_list, multi_list, config_table, global_multiplier=1, high_multiplier=[1] * 6):
        self.board_list = board_list
        self.multi_list = multi_list
        self.config_table = config_table
        self.symbol_list = []
        self.flag_wild_board = False
        self.existing_symbols = []

        self.global_multiplier = global_multiplier
        self.high_multiplier = high_multiplier

        self.accumulated_wins = 0.0
        # check for each reel, which symbol(s) are present.

        # check which symbol appeared on the board.
        for reel in self.board_list:
            for symbol in reel:
                if symbol not in self.existing_symbols and symbol != '':
                    self.existing_symbols.append(symbol)

        # if the only symbol exists is W, then the board is a wild board.
        if len(self.existing_symbols) == 1 and self.existing_symbols[0] == "W":
            self.flag_wild_board = True
            print("self.existing_symbols: ", self.existing_symbols)

        else:
            self.flag_wild_board = False
        self.calculations_string = []
    # rest of the class methods...
    def update_symbol_list(self, symbol_list):
        self.symbol_list = symbol_list

    def check_if_symbol_exists(self, symbol):
        # check if a symbol exists across all reels.
        # print("Given board: ", self.board_list)
        for i in range(0, self.config_table.reels):
            if symbol in self.board_list[i]:
                return True
        return False

    def calculate_payout(self):
        # print("Calculating payout...")
        # print("Symbols found: ", self.existing_symbols)
        # print("Wild board: ", self.flag_wild_board)
        self.accumulated_wins = 0
        if self.flag_wild_board:
            return_string, return_value = self.calculate_symbol_payout("H1", True)
            self.calculations_string.append("W -> " + return_string)
            self.accumulated_wins += return_value
            joined_string = "\n".join(self.calculations_string)
            joined_string = "\n".join([x for x in joined_string.split("\n") if x.strip() != ""])
            joined_string += f"\nTotal Win: {self.accumulated_wins:,} coins / {self.accumulated_wins / 100:,.2f} x"
            return joined_string
        symbols_involved = []
        for symbol in self.symbol_list:
            if symbol == "W":
                continue

            if self.check_if_symbol_exists(symbol):
                symbols_involved.append(symbol)

        # Calculate payout for each symbol
        for symbol in symbols_involved:
            return_string, return_value = self.calculate_symbol_payout(symbol)
            # print("calculated payout for symbol", symbol, ":", return_value)
            self.calculations_string.append(return_string)
            self.accumulated_wins += return_value

        # Add a result summary for total win
        if self.accumulated_wins > 0:
            self.calculations_string.append(f"Total Win: {self.accumulated_wins:,} coins / {self.accumulated_wins/100:,.2f} x")
        else:
            return "0\n\n(No win)"
        joined_string = "\n".join(self.calculations_string)
        # if there's multiple \n in a row, replace it with just one \n
        joined_string = "\n".join([x for x in joined_string.split("\n") if x.strip() != ""])
        return joined_string

    def calculate_symbol_payout(self, symbol, flag_wild_board_overwrite=False):
        flag_source_symbol_found = False
        payout_string = ""

        OAKs = 0
        Ways = 1
        Ways_factor_list = []
        while OAKs < self.config_table.reels:
            reel_id = OAKs
            if (not symbol in self.board_list[reel_id]) and (not "W" in self.board_list[reel_id]):
                break

            symbol_appearance = 0
            for i in range(len(self.board_list[reel_id])):
                if self.board_list[reel_id][i] == symbol or self.board_list[reel_id][i] == "W":
                    # no multi or negative multi will be treated as 1
                    symbol_appearance += max(self.multi_list[reel_id][i], 1)
                    if self.board_list[reel_id][i] == symbol and not flag_source_symbol_found:
                        flag_source_symbol_found = True
            Ways *= symbol_appearance
            Ways_factor_list.append(symbol_appearance)
            OAKs += 1
        if (not flag_source_symbol_found) and (not flag_wild_board_overwrite):
            return "", 0
        base_payout = self.config_table.get_payout(symbol, OAKs)
        payout = base_payout * Ways
        # Apply global multiplier
        if self.global_multiplier > 1:
            payout *= int(self.global_multiplier)
        # Apply high value symbol multiplier
        if symbol[0] == "H":
            if self.high_multiplier[int(symbol[1]) - 1] > 1:
                payout *= int(self.high_multiplier[int(symbol[1]) - 1])
        # payout string Format:
        # {symbol_name}: {ways:,} Ways ({Ways_factor_list.join("x"}) x {payout_coefficient} ({length} OAKs)
        # x {global_multiplier} (if greater than 1)
        # x {symbol_multiplier} (if it's high value symbol and multiplier greater than 1)
        # = {payout/100:.2f}
        # debug print the symbol, ways, ways factor list, base payout, OAKs, payout
        # print(f"Symbol: {symbol}, Ways: {Ways}, Ways factor list: {Ways_factor_list} x {base_payout}, OAKs: {OAKs}, Payout: {payout}")
        if payout <= 0:
            return "", 0

        payout_string += f"{symbol}: {Ways:,} Ways ({' x '.join([str(x) for x in Ways_factor_list])}) x {base_payout} ({OAKs} OAKs)"
        # print(payout_string)
        if symbol[0] == "H" and self.high_multiplier[int(symbol[1]) - 1] > 1:
            payout_string += f" x {self.high_multiplier[int(symbol[1]) - 1]} Symbol Multiplier"
        if self.global_multiplier > 1:
            payout_string += f" x {self.global_multiplier} Global Multiplier"
        payout_string += f" = {(payout):,}"
        return payout_string, payout



