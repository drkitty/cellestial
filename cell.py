#!/usr/bin/env python3


from time import sleep


CELL_MEM_SIZE = 256

M = 0
N = 1
E = 2
S = 3
W = 4

INIT = 0  # A, X, Y, Z, P <- 0 ; T <- M ; (P) <- INIT
SET  = 1  # A <- imm
ROT  = 2  # Z <- Y <- X <- A <- Z
IN   = 3  # A <- (X)
OUT  = 4  # (X) <- A
ADD  = 5  # A <- A + X
AT   = 6  # T <- A
BR   = 7  # P <- P + A if X == Y

INSN_COUNT = 8


class Cell(object):
    a = p = x = y = z = 0
    t = M

    def __init__(self):
        self.mem = [INIT] * CELL_MEM_SIZE

    def __str__(self):
        return '<Cell: {:02X} {:02X} {:02X} {:02X}  {:02X}>'.format(
            self.a, self.x, self.y, self.z, self.t
        )

    @property
    def insn_str(self):
        insn = self.mem[self.p] % INSN_COUNT
        if insn == SET:
            return "SET {}".format(self.mem[self.p + 1])
        else:
            return {
                INIT: "INIT",
                ROT: "ROT",
                IN: "IN",
                OUT: "OUT",
                ADD: "ADD",
                AT: "AT",
                BR: "BR",
            }[insn]

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
            tx, ty = (x, 0 if (y == self.yw - 1) else (y + 1))
        elif c.t == E:
            tx, ty = (0 if (x == self.xw - 1) else (x + 1), y)
        elif c.t == S:
            tx, ty = (x, (self.yw - 1) if (y == 0) else (y - 1))
        elif c.t == W:
            tx, ty = ((self.xw - 1) if (x == 0) else (x - 1), y)
        else:  # M
            tx, ty = (x, y)
        cc = self.cells[tx][ty]
        if cc is None:
            cc = self.cells[tx][ty] = Cell()
        return cc

    def step(self):
        chgs = []
        for x in range(self.xw):
            for y in range(self.yw):
                if self.cells[x][y] is not None:
                    chg = self.cell_step((x, y))
                    if chg is not None:
                        chgs.append(chg)
        for chg in chgs:
            c, addr, val = chg
            c.mem[addr] = val


    def cell_step(self, xy):
        x, y = xy
        c = self.cells[x][y]
        insn = c.mem[c.p] % INSN_COUNT
        c.inc_p()

        if insn == INIT:
            cc = self.target((x, y))
            cc.a = cc.x = cc.y = cc.z = cc.p = 0
            cc.t = M
            return (cc, 0, INIT)
        elif insn == SET:
            c.a = c.mem[c.p]
            c.inc_p()
        elif insn == ROT:
            temp = c.z
            c.z = c.y
            c.y = c.x
            c.x = c.a
            c.a = temp
        elif insn == IN:
            cc = self.target((x, y))
            c.a = cc.mem[c.x]
        elif insn == OUT:
            cc = self.target((x, y))
            return (cc, c.x, c.a)
        elif insn == ADD:
            c.a = (c.a + c.x) % CELL_MEM_SIZE
        elif insn == AT:
            c.t = c.a
        elif insn == BR:
            if c.x == c.y:
                c.p = (c.p + c.a) % CELL_MEM_SIZE
        else:
            raise Exception("BUG")


def test():
    w = World((3, 3))

    c = w.cells[1][1] = Cell()
    c.mem = [
        # A X Y Z  T

        # . . . 0  M
        SET, 1,
        AT,
        # 1 . . 0  N
        INIT,
        # 1 . . 0  N
        ROT,
        # 0 1 . .  N
        AT,
        # 0 1 . .  M
        ROT,
        ROT,

        ROT,
        ROT,
        # . a . .  M
        IN,
        # d a . .  M
        ROT,
        # . d a .  M
        SET, N,
        AT,
        # . d a .  N
        ROT,
        ROT,
        ROT,
        # d a . .  N
        OUT,
        # . a . .  N
        SET, M,
        AT,
        # . a . .  M
        ROT, ROT,
        # . . . a  M
        SET, 1,
        # 1 . . a  M
        ROT,
        # a 1 . .  M
        ADD,
        # a . . .  M
        ROT,
        # . a . .  M
        SET, 0,
        # 0 a . .  M
        ROT,
        # . 0 a .  M
        SET, 6,
        BR,
        # . 0 a .  M
        SET, 0,
        # 0 0 a .  M
        ROT,
        # . 0 0 a  M
        SET, CELL_MEM_SIZE - 33,
        BR,

        SET, 0,
        # 0 . . .  M
        ROT,
        # . 0 . .  M
        IN,
        # d 0 . .  M
        ROT,
        # . d 0 .  M
        SET, N,
        AT,
        # . d 0 .  N
        ROT,
        ROT,
        ROT,
        # d 0 . .  N
        OUT,
        # . 0 . .  N
        SET, 0,
        # 0 0 . .  N
        ROT,
        # . 0 0 .  N
        SET, CELL_MEM_SIZE - 1,
        BR,
    ]
    c.mem += [INIT] * (CELL_MEM_SIZE - len(c.mem))

    cc = w.cells[1][2] = Cell()

    while True:
        print(c)
        print(c.insn_str)
        #print(cc.mem)
        w.step()
        sleep(0.1)


if __name__ == '__main__':
    test()
