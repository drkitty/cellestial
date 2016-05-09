#!/usr/bin/env python3


from time import sleep


CELL_MEM_SIZE = 256

N = 0
E = 1
S = 2
W = 3
ME = 4

SET  = 0  # A <- imm
ROT  = 1  # Z <- Y <- X <- A <- Z
IN   = 2  # A <- (X)
OUT  = 3  # (X) <- A
ADD  = 4  # A <- A + X
AT   = 5  # T <- A
BR   = 6  # P <- P + imm
INIT = 7  # A, X, Y, Z, P <- 0 ; T <- ME ; (P) <- INIT


class Cell(object):
    a = p = x = y = z = 0
    t = ME

    def __init__(self):
        self.mem = [INIT] * CELL_MEM_SIZE

    def inc_p(self):
        self.p = (self.p + 1) % CELL_MEM_SIZE


class World(object):
    def __init__(self, xwyw):
        xw, yw = xwyw
        self.xw = xw
        self.yw = yw
        self.cells = [[None] * xw for _ in range(yw)]

    def target(self, xy):
        x, y = xy
        c = self.cells[x][y]
        if c.t == N:
            return (x, 0 if (y == self.yw - 1) else (y + 1))
        elif c.t == E:
            return (0 if (x == self.xw - 1) else (x + 1), y)
        elif c.t == S:
            return (x, (self.yw - 1) if (y == 0) else (y - 1))
        elif c.t == W:
            return ((self.xw - 1) if (x == 0) else (x - 1), y)
        else:  # ME
            return (x, y)

    def step(self):
        chgs = []
        for x in range(self.xw):
            for y in range(self.yw):
                if self.cells[x][y] is None:
                    continue
                chg = self.cell_step((x, y))
                if chg is not None:
                    chgs.append(chg)
        for chg in chgs:
            c, addr, val = chg
            c.mem[addr] = val


    def cell_step(self, xy):
        x, y = xy
        c = self.cells[x][y]
        insn = c.mem[c.p]
        c.inc_p()

        if insn == SET:
            c.a = c.mem[c.p]
            c.inc_p()
        elif insn == ROT:
            temp = c.z
            c.z = c.y
            c.y = c.x
            c.x = c.a
            c.a = temp
        elif insn == IN:
            tx, ty = self.target((x, y))
            target = self.cells[tx][ty]
            if target is None:
                c.a = INIT
            else:
                c.a = target.mem[c.x]
        elif insn == OUT:
            tx, ty = self.target((x, y))
            target = self.cells[tx][ty]
            if target is None:
                target = self.cells[tx][ty] = Cell()
            return (target, c.x, c.a)
        elif insn == ADD:
            c.a = (c.a + c.x) % CELL_MEM_SIZE
        elif insn == AT:
            c.t = c.a
        elif insn == BR:
            c.p = (c.p + c.a) % CELL_MEM_SIZE
        else:  # INIT
            c.a = c.x = c.y = c.z = c.p = 0
            c.t = ME
            return (c, 0, INIT)


def test():
    w = World((3, 3))

    c = w.cells[1][1] = Cell()
    c.mem = [
        # A X Y Z  T
        # 0 . a 0  ME
        SET, 4,
        # 4 . a 0  ME
        ROT,
        # 0 4 . a  ME
        SET, 1,
        # 1 4 . a  ME
        ROT,
        # a 1 4 .  ME
        ROT,
        # . a 1 4  ME
        IN,
        # ? a 1 4  ME
        ROT,
        # 4 ? a 1  ME
        ROT,
        # 1 4 ? a  ME
        AT,
        # 1 4 ? a  E
        ROT,
        # a 1 4 ?  E
        ROT,
        # ? a 1 4  E
        OUT,
        # . a 1 4  E
        ROT,
        # 4 . a 1  E
        AT,
        # 4 . a 1  ME
        ROT,
        # 1 4 . a  ME
        ROT,
        # a 1 4 .  ME
        ADD,
        # a 1 4 .  ME
        ROT,
        # . a 1 4  ME
        SET, CELL_MEM_SIZE - 1 - 15,
        # f a 1 4  ME
        BR,
    ]
    c.mem += [INIT] * (CELL_MEM_SIZE - len(c.mem))

    while True:
        print(c.a, c.x, c.y, c.z, c.t)
        print(w.cells)
        w.step()
        sleep(0.1)


if __name__ == '__main__':
    test()
