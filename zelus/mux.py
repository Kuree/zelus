from kratos import Generator, PortDirection, SwitchStmt, CombinationalCodeBlock
from zelus.util import clog2
import math
from zelus.decoder import OneHotDecoder


class AOIMux(Generator):
    def __init__(self, height: int, width: int):
        name = "AOIMux_{0}_{1}".format(height, width)
        super().__init__(name)

        if height < 1:
            height = 1
        self.height = height

        # pass through wires
        if height == 1:
            self.in_ = self.port("I", width, PortDirection.In)
            self.out_ = self.port("O", width, PortDirection.Out)
            self.wire(self.out_, self.in_)
            return

        # based on Ankita's aoi mux implementation
        num_sel = clog2(height)
        num_ops = int(math.ceil(height / 2))
        num_inputs = int(math.pow(2, num_sel))

        # declare inputs and output
        inputs = []
        for i in range(height):
            inputs.append(self.port("I{0}".format(i), width, PortDirection.In))
        sel = self.port("S", num_sel, PortDirection.In)
        output = self.port("O", width, PortDirection.Out)

        # intermediate signals
        int_outputs = []
        for i in range(num_ops):
            int_outputs.append(self.var("O{0}".format(i), width))
        out_sel = self.var("out_sel", num_inputs)

        # one hot decoder
        decoder = OneHotDecoder(height, num_inputs)
        self.add_child_generator("decoder", decoder)
        self.wire(decoder.ports.S, sel)
        self.add_stmt(out_sel.assign(decoder.ports.O))

        for w in range(width):
            max_range = int(math.floor(height / 2))
            for i in range(max_range):
                # O_i[w] = (out_sel[i * 2] & I_{i * 2}[w]) |
                # (out_sel[i * 2 + 1] & I_{i * 2 + 1}[w])
                self.wire(int_outputs[i][w],
                          (out_sel[i * 2] & inputs[i * 2][w]) | out_sel[
                              i * 2 + 1] & inputs[i * 2 + 1][w])
            if height % 2:
                self.wire(int_outputs[max_range][w],
                          out_sel[max_range * 2] & inputs[max_range * 2][w])

        # or all the int outputs up
        expr = int_outputs[0]
        for i in range(1, num_ops):
            expr = expr | int_outputs[i]
        self.wire(output, expr)


class Mux(Generator):
    def __init__(self, height: int, width: int):
        name = "Mux_{0}_{0}".format(width, height)
        super().__init__(name)

        if height < 1:
            height = 1
        self.height = height

        # pass through wires
        if height == 1:
            self.in_ = self.port("I", width, PortDirection.In)
            self.out_ = self.port("O", width, PortDirection.Out)
            self.wire(self.out_, self.in_)
            return

        self.sel_size = clog2(height)
        for i in range(height):
            self.port("I{0}".format(i), width, PortDirection.In)
        self.out_ = self.port("O", width, PortDirection.Out)
        self.port("S", self.sel_size, PortDirection.In)

        # add a case statement
        stmt = SwitchStmt(self.ports.S)
        for i in range(height):
            stmt.add_switch_case(self.const(i, self.sel_size),
                                 self.out_.assign(self.ports["I{0}".format(i)]))
        # add default
        stmt.add_switch_case(None, self.out_.assign(self.const(0, width)))
        comb = CombinationalCodeBlock(self)
        comb.add_stmt(stmt)
