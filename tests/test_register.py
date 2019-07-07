from zelus import Register
from kratos import verilog
import fault
import magma
import tempfile
import os
from hwtypes import BitVector


def test_register():
    width = 16
    num_tests = 10
    init_value = BitVector.random(width)

    reg = Register(width, init_value)
    mod_src = verilog(reg)
    src = mod_src[reg.name]

    with tempfile.TemporaryDirectory() as tempdir:
        tempdir = "temp"

        filename = os.path.join(tempdir, reg.name + ".sv")
        with open(filename, "w+") as f:
            f.write(src)

        # import it as magma circuit
        circuit = magma.DefineFromVerilogFile(filename,
                                              type_map={
                                                  "clk": magma.In(magma.Clock),
                                                  "reset":
                                                      magma.In(
                                                          magma.AsyncReset)},
                                              target_modules=[reg.name],
                                              shallow=True)[0]

        tester = fault.Tester(circuit, circuit.clk)

        tester.zero_inputs()
        tester.poke(circuit.clk_en, 1)
        # test it with clk en signal
        data = [BitVector.random(width) for _ in range(num_tests)]
        for i in range(10):
            tester.poke(circuit.I, data[i])

            if i > 0:
                tester.expect(circuit.O, data[i - 1])

            tester.step(2)

        # test clock gating
        tester.poke(circuit.clk_en, 0)
        for i in range(10):
            tester.poke(circuit.I, BitVector.random(width))

            tester.step(2)
            tester.expect(circuit.O, data[num_tests - 1])

        tester.compile_and_run(target="verilator",
                               magma_output="coreir-verilog",
                               directory=tempdir,
                               flags=["-Wno-fatal"])
