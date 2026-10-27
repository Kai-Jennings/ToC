class TM:
    def __init__(self, tape):
        self.tape = list(tape)
        self.ptr = 0
        self.cntr = 0
        self.state = "⎆"
        self.blank_sym = "·"
        self.lang_set = {"[", "]", ",", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"}
        self.transitions = {
            "⎆": self.start,
            "✔": self.accepting_state,
            "comp_asc_begin": self.comp_asc_begin,
            "comp_dsc_begin": self.comp_dsc_begin,
            "swap_dsc_begin": self.swap_dsc_begin,
            "goto_next_elem_comp": self.goto_next_elem_comp,
            "goto_curr_elem_comp": self.goto_curr_elem_comp,
            "goto_next_elem_swap": self.goto_next_elem_swap,
            "goto_curr_elem_swap": self.goto_curr_elem_swap,
            "goto_start": self.goto_start,
            "goto_prev_2": self.goto_prev_2,
            "goto_prev_1": self.goto_prev_1,
            "goto_prev_0": self.goto_prev_0
        }
        self.debug = ["⎆"]
        self.__gen_transitions__()
        self.run()

    def __gen_transitions__(self):
        for character in self.lang_set - {"[", "]", ","}:
            for direction in ["asc", "dsc"]:
                for step in range(1, 17):
                    def __gen_comp_wrapper__(d=direction, c=character, s=step):
                        def __gen_comp__():
                            char = self.read()
                            if s == 1 and d == "asc" and char == "]":  # change later maybe
                                self.state = "goto_start"
                                self.dec()
                            else:
                                self.state = f"comp_{d}_{c}_{s-1}"
                                if d == "asc":
                                    self.inc()
                                else:
                                    self.dec()
                        return __gen_comp__

                    self.transitions.update({f"comp_{direction}_{character}_{step}": __gen_comp_wrapper__()})

                    def __gen_swap_wrapper__(d=direction, c=character, s=step):
                        def __gen_swap__():
                            self.state = f"swap_{d}_{c}_{s-1}"
                            if d == "asc":
                                self.inc()
                            else:
                                self.dec()
                        return __gen_swap__

                    self.transitions.update({f"swap_{direction}_{character}_{step}": __gen_swap_wrapper__()})

            def __gen_comp_asc_final_wrapper__(c=character):
                def __gen_comp_asc_final__():
                    other = self.read()
                    if ord(c) < ord(other):
                        self.state = "goto_curr_elem_comp"
                        self.dec()
                    elif ord(c) > ord(other):
                        self.state = "goto_curr_elem_swap"
                        self.dec()
                    else:
                        self.state = "comp_dsc_begin"
                        self.inc()

                return __gen_comp_asc_final__

            self.transitions.update({f"comp_asc_{character}_0": __gen_comp_asc_final_wrapper__()})

            def __gen_comp_dsc_final_wrapper__(c=character):
                def __gen_comp_dsc_final__():
                    other = self.read()
                    if ord(other) < ord(c):
                        self.state = "goto_next_elem_comp"
                        self.inc()
                    elif ord(other) > ord(c):
                        self.state = "goto_next_elem_swap"
                        self.inc()
                    else:
                        self.state = "comp_asc_begin"
                        self.inc()

                return __gen_comp_dsc_final__

            self.transitions.update({f"comp_dsc_{character}_0": __gen_comp_dsc_final_wrapper__()})

            def __gen_swap_asc_final_wrapper__(c=character):
                def __gen_swap_asc_final__():
                    self.write(c)
                    self.state = "swap_dsc_begin"
                    self.inc()

                return __gen_swap_asc_final__

            self.transitions.update({f"swap_asc_{character}_0": __gen_swap_asc_final_wrapper__()})

            def __gen_swap_dsc_final_wrapper__(c=character):
                def __gen_swap_dsc_final__():
                    other = self.read()
                    self.write(c)
                    self.state = f"swap_asc_{other}_16"
                    self.inc()

                return __gen_swap_dsc_final__

            self.transitions.update({f"swap_dsc_{character}_0": __gen_swap_dsc_final_wrapper__()})

    def inc(self):
        self.ptr += 1

    def dec(self):
        self.ptr -= 1

    def read(self):
        if self.ptr < 0:
            self.halt("ERROR: negative pointer")
        return self.tape[self.ptr]  # no oob blank for now

    def write(self, sym):
        self.tape[self.ptr] = sym

    def halt(self, msg):
        self.debug.append(f"HALT({msg}) halted in {self.cntr} steps")
        self.print_debug()
        self.print_tape()
        exit()

    def print_debug(self):
        print("\nDEBUG TRANSITIONS:")
        print("\n⤷ ".join(self.debug))

    def print_tape(self):
        print("".join(self.tape))
        print(" " * self.ptr + f"^ {self.ptr} \"{self.read()}\"")

    def run(self):
        while True:
            self.cntr += 1
            self.transitions[self.state]()
            # self.debug.append(self.state)

    def start(self):
        self.state = "comp_asc_begin"
        self.inc()

    def comp_asc_begin(self):
        char = self.read()
        if char == "]":
            self.state = "goto_start"
            self.dec()
        elif char == ",":
            self.inc()
        else:
            self.state = f"comp_asc_{char}_16"
            self.inc()

    def comp_dsc_begin(self):
        char = self.read()
        self.state = f"comp_dsc_{char}_16"
        self.dec()

    def swap_dsc_begin(self):
        char = self.read()
        if char == "," or char == "]":
            self.state = "goto_prev_2"
            self.dec()
        else:
            self.state = f"swap_dsc_{char}_16"
            self.dec()

    def goto_next_elem_comp(self):
        char = self.read()
        if char == "]":
            self.state = "goto_start"
            self.dec()
        elif char == ",":
            self.state = "comp_asc_begin"
            self.inc()
        else:
            self.inc()

    def goto_curr_elem_comp(self):
        char = self.read()
        if char == ",":
            self.state = "comp_asc_begin"
            self.inc()
        else:
            self.dec()

    def goto_next_elem_swap(self):
        char = self.read()
        if char == ",":
            self.state = "swap_dsc_begin"
            self.inc()
        else:
            self.inc()

    def goto_curr_elem_swap(self):
        char = self.read()
        if char == ",":
            self.state = "swap_dsc_begin"
            self.inc()
        else:
            self.dec()

    def goto_start(self):
        char = self.read()
        if char == "[":
            self.state = "✔"
        else:
            self.dec()

    def goto_prev_2(self):
        char = self.read()
        if char == ",":
            self.state = "goto_prev_1"
            self.dec()
        else:
            self.dec()

    def goto_prev_1(self):
        char = self.read()
        if char == "[":
            self.state = "comp_asc_begin"
            self.inc()
        elif char == ",":
            self.state = "goto_prev_0"
            self.dec()
        else:
            self.dec()

    def goto_prev_0(self):
        char = self.read()
        if char == "," or char == "[":
            self.state = "comp_asc_begin"
            self.inc()
        else:
            self.dec()

    def accepting_state(self):
        self.halt("Accepting State")
