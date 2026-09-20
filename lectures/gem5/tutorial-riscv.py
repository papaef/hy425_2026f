import m5
from m5.objects import *

# import cache classes
from tutorial_caches import *
# argument parser
args = SimpleOpts.parse_args()

system = System()

system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "1GHz"
system.clk_domain.voltage_domain = VoltageDomain()

system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MiB")]
# different types of CPU to use
system.cpu = RiscvMinorCPU()
#system.cpu = RiscvTimingSimpleCPU()
#system.cpu = RiscvO3CPU()

# employ caches
system.cpu.icache = L1ICache()
# with or without passing arguments to them
#system.cpu.dcache = L1DCache()
system.cpu.dcache = L1DCache(args)

# system crossbar
system.membus = SystemXBar()

# connect caches to the CPU ports
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

# connect caches to the crossbar
system.cpu.icache.connectBus(system.membus)
system.cpu.dcache.connectBus(system.membus)

# uncomment if you want to discard caches
#system.cpu.icache_port = system.membus.cpu_side_ports
#system.cpu.dcache_port = system.membus.cpu_side_ports

system.cpu.createInterruptController()

system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

system.system_port = system.membus.cpu_side_ports

# give the path to the executable
thispath = os.path.dirname(os.path.realpath(__file__))
binary = os.path.join(
    thispath,
    "../../../",
    "give/a/path/here"
    #example:"tests/test-progs/hello/bin/riscv/linux/simple_for",
)
system.workload = SEWorkload.init_compatible(binary)

process = Process()
process.cmd = [binary]
system.cpu.workload = process
system.cpu.createThreads()

root = Root(full_system=False, system=system)
m5.instantiate()

print(f"Beginning simulation!")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
