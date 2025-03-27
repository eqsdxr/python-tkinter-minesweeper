# Python Version 2.7.3
# File: minesweeper.py

from tkinter import *
from tkinter import messagebox as tkMessageBox
from collections import deque
import random
import platform
import time
from datetime import time, date, datetime

DEFAULT_SIZE_X = 10
DEFAULT_SIZE_Y = 10
DEFAULT_MINE_AMOUNT = 10

STATE_DEFAULT = 0
STATE_CLICKED = 1
STATE_FLAGGED = 2


BTN_CLICK = "<Button-1>"
BTN_FLAG = "<Button-2>" if platform.system() == "Darwin" else "<Button-3>"

window = None


class Minesweeper:
    def __init__(self, tk, mine_amount, size_x, size_y):
        # import images
        self.images = {
            "plain": PhotoImage(file="images/tile_plain.gif"),
            "clicked": PhotoImage(file="images/tile_clicked.gif"),
            "mine": PhotoImage(file="images/tile_mine.gif"),
            "flag": PhotoImage(file="images/tile_flag.gif"),
            "wrong": PhotoImage(file="images/tile_wrong.gif"),
            "numbers": [],
        }
        for i in range(1, 9):
            self.images["numbers"].append(
                {"value": i, "image": PhotoImage(file="images/tile_" + str(i) + ".gif")}
            )

        # set up frame
        self.tk = tk
        self.frame = Frame(self.tk)
        self.frame.pack()
        self.size_x = size_x
        self.size_y = size_y
        self.mine_amount = mine_amount

        if self.mine_amount > (self.size_x * self.size_y):
            raise ValueError("Amount of mines can't exceed amount of tiles")

        # set up labels/UI
        self.labels = {
            "time": Label(self.frame, text="00:00:00"),
            "score": Label(self.frame, text="Score: 0"),
            "mines": Label(self.frame, text="Mines: 0"),
            "flags": Label(self.frame, text="Flags: 0"),
        }
        self.labels["time"].grid(
            row=0, column=0, columnspan=int(self.size_y / 2)
        )  # top full width
        self.labels["score"].grid(
            row=0, column=int(self.size_y / 2), columnspan=int(self.size_y / 2)
        )  # top full width
        self.labels["mines"].grid(
            row=self.size_x + 1, column=0, columnspan=int(self.size_y / 2)
        )  # bottom left
        self.labels["flags"].grid(
            row=self.size_x + 1,
            column=int(self.size_y / 2) - 1,
            columnspan=int(self.size_y / 2),
        )  # bottom right

        self.restart()  # start game
        self.updateTimer()  # init timer

    def setup(self):
        # create flag and clicked tile variables
        self.flagCount = 0
        self.correctFlagCount = 0
        self.clickedCount = 0
        self.startTime = None

        self.score = 0

        # create buttons
        self.tiles = dict({})
        self.mine_amount = self.mine_amount
        for x in range(0, self.size_x):
            for y in range(0, self.size_y):
                if y == 0:
                    self.tiles[x] = {}

                id = str(x) + "_" + str(y)

                # tile image changeable for debug reasons:
                gfx = self.images["plain"]

                tile = {
                    "id": id,
                    "isMine": False,
                    "state": STATE_DEFAULT,
                    "coords": {"x": x, "y": y},
                    "button": Button(self.frame, image=gfx),
                    "mines": 0,  # calculated after grid is built
                }

                tile["button"].bind(BTN_CLICK, self.onClickWrapper(x, y))
                tile["button"].bind(BTN_FLAG, self.onRightClickWrapper(x, y))
                tile["button"].grid(row=x + 1, column=y)  # offset by 1 row for timer

                self.tiles[x][y] = tile

        self.seed_mines()

        # loop again to find nearby mines and display number on tile
        for x in range(0, self.size_x):
            for y in range(0, self.size_y):
                mc = 0
                for n in self.getNeighbors(x, y):
                    mc += 1 if n["isMine"] else 0
                self.tiles[x][y]["mines"] = mc

    def get_input(self):
        pass

    # seed predefined amount of mines into tiles
    def seed_mines(self):
        mines_left = self.mine_amount
        while mines_left > 0:
            for x in range(0, self.size_x):
                for y in range(0, self.size_y):
                    if mines_left < 1:
                        return

                    cond1 = random.uniform(0.0, 1.0) < 0.1
                    cond2 = self.tiles[x][y]["isMine"] is False
                    if cond1 and cond2:
                        self.tiles[x][y]["isMine"] = True
                        mines_left -= 1

    def restart(self):
        self.setup()
        self.refreshLabels()

    def refreshLabels(self):
        self.labels["flags"].config(text="Flags: " + str(self.flagCount))
        self.labels["mines"].config(text="Mines: " + str(self.mine_amount))
        self.labels["score"].config(text="Score: " + str(self.score))

    def gameOver(self, won):
        for x in range(0, self.size_x):
            for y in range(0, self.size_y):
                if (
                    self.tiles[x][y]["isMine"] == False
                    and self.tiles[x][y]["state"] == STATE_FLAGGED
                ):
                    self.tiles[x][y]["button"].config(image=self.images["wrong"])
                if (
                    self.tiles[x][y]["isMine"] == True
                    and self.tiles[x][y]["state"] != STATE_FLAGGED
                ):
                    self.tiles[x][y]["button"].config(image=self.images["mine"])

        self.tk.update()

        msg = "You Win! Play again?" if won else "You Lose! Play again?"
        res = tkMessageBox.askyesno("Game Over", msg)
        if res:
            self.restart()
        else:
            self.tk.quit()

    def updateTimer(self):
        ts = "00:00:00"
        if self.startTime != None:
            delta = datetime.now() - self.startTime
            ts = str(delta).split(".")[0]  # drop ms
            if delta.total_seconds() < 36000:
                ts = "0" + ts  # zero-pad
        self.labels["time"].config(text=ts)
        self.frame.after(100, self.updateTimer)

    def getNeighbors(self, x, y):
        neighbors = []
        coords = [
            {"x": x - 1, "y": y - 1},  # top right
            {"x": x - 1, "y": y},  # top middle
            {"x": x - 1, "y": y + 1},  # top left
            {"x": x, "y": y - 1},  # left
            {"x": x, "y": y + 1},  # right
            {"x": x + 1, "y": y - 1},  # bottom right
            {"x": x + 1, "y": y},  # bottom middle
            {"x": x + 1, "y": y + 1},  # bottom left
        ]
        for n in coords:
            try:
                neighbors.append(self.tiles[n["x"]][n["y"]])
            except KeyError:
                pass
        return neighbors

    def onClickWrapper(self, x, y):
        return lambda Button: self.onClick(self.tiles[x][y])

    def onRightClickWrapper(self, x, y):
        return lambda Button: self.onRightClick(self.tiles[x][y])

    def onClick(self, tile):
        if self.startTime == None:
            self.startTime = datetime.now()

        if tile["isMine"] == True:
            # end game
            self.gameOver(False)
            return

        # change image
        if tile["mines"] == 0:
            tile["button"].config(image=self.images["clicked"])
            self.clearSurroundingTiles(tile["id"])
        else:
            tile["button"].config(
                image=self.images["numbers"][tile["mines"] - 1]["image"]
            )
            # update score
            self.score += self.images["numbers"][tile["mines"] - 1]["value"]
            self.refreshLabels()
        # if not already set as clicked, change state and count
        if tile["state"] != STATE_CLICKED:
            tile["state"] = STATE_CLICKED
            self.clickedCount += 1
        if self.clickedCount == (self.size_x * self.size_y) - self.mine_amount:
            self.gameOver(True)

    def onRightClick(self, tile):
        if self.startTime == None:
            self.startTime = datetime.now()

        # if not clicked
        if tile["state"] == STATE_DEFAULT:
            tile["button"].config(image=self.images["flag"])
            tile["state"] = STATE_FLAGGED
            tile["button"].unbind(BTN_CLICK)
            # if a mine
            if tile["isMine"] == True:
                self.correctFlagCount += 1
            self.flagCount += 1
            self.refreshLabels()
        # if flagged, unflag
        elif tile["state"] == 2:
            tile["button"].config(image=self.images["plain"])
            tile["state"] = 0
            tile["button"].bind(
                BTN_CLICK, self.onClickWrapper(tile["coords"]["x"], tile["coords"]["y"])
            )
            # if a mine
            if tile["isMine"] == True:
                self.correctFlagCount -= 1
            self.flagCount -= 1
            self.refreshLabels()

    def clearSurroundingTiles(self, id):
        queue = deque([id])

        while len(queue) != 0:
            key = queue.popleft()
            parts = key.split("_")
            x = int(parts[0])
            y = int(parts[1])

            for tile in self.getNeighbors(x, y):
                self.clearTile(tile, queue)

    def clearTile(self, tile, queue):
        if tile["state"] != STATE_DEFAULT:
            return

        if tile["mines"] == 0:
            tile["button"].config(image=self.images["clicked"])
            queue.append(tile["id"])
        else:
            tile["button"].config(
                image=self.images["numbers"][tile["mines"] - 1]["image"]
            )
            # update score by counting surrounding tiles
            self.score += self.images["numbers"][tile["mines"] - 1]["value"]
            self.refreshLabels()

        tile["state"] = STATE_CLICKED
        self.clickedCount += 1


### END OF CLASSES ###


def main():
    # Get user input
    mine_amount = DEFAULT_MINE_AMOUNT
    size_x = DEFAULT_SIZE_X
    size_y = DEFAULT_SIZE_Y

    def save_input():
        nonlocal mine_amount
        nonlocal size_x
        nonlocal size_y

        try:
            mine_amount = int(entry_mines_amount.get())
            size_x = int(entry_x.get())
            size_y = int(entry_y.get())
        except ValueError:
            tkMessageBox.showerror("Error", "All values should be integers!")
            return

        if mine_amount > (size_x * size_y):
            tkMessageBox.showerror(
                "Error", "Amount of mines can't exceed amount of tiles"
            )
            return


        if not size_x or not size_y or not mine_amount:
            tkMessageBox.showerror("Error", "All fields are required!")
            return
        input_window.destroy()

    input_window = Tk()
    input_window.title("Start Minesweeper")
    input_window.geometry("400x300")
    Label(window, text="Enter amount of mines:").pack()
    entry_mines_amount = Entry(window)
    entry_mines_amount.pack()
    Label(window, text="Enter x:").pack()
    entry_x = Entry(window)
    entry_x.pack()
    Label(window, text="Enter y:").pack()
    entry_y = Entry(window)
    entry_y.pack()
    Button(window, text="Play", command=save_input).pack(pady=10)
    input_window.mainloop()

    # Start the game

    # create Tk instance
    game_window = Tk()
    # set program title
    game_window.title("Minesweeper")
    # create game instance
    minesweeper = Minesweeper(game_window, mine_amount, size_x, size_y)
    # run event loop
    game_window.mainloop()


if __name__ == "__main__":
    main()
