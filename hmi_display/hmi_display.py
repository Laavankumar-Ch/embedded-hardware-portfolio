import pyb
import utime

LOCAL_REG = 199
SID_IO = 200
HOLDING = 0
HMI_Color_Status = 12002
HMI_INPUT_REG = 12001
DISPLAY_ON_REG = 1051
DISPLAY_MODE_REG = 1052
DISPLAY_COLOR_REG = 1053
DISPLAY_TEXT = 1055
TEXT_REGS = 13                  # 2 characters per register
TEXT_CHARS = TEXT_REGS * 2

# HMI_Input -> (colour register value, text shown). Text is "" where none was specified.
HMI_MAP = {
    4: (1, "GREEN"),
    1: (2, ""),
    2: (5, ""),
    8: (10, ""),
}

_last_input = None


def Display_line(line_1_msg):
    pyb.setreg(DISPLAY_ON_REG, 1, LOCAL_REG, HOLDING)
    characters = list(line_1_msg[:TEXT_CHARS])
    characters += ["\0"] * (TEXT_CHARS - len(characters))
    register_values = []

    for index in range(0, TEXT_CHARS, 2):
        register_values.append(
            (ord(characters[index]) << 8) | ord(characters[index + 1])
        )
    pyb.multiset(DISPLAY_TEXT, register_values, LOCAL_REG, HOLDING)


def clear_s100():
    pyb.setreg(DISPLAY_MODE_REG, 0, SID_IO, HOLDING)
    pyb.multiset(DISPLAY_TEXT, [0] * TEXT_REGS, SID_IO, HOLDING)
    pyb.multiset(DISPLAY_COLOR_REG, [0] * 16, SID_IO, HOLDING)


# Runs every timestep
def step():
    global _last_input

    pyb.setreg(DISPLAY_ON_REG, 1, LOCAL_REG, HOLDING)

    HMI_Input = pyb.getreg(HMI_INPUT_REG, LOCAL_REG, HOLDING)
    if HMI_Input == _last_input:
        return                  # nothing changed, avoid rewriting registers
    _last_input = HMI_Input

    if HMI_Input in HMI_MAP:
        color, text = HMI_MAP[HMI_Input]
        pyb.setreg(DISPLAY_MODE_REG, 256, LOCAL_REG, HOLDING)
        pyb.setreg(DISPLAY_COLOR_REG, color, LOCAL_REG, HOLDING)
        Display_line(text)
    else:
        clear_s100()


if __name__ == '__main__':
    while True:
        step()
        utime.sleep_ms(50)
