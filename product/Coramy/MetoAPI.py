from Products.PythonScripts.Utility import allow_module
allow_module("Products.Coramy.MetoAPI")

XON  = "\x11"
XOFF = "\x13"
STX  = "\x02"
SOH  = "\x01"
ESC  = "\x1B"
LF   = "\x0A"
CR   = "\x0D"

def command(*args):
    raw_string = ''.join(args)
    return raw_string

def selectMeter():
    return command(STX, "m")

def setDecoration(active):
    if active:
        return command(STX, "V4")
    else:
        return command(STX, "V0")

def startFormat():
    return command(STX, "L")

def endFormat():
    return command("E", CR)

def setNumber(n = 1):
    return command("Q%04d" % n, CR)

def setTemparature(t = 15):
    return command("H%02d" % t)

def setPixel(width = 1, height = 1):
    return command("D%1d%1d" % (width, height))

def setPrintSpeed(s = "C"):
    return command("P", s)

def setAsdFont(s = "4"):
    return command("Kl<", s)

def setPaperSpeed(s = "C"):
    return command("S", s)

def printLine(rotation, x, y, width, height, unit = 1):
    return command("%1d" % rotation,
            "X11000",
            "%04d%04d" % (y * unit, x * unit),
            "l",
            "%04d%04d" % (width * unit, height * unit),
            CR)

def printText(rotation, font, horizontal_expansion, vertical_expansion,
               size, x, y, text, unit = 1):
    return command("%1d" % rotation,
            font,
            "%1d" % horizontal_expansion,
            "%1d" % vertical_expansion,
            "%03d" % size,
            "%04d%04d" % (y * unit, x * unit),
            text,
            CR)

def printFrame(rotation, x, y, width, height,
                thickness_of_horizontal_lines, thickness_of_vertical_lines,
                unit = 1):
    return command("%1d" % rotation,
            "X11000",
            "%04d%04d" % (y * unit, x * unit),
            "b",
            "%04d%04d" % (width * unit, height * unit),
            "%04d%04d" % (thickness_of_horizontal_lines,
                          thickness_of_vertical_lines),
            CR)
