from kratos import Generator, PortDirection, CombinationalCodeBlock, SwitchStmt
from zelus.util import clog2


class OneHotDecoder(Generator):
    def __init__(self, num_case: int, output_size: int):
        name = "Decoder_{0}_{1}".format(num_case, output_size)
        super().__init__(name)

        self.num_case = num_case
        self.sel_size = clog2(num_case)
        self.output_size = output_size

        # input
        self.select = self.port("S", self.sel_size, PortDirection.In)
        self.output = self.port("O", self.output_size, PortDirection.Out)

        # use procedural python code to generate the code
        stmt = SwitchStmt(self.select)
        # adding cases
        for i in range(self.num_case):
            one_hot_encoding = self.const(1 << i, self.output_size)
            stmt.add_switch_case(self.const(i, self.sel_size),
                                 self.output.assign(one_hot_encoding))
        # add a default case
        stmt.add_switch_case(None, self.output.assign(
            self.const(0, self.output_size)))
        # wrap that switch statement into a combinational stmt
        comb = CombinationalCodeBlock(self)
        comb.add_stmt(stmt)
