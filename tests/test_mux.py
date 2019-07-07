from zelus import Mux, AOIMux
from kratos import verilog
import fault
import magma
import tempfile
import os
from hwtypes import BitVector
import random
import pytest


# unfortunately the magma based testing framework is very verbose
@pytest.mark.parametrize("mux_ctor", [Mux, AOIMux])
@pytest.mark.parametrize("height", [2, 3, 4, 5, 6, 7])
def test_mux(mux_ctor, height):
    width = 16
    num_tests = 100

    mux = mux_ctor(height, width)
    mod_src = verilog(mux)

    with tempfile.TemporaryDirectory() as tempdir:
        filename = os.path.join(tempdir, mux.name + ".sv")
        with open(filename, "w+") as f:
            for value in mod_src.values():
                f.write(value)
                f.write("\n")

        # import it as magma circuit
        circuit = magma.DefineFromVerilogFile(filename,
                                              target_modules=[mux.name],
                                              shallow=True)[0]

        tester = fault.Tester(circuit)

        tester.zero_inputs()

        test_data = []
        for _ in range(num_tests):
            data_point = []
            for i in range(height):
                data_point.append(BitVector.random(width))
            # select
            sel = random.randrange(height)
            output = data_point[sel]
            data_point += [sel, output]
            test_data.append(data_point)

        for entry in test_data:
            for i in range(height):
                tester.poke(circuit.interface["I{0}".format(i)], entry[i])
            tester.poke(circuit.S, entry[height])
            tester.eval()
            tester.expect(circuit.O, entry[-1])

        tester.compile_and_run(target="verilator",
                               skip_compile=True,
                               directory=tempdir,
                               flags=["-Wno-fatal"])
