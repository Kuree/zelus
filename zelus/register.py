from kratos import Generator, always, PortDirection, PortType, BlockEdgeType


class Register(Generator):
    def __init__(self, width, init_value: int = 0, has_ce: bool = True):
        if has_ce:
            name = "Register{0}CE".format(width, init_value)
        else:
            name = "Register{0}".format(width, init_value)

        super().__init__(name, False)

        self.width = width

        # define port
        self.input = self.port("I", width, PortDirection.In)
        self.output = self.port("O", width, PortDirection.Out)
        self.clk = self.port("clk", 1, PortDirection.In, PortType.Clock)
        self.reset = self.port("reset", 1, PortDirection.In,
                               PortType.AsyncReset)

        self.value = self.var("value", width)

        if has_ce:
            self.ce = self.port("clk_en", 1, PortDirection.In,
                                PortType.ClockEnable)

        self.init_value = self.parameter("init", width)
        self.init_value.set_value(init_value)

        # wiring
        self.wire(self.output, self.value)

        # add code
        if has_ce:
            self.add_code(self.ce_code)
        else:
            self.add_code(self.no_ce_code)

    @always([(BlockEdgeType.Posedge, "clk"), (BlockEdgeType.Posedge, "reset")])
    def no_ce_code(self):
        if self.reset:
            self.value = self.init_value
        else:
            self.value = self.input

    @always([(BlockEdgeType.Posedge, "clk"), (BlockEdgeType.Posedge, "reset")])
    def ce_code(self):
        if self.reset:
            self.value = self.init_value
        elif self.ce:
            self.value = self.input
