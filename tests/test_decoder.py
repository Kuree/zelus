from zelus import OneHotDecoder
from kratos import verilog
import fault
import magma
import tempfile
import os
import random


def test_one_hot_decoder():
    cases = 16
    num_tests = 10
    output_size = 20

    decoder = OneHotDecoder(cases, output_size)
    mod_src = verilog(decoder)

    with tempfile.TemporaryDirectory() as tempdir:
        filename = os.path.join(tempdir, decoder.name + ".sv")
        with open(filename, "w+") as f:
            for value in mod_src.values():
                f.write(value)
                f.write("\n")

        # import it as magma circuit
        circuit = magma.DefineFromVerilogFile(filename,
                                              target_modules=[decoder.name],
                                              shallow=True)[0]

        tester = fault.Tester(circuit)

        tester.zero_inputs()

        for i in range(num_tests):
            value = random.randrange(cases)
            tester.poke(circuit.S, value)
            tester.eval()
            tester.expect(circuit.O, 1 << value)

        tester.compile_and_run(target="verilator",
                               skip_compile=True,
                               directory=tempdir,
                               flags=["-Wno-fatal"])
