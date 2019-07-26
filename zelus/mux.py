from kratos import Generator, PortDirection, SwitchStmt, CombinationalCodeBlock
from kratos.util import clog2, reduce_or
import math
from zelus.decoder import OneHotDecoder


class AOIMux(Generator):
    def __init__(self, height: int, width: int, is_clone: bool = False):
        name = "AOIMux_{0}_{1}".format(height, width)
        super().__init__(name, is_clone=is_clone)

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
        self.add_stmt(out_sel(decoder.ports.O))

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
        expr = reduce_or(int_outputs)
        self.wire(output, expr)


class Mux(Generator):
    def __init__(self, height: int, width: int, is_clone: bool = False):
        name = "Mux_{0}_{1}".format(width, height)
        super().__init__(name, is_clone=is_clone)

        # pass through wires
        if height == 1:
            self.in_ = self.port("I", width, PortDirection.In)
            self.out_ = self.port("O", width, PortDirection.Out)
            self.wire(self.out_, self.in_)
            return

        self.sel_size = clog2(height)
        ports = [self.port("I{0}".format(i), width,
                           PortDirection.In) for i in range(height)]
        self.out_ = self.port("O", width, PortDirection.Out)
        self.port("S", self.sel_size, PortDirection.In)

        # add a combinational block
        comb = self.combinational()

        # add a case statement
        switch_ = comb.switch_(self.ports.S)
        for i in range(height):
            switch_.case_(i, self.out_.assign(ports[i]))
        # add default
        switch_.case_(None, self.out_.assign(0))


class MuxDefault(Generator):
    def __init__(self, height: int, width: int, sel_bsize: int,
                 is_clone: bool = False):
        name = "MuxDefault_{0}_{1}".format(width, height)
        super().__init__(name, is_clone=is_clone)
        default = self.parameter("default_value", width)

        # pass through wires
        if height == 1:
            self.in_ = self.port("I", width, PortDirection.In)
            self.out_ = self.port("O", width, PortDirection.Out)
            self.wire(self.out_, self.in_)
            return

        self.sel_size = sel_bsize
        ports = [self.port("I{0}".format(i), width,
                           PortDirection.In) for i in range(height)]
        self.out_ = self.port("O", width, PortDirection.Out)
        self.port("S", self.sel_size, PortDirection.In)

        # add a combinational block
        comb = self.combinational()

        # add a case statement
        switch_ = comb.switch_(self.ports.S)
        for i in range(height):
            switch_.case_(i, self.out_.assign(ports[i]))
        # add default
        switch_.case_(None, self.out_.assign(default))
