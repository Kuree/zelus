from kratos import Generator, always, PortDirection, PortType, BlockEdgeType


class Register(Generator):
    def __init__(self, width, init_value: int = 0, has_ce: bool = True,
                 is_clone: bool = False):
        if has_ce:
            name = "Register{0}CE".format(width)
        else:
            name = "Register{0}".format(width)

        super().__init__(name, is_clone=is_clone)

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


class ConfigRegister(Generator):
    def __init__(self, width, addr_width, data_width, use_config_en,
                 is_clone: bool = False):
        if use_config_en:
            name = "ConfigRegister{0}CE".format(width)
        else:
            name = "ConfigRegister{0}".format(width)

        super().__init__(name, is_clone=is_clone)

        self.width = width
        self.use_config_en = use_config_en

        # addr param
        self.parameter("addr", addr_width)

        # define port
        self.config_addr = self.port("config_addr", addr_width,
                                     PortDirection.In)
        self.config_data = self.port("config_data", data_width,
                                     PortDirection.In)
        self.output = self.port("O", width, PortDirection.Out)
        self.clk = self.port("clk", 1, PortDirection.In, PortType.Clock)
        self.reset = self.port("reset", 1, PortDirection.In,
                               PortType.AsyncReset)
        if use_config_en:
            self.port("config_en", 1, PortDirection.In)

        self.value = self.var("value", width)

        self.ce = self.port("clk_en", 1, PortDirection.In, PortType.ClockEnable)

        # wiring
        self.wire(self.output, self.value)

        # add code
        if self.use_config_en:
            self.add_code(self.code_config_en)
        else:
            self.add_code(self.code)

    @always([(BlockEdgeType.Posedge, "clk"), (BlockEdgeType.Posedge, "reset")])
    def code_config_en(self):
        if self.reset:
            self.value = 0
        elif self.ce & (self.ports.config_addr.eq(self.params.addr)):
            if self.ports.config_en:
                self.value = self.ports.config_data[self.width - 1, 0]

    @always([(BlockEdgeType.Posedge, "clk"), (BlockEdgeType.Posedge, "reset")])
    def code(self):
        if self.reset:
            self.value = 0
        elif self.ce & (self.ports.config_addr.eq(self.params.addr)):
            self.value = self.ports.config_data[self.width - 1, 0]
