from kratos import Generator, PortDirection, CombinationalCodeBlock, SwitchStmt
from kratos.util import clog2


class OneHotDecoder(Generator):
    def __init__(self, num_case: int, output_size: int):
        name = "Decoder_{0}_{1}".format(num_case, output_size)
        super().__init__(name)

        self.num_case = num_case
        self.sel_size = clog2(num_case)
        self.output_size = output_size

        if self.num_case > self.output_size:
            raise ValueError(
                "output_size {0} cannot be smaller than num_cases {1}".format(
                    output_size, num_case))

        # input
        self.select = self.port("S", self.sel_size, PortDirection.In)
        self.output = self.port("O", self.output_size, PortDirection.Out)

        # use procedural python code to generate the code
        comb = self.combinational()
        switch = comb.switch_(self.select)
        # adding cases
        for i in range(self.num_case):
            switch.case_(self.const(i, self.sel_size),
                         self.output(1 << i))
        # add a default case
        switch.case_(None, self.output(0))
