"""
RailCOA — Simulation Engine
============================
Course: Computer Organization and Architecture (UE25CS2302)
Faculty: Dr. Neelambike S | GM University

This module implements the complete mathematical and architectural simulation models:
1. Synthetic Indian Rail Workload Generator (Tatkal Peak, Normal, Uniform)
2. Multi-Level Cache Hierarchy (L1 & L2, Associativity, Replacement, Write Policies)
3. Virtual Memory, Paging, Page Table & TLB
4. IEEE 754 Single-Precision Floating-Point vs. Arbitrary Decimal Fare Processing
5. Storage I/O Interfacing (Programmed I/O, Interrupt-Driven I/O, DMA Burst & Cycle-Stealing)
6. Multi-Core Parallel Processing & Memory Bus Contention Model
7. 32-bit Address Bitfield Decoder
8. Exception Handling & Configuration Verification
"""

import random
import struct
import math
from collections import OrderedDict
from decimal import Decimal, ROUND_HALF_UP


# =====================================================================
# 1. SYNTHETIC WORKLOAD GENERATOR (INDIAN RAILWAY TICKETING SERVER)
# =====================================================================

HOT_TRAINS = [
    {"number": "20607", "name": "Vande Bharat Express (MAS - MYS)", "base_fare": 1365.0, "quota": "Tatkal / Premium"},
    {"number": "12951", "name": "Mumbai Tejas Rajdhani Express", "base_fare": 2410.0, "quota": "General / Tatkal"},
    {"number": "12002", "name": "Bhopal Shatabdi Express", "base_fare": 1150.0, "quota": "Chair Car"},
    {"number": "12259", "name": "Sealdah - Bikaner Duronto", "base_fare": 1890.0, "quota": "Sleeper / 3AC"},
    {"number": "12626", "name": "Kerala Superfast Express", "base_fare": 745.0, "quota": "General / Sleeper"}
]

def generate_workload_trace(requests_count, workload_type, locality, seed=42):
    """
    Generates synthetic memory access traces simulating an IRCTC ticketing server.
    
    Workload Profiles:
    - Peak booking (Tatkal 10:00 AM window): Severe hotspotting on hot train seat maps
      and lock tables (80-95% accesses concentrated on ~5% memory space).
    - Normal booking: Moderate locality representing distributed regional bookings.
    - Uniform / Random: Stress load with zero temporal locality to test cache thrashing.
    
    Returns:
        list of dicts containing:
        - 'address': 32-bit integer address
        - 'op': 'READ' or 'WRITE'
        - 'train': Train metadata
        - 'region': Memory region (Seat Map, PNR Hash, Auth Cache, Payment Ledger)
    """
    rng = random.Random(seed)
    
    # Define working set sizes in terms of 32-bit memory word addresses
    if workload_type == "Peak booking":
        hot_pool_size = max(16, int(requests_count * 0.05))   # Top 5% addresses are hot
    elif workload_type == "Normal booking":
        hot_pool_size = max(32, int(requests_count * 0.20))   # 20% addresses are hot
    else: # Uniform/random
        hot_pool_size = requests_count * 4                     # Flat distribution
        
    trace = []
    base_memory_offset = 0x00400000  # Starting in 32-bit user process address space
    
    regions = [
        ("Seat Map Bitmap (Critical Mutex)", 0.45),
        ("PNR Status & Inquiry Cache", 0.30),
        ("User Authentication & Session Table", 0.15),
        ("Payment Gateway & Ledger Buffer", 0.10)
    ]
    
    for i in range(requests_count):
        # Determine temporal locality access
        if workload_type != "Uniform/random" and rng.random() < locality:
            # Hit the hot working set (high temporal/spatial locality)
            slot = rng.randrange(hot_pool_size)
            # Clustered memory address within 64-byte blocks
            address = base_memory_offset + (slot * 64) + (rng.randrange(4) * 4)
            train = HOT_TRAINS[slot % len(HOT_TRAINS)]
        else:
            # Scattered / cold access across broader memory space
            slot = rng.randrange(hot_pool_size, max(hot_pool_size * 4, requests_count * 8))
            address = base_memory_offset + (slot * 64)
            train = HOT_TRAINS[rng.randrange(len(HOT_TRAINS))]
            
        # Operation distribution: 75% reads (availability/PNR checks), 25% writes (seat locks)
        op = "WRITE" if rng.random() < 0.25 else "READ"
        
        # Select subsystem memory region based on probability distribution
        r_val = rng.random()
        cumulative = 0.0
        selected_region = regions[0][0]
        for region_name, prob in regions:
            cumulative += prob
            if r_val <= cumulative:
                selected_region = region_name
                break
                
        trace.append({
            "address": address,
            "op": op,
            "train": train,
            "region": selected_region
        })
        
    return trace


# =====================================================================
# 2. MULTI-LEVEL CACHE HIERARCHY SIMULATOR (L1 & L2 WITH WRITE POLICIES)
# =====================================================================

def simulate_cache_hierarchy(cfg, trace):
    """
    Models an L1 Data Cache + L2 Unified Cache hierarchy with:
    - Configurable cache size, block size, and associativity
    - Replacement policies: LRU (Least Recently Used), FIFO, Random
    - Write policies: Write-Through vs Write-Back (with Dirty Bit tracking)
    - Latency model: L1 = 1 cycle, L2 = 8 cycles, Main Memory = 80 cycles
    
    Mathematical AMAT Formulations:
    L1 AMAT = Hit_Time_L1 + (Miss_Rate_L1 * Penalty_L1)
    Hierarchy AMAT = Hit_Time_L1 + Miss_Rate_L1 * [ Hit_Time_L2 + Miss_Rate_L2 * Memory_Latency ]
    """
    n = len(trace)
    
    # --- L1 Cache Configuration ---
    l1_kb = cfg["cache_kb"]
    block_size = cfg["block_size"]
    total_l1_blocks = max(1, (l1_kb * 1024) // block_size)
    
    assoc_str = cfg["associativity"]
    if assoc_str == "Direct mapped":
        ways = 1
    elif assoc_str == "2-way":
        ways = 2
    elif assoc_str == "4-way":
        ways = 4
    elif assoc_str == "8-way":
        ways = 8
    else:  # Fully associative
        ways = total_l1_blocks
        
    ways = max(1, min(total_l1_blocks, ways))
    sets = max(1, total_l1_blocks // ways)
    
    # Calculate address bits for L1
    offset_bits = int(math.log2(block_size)) if block_size > 0 else 0
    index_bits = int(math.log2(sets)) if sets > 0 else 0
    tag_bits = 32 - (offset_bits + index_bits)
    
    # L1 storage representation:
    # Each set has an OrderedDict of tag -> {'dirty': bool}
    l1_cache = {i: OrderedDict() for i in range(sets)}
    
    # --- L2 Cache Configuration (Hierarchy) ---
    # L2 is typically 4x-8x larger than L1 with 8-way associativity
    l2_kb = max(l1_kb * 4, 64)
    l2_ways = 8
    total_l2_blocks = max(1, (l2_kb * 1024) // block_size)
    l2_sets = max(1, total_l2_blocks // l2_ways)
    l2_cache = {i: OrderedDict() for i in range(l2_sets)}
    
    replacement_policy = cfg["replacement"]
    write_policy = cfg["write_policy"]
    rng = random.Random(1337)
    
    # Metrics
    l1_hits = 0
    l1_misses = 0
    l1_reads = 0
    l1_writes = 0
    l1_dirty_evictions = 0
    
    l2_accesses = 0
    l2_hits = 0
    l2_misses = 0
    l2_dirty_evictions = 0
    
    main_memory_accesses = 0
    
    # Address trace processing
    for item in trace:
        addr = item["address"]
        is_write = (item["op"] == "WRITE")
        
        if is_write:
            l1_writes += 1
        else:
            l1_reads += 1
            
        # L1 Set and Tag calculation
        block_addr = addr >> offset_bits
        set_idx = block_addr % sets
        tag = block_addr >> index_bits
        
        target_set = l1_cache[set_idx]
        
        # Check L1 Hit / Miss
        if tag in target_set:
            l1_hits += 1
            if replacement_policy == "LRU":
                target_set.move_to_end(tag)
            if is_write:
                if write_policy == "Write-Back":
                    target_set[tag]["dirty"] = True
                else: # Write-Through
                    # Writes immediately propagate to L2 and memory
                    main_memory_accesses += 1
        else:
            # L1 Cache Miss
            l1_misses += 1
            
            # Handling set capacity and eviction
            if len(target_set) >= ways:
                if replacement_policy == "Random":
                    victim_tag = rng.choice(list(target_set.keys()))
                    victim_info = target_set.pop(victim_tag)
                else: # LRU or FIFO (both remove first element in OrderedDict when not moved)
                    victim_tag, victim_info = target_set.popitem(last=False)
                    
                if victim_info.get("dirty", False):
                    l1_dirty_evictions += 1
                    # Write-back evicted block to L2
                    l2_accesses += 1
                    
            # Insert new block into L1
            target_set[tag] = {"dirty": is_write if write_policy == "Write-Back" else False}
            
            # --- L1 Miss triggers L2 lookup ---
            l2_accesses += 1
            l2_block_addr = addr >> offset_bits
            l2_set_idx = l2_block_addr % l2_sets
            l2_tag = l2_block_addr // l2_sets
            target_l2_set = l2_cache[l2_set_idx]
            
            if l2_tag in target_l2_set:
                l2_hits += 1
                if replacement_policy == "LRU":
                    target_l2_set.move_to_end(l2_tag)
            else:
                l2_misses += 1
                main_memory_accesses += 1
                # L2 eviction if full
                if len(target_l2_set) >= l2_ways:
                    v_l2_tag, v_l2_info = target_l2_set.popitem(last=False)
                    if v_l2_info.get("dirty", False):
                        l2_dirty_evictions += 1
                        main_memory_accesses += 1
                target_l2_set[l2_tag] = {"dirty": False}
                
    # Calculate Ratios and Metrics
    l1_hit_ratio = (l1_hits / n) * 100.0 if n > 0 else 0.0
    l1_miss_ratio = (l1_misses / n) * 100.0 if n > 0 else 0.0
    
    l2_hit_ratio = (l2_hits / l2_accesses) * 100.0 if l2_accesses > 0 else 0.0
    l2_miss_ratio = (l2_misses / l2_accesses) * 100.0 if l2_accesses > 0 else 0.0
    
    # Standard Latencies (in CPU clock cycles):
    t_l1 = 1      # 1 cycle hit time
    t_l2 = 8      # 8 cycles L2 hit time
    t_ram = 80    # 80 cycles Main Memory penalty
    
    # L1 Single-Level AMAT
    l1_amat = t_l1 + (l1_miss_ratio / 100.0) * t_ram
    
    # Multi-Level Hierarchy AMAT
    # AMAT = L1_Hit_Time + Miss_Rate_L1 * (L2_Hit_Time + Miss_Rate_L2 * RAM_Latency)
    hierarchy_amat = t_l1 + (l1_miss_ratio / 100.0) * (t_l2 + (l2_miss_ratio / 100.0) * t_ram)
    
    # CPI Impact (assuming base CPI = 1.0 for compute instructions)
    base_cpi = 1.0
    memory_instruction_fraction = 0.35  # ~35% of ticketing instructions are load/store
    effective_cpi = base_cpi + (memory_instruction_fraction * (hierarchy_amat - 1.0))
    
    return {
        "l1_kb": l1_kb,
        "l2_kb": l2_kb,
        "block_size": block_size,
        "associativity": assoc_str,
        "ways": ways,
        "sets": sets,
        "tag_bits": tag_bits,
        "index_bits": index_bits,
        "offset_bits": offset_bits,
        "l1_hits": l1_hits,
        "l1_misses": l1_misses,
        "l1_hit_ratio": l1_hit_ratio,
        "l1_miss_ratio": l1_miss_ratio,
        "l1_dirty_evictions": l1_dirty_evictions,
        "l2_accesses": l2_accesses,
        "l2_hits": l2_hits,
        "l2_misses": l2_misses,
        "l2_hit_ratio": l2_hit_ratio,
        "l2_miss_ratio": l2_miss_ratio,
        "main_memory_accesses": main_memory_accesses,
        "l1_amat": l1_amat,
        "hierarchy_amat": hierarchy_amat,
        "effective_cpi": effective_cpi,
        "t_l1": t_l1,
        "t_l2": t_l2,
        "t_ram": t_ram
    }


# =====================================================================
# 3. VIRTUAL MEMORY, ADDRESS TRANSLATION & TLB SIMULATOR
# =====================================================================

def simulate_virtual_memory(cfg, trace):
    """
    Simulates Virtual Memory Paging with:
    - Translation Lookaside Buffer (TLB): 16-entry fully associative
    - Page Table: Tracking Virtual Page Number (VPN) -> Physical Page Number (PPN)
    - Page fault handling with disk fetch penalty (10,000 cycles)
    - Configurable page size (1KB to 16KB) and physical frames (4 to 128)
    - Replacement policies: LRU vs FIFO
    
    Formula for Effective Memory Access Time (EMAT):
    EMAT = TLB_Hit_Rate * (t_tlb + t_ram) + (1 - TLB_Hit_Rate) * [ (1 - p_fault) * (t_tlb + 2*t_ram) + p_fault * t_disk_fault ]
    """
    n = len(trace)
    page_size_kb = cfg.get("page_size_kb", 4)
    page_size_bytes = page_size_kb * 1024
    offset_bits = int(math.log2(page_size_bytes))
    vpn_bits = 32 - offset_bits
    
    frames = cfg.get("frames", 32)
    policy = cfg.get("page_policy", "LRU")
    
    tlb_capacity = 16
    tlb = OrderedDict()  # VPN -> PPN
    resident_frames = OrderedDict()  # VPN -> PPN
    
    tlb_hits = 0
    tlb_misses = 0
    page_faults = 0
    replacements = 0
    
    next_free_frame = 0
    page_table_log = []
    
    for item in trace:
        addr = item["address"]
        vpn = addr >> offset_bits
        offset = addr & ((1 << offset_bits) - 1)
        
        # 1. TLB Check
        if vpn in tlb:
            tlb_hits += 1
            ppn = tlb[vpn]
            if policy == "LRU":
                tlb.move_to_end(vpn)
                resident_frames.move_to_end(vpn)
        else:
            tlb_misses += 1
            
            # 2. Page Table / Resident Memory Check
            if vpn in resident_frames:
                # Page Hit in RAM, but was a TLB miss
                ppn = resident_frames[vpn]
                if policy == "LRU":
                    resident_frames.move_to_end(vpn)
            else:
                # 3. Page Fault (Not in RAM)
                page_faults += 1
                
                # Check if physical frame replacement is required
                if len(resident_frames) >= frames:
                    # Evict victim frame
                    victim_vpn, victim_ppn = resident_frames.popitem(last=False)
                    tlb.pop(victim_vpn, None)
                    ppn = victim_ppn
                    replacements += 1
                else:
                    ppn = next_free_frame
                    next_free_frame += 1
                    
                resident_frames[vpn] = ppn
                
            # 4. Update TLB with new translation
            if len(tlb) >= tlb_capacity:
                tlb.popitem(last=False)
            tlb[vpn] = ppn
            
    # Sample Page Table for Display (first 10 entries)
    sample_table = []
    for idx, (v_page, p_frame) in enumerate(resident_frames.items()):
        if idx >= 10:
            break
        v_addr_sample = (v_page << offset_bits)
        p_addr_sample = (p_frame << offset_bits)
        sample_table.append({
            "Virtual Page (VPN)": f"0x{v_page:05X}",
            "Physical Frame (PPN)": f"Frame #{p_frame:02d}",
            "Virtual Base Address": f"0x{v_addr_sample:08X}",
            "Physical Base Address": f"0x{p_addr_sample:08X}",
            "Valid Bit": "1 (Resident)",
            "Protection": "Read/Write"
        })
        
    tlb_hit_rate = (tlb_hits / n) * 100.0 if n > 0 else 0.0
    fault_rate = (page_faults / n) * 100.0 if n > 0 else 0.0
    
    # Paging Timing (cycles):
    t_tlb = 1             # 1 cycle TLB lookup
    t_ram = 80            # 80 cycles Main memory access
    t_disk_fault = 8000   # 8,000 cycles OS page fault handler + storage transfer
    
    # EMAT Calculation
    # TLB Hit: t_tlb + t_ram
    # TLB Miss + Page Table Hit: t_tlb + 2*t_ram (1 for Page Table + 1 for Data)
    # Page Fault: t_tlb + 2*t_ram + t_disk_fault
    p_hit = tlb_hit_rate / 100.0
    p_fault = fault_rate / 100.0
    
    emat = (p_hit * (t_tlb + t_ram)) + ((1.0 - p_hit) * ((1.0 - p_fault) * (t_tlb + 2 * t_ram) + p_fault * (t_tlb + 2 * t_ram + t_disk_fault)))
    
    return {
        "page_size_kb": page_size_kb,
        "offset_bits": offset_bits,
        "vpn_bits": vpn_bits,
        "physical_frames": frames,
        "tlb_hits": tlb_hits,
        "tlb_misses": tlb_misses,
        "tlb_hit_rate": tlb_hit_rate,
        "page_faults": page_faults,
        "replacements": replacements,
        "fault_rate": fault_rate,
        "emat": emat,
        "sample_table": sample_table
    }


# =====================================================================
# 4. IEEE 754 FLOATING-POINT VS. DECIMAL FARE PROCESSING
# =====================================================================

def float_to_ieee754_components(val):
    """
    Deconstructs a 32-bit float into IEEE 754 Standard components:
    - 1 Sign bit (0 for +, 1 for -)
    - 8 Biased Exponent bits (Bias = 127)
    - 23 Mantissa / Fraction bits
    """
    packed = struct.pack(">f", float(val))
    int_val = struct.unpack(">I", packed)[0]
    binary_str = format(int_val, "032b")
    
    sign_bit = binary_str[0]
    exponent_bits = binary_str[1:9]
    mantissa_bits = binary_str[9:]
    
    exp_int = int(exponent_bits, 2)
    unbiased_exp = exp_int - 127
    hex_str = f"0x{int_val:08X}"
    
    return {
        "full_binary": f"{sign_bit} {exponent_bits} {mantissa_bits[:7]} {mantissa_bits[7:15]} {mantissa_bits[15:]}",
        "raw_binary": binary_str,
        "sign_bit": sign_bit,
        "exponent_bits": exponent_bits,
        "unbiased_exp": unbiased_exp,
        "mantissa_bits": mantissa_bits,
        "hex": hex_str
    }

def simulate_fare_processing(base_fare=1245.50, tatkal_rate=0.30, gst_rate=0.05, passenger_count=1000):
    """
    Demonstrates Indian Railway fee calculation comparing:
    1. IEEE 754 Single-Precision 32-bit Floating Point (Hardware FPU)
    2. Arbitrary-Precision Decimal (Financial Standard: Decimal with ROUND_HALF_UP)
    
    Reveals precision loss, binary fractional rounding errors, and cancellation errors
    over batch passenger transactions.
    """
    # Exact Decimal Representation
    d_base = Decimal(str(base_fare))
    d_tatkal = (d_base * Decimal(str(tatkal_rate))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    d_subtotal = d_base + d_tatkal
    d_gst = (d_subtotal * Decimal(str(gst_rate))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    d_total = d_subtotal + d_gst
    d_cancellation_refund = (d_total * Decimal("0.50")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    # IEEE 754 32-Bit Float Representation (Hardware FPU emulation)
    f_base = struct.unpack("f", struct.pack("f", float(base_fare)))[0]
    f_tatkal = struct.unpack("f", struct.pack("f", f_base * tatkal_rate))[0]
    f_subtotal = struct.unpack("f", struct.pack("f", f_base + f_tatkal))[0]
    f_gst = struct.unpack("f", struct.pack("f", f_subtotal * gst_rate))[0]
    f_total = struct.unpack("f", struct.pack("f", f_subtotal + f_gst))[0]
    f_cancellation_refund = struct.unpack("f", struct.pack("f", f_total * 0.50))[0]
    
    # Cumulative discrepancy over batch bookings
    cumulative_decimal = d_total * passenger_count
    cumulative_float = f_total * passenger_count
    cumulative_drift = float(cumulative_decimal) - cumulative_float
    
    return {
        "base_fare": float(d_base),
        "tatkal_charge": float(d_tatkal),
        "gst_charge": float(d_gst),
        "decimal_total": float(d_total),
        "decimal_refund": float(d_cancellation_refund),
        "float_total": f_total,
        "float_refund": f_cancellation_refund,
        "single_ticket_error": f_total - float(d_total),
        "cumulative_drift": cumulative_drift,
        "passenger_count": passenger_count,
        "ieee754_total_components": float_to_ieee754_components(f_total),
        "ieee754_base_components": float_to_ieee754_components(f_base),
        "ieee754_gst_components": float_to_ieee754_components(f_gst)
    }


# =====================================================================
# 5. STORAGE I/O INTERFACING & DMA CONTROLLER MODEL
# =====================================================================

def simulate_io_and_dma(cfg):
    """
    Models storage transfer (e.g. Passenger Reservation Chart generation,
    Transaction logs, and audit dumps) under three I/O architectures:
    
    1. Programmed I/O (Polled I/O):
       - CPU checks device status register in a busy-wait polling loop.
       - Each 32-bit word requires CPU read, test bit, branch, and memory store.
       - CPU overhead = 100% of transfer duration.
       
    2. Interrupt-Driven I/O:
       - Device interrupts CPU when word/buffer ready.
       - CPU executes Interrupt Service Routine (ISR) with Context Switch overhead:
         (Save registers, load vector, transfer word, acknowledge, restore registers).
       - Context overhead = ~8-12 cycles per word + 500 cycle vector overhead.
       
    3. Direct Memory Access (DMA):
       - DMA Controller takes control of system bus (Bus Request / Bus Grant).
       - CPU overhead is strictly initialization (~1,500 cycles) + 1 completion interrupt (~400 cycles).
       - Mode A: Burst Mode (High throughput, CPU held off bus).
       - Mode B: Cycle Stealing (DMA steals idle bus cycles without stalling CPU).
    """
    io_mb = cfg.get("io_mb", 16)
    bytes_count = io_mb * 1024 * 1024
    words_count = bytes_count // 4  # 32-bit words
    
    # Hardware cycle models:
    bus_clock_mhz = 200  # 200 MHz Memory/Storage Bus
    cycles_per_word_bus = 2  # 2 bus cycles to transfer 32-bit word
    
    # 1. Programmed I/O (CPU does everything)
    # Loop: Read Status (1) -> Test Bit (1) -> Branch (1) -> Read Data (1) -> Store RAM (1) -> Inc/Dec Counter (1)
    cycles_per_word_pio = 6
    pio_cpu_cycles = words_count * cycles_per_word_pio
    
    # 2. Interrupt-Driven I/O
    # ISR per 64-byte block (16 words):
    # Context Save (10) + Transfer loop (16 * 2) + ACK (2) + Context Restore (10) = 54 cycles per block
    blocks_count = bytes_count // 64
    interrupt_cpu_cycles = (blocks_count * 54) + 600
    
    # 3. Direct Memory Access (DMA Controller)
    # CPU only configures: Source Address (1), Destination Address (1), Byte Count (1), Command Reg (1)
    # Total setup = ~1,500 cycles. Completion ISR = ~450 cycles.
    dma_setup_cycles = 1500
    dma_completion_cycles = 450
    dma_cpu_cycles = dma_setup_cycles + dma_completion_cycles
    
    # Bus transfer cycles (DMA Hardware Controller doing the transfer)
    dma_bus_transfer_cycles = words_count * cycles_per_word_bus
    
    # Cycles saved by DMA compared to PIO and Interrupts
    cycles_saved_vs_pio = max(0, pio_cpu_cycles - dma_cpu_cycles)
    cycles_saved_vs_interrupt = max(0, interrupt_cpu_cycles - dma_cpu_cycles)
    
    # CPU Busy Percentage during I/O operation
    total_duration = max(pio_cpu_cycles, dma_bus_transfer_cycles)
    pio_cpu_utilization = 100.0
    interrupt_cpu_utilization = min(100.0, (interrupt_cpu_cycles / total_duration) * 100.0)
    dma_cpu_utilization = (dma_cpu_cycles / total_duration) * 100.0
    
    return {
        "io_mb": io_mb,
        "bytes_count": bytes_count,
        "words_count": words_count,
        "pio_cpu_cycles": int(pio_cpu_cycles),
        "interrupt_cpu_cycles": int(interrupt_cpu_cycles),
        "dma_cpu_cycles": int(dma_cpu_cycles),
        "dma_bus_transfer_cycles": int(dma_bus_transfer_cycles),
        "cycles_saved_vs_pio": int(cycles_saved_vs_pio),
        "cycles_saved_vs_interrupt": int(cycles_saved_vs_interrupt),
        "pio_cpu_utilization": pio_cpu_utilization,
        "interrupt_cpu_utilization": interrupt_cpu_utilization,
        "dma_cpu_utilization": dma_cpu_utilization,
        "speedup_dma_vs_pio": pio_cpu_cycles / dma_cpu_cycles if dma_cpu_cycles > 0 else 1.0
    }


# =====================================================================
# 6. MULTI-CORE PARALLEL PROCESSING & CONTENTION MODEL
# =====================================================================

def simulate_parallel_workers(cfg, trace):
    """
    Models multi-core concurrent booking threads/workers (1 to 16 cores) on a shared memory bus.
    
    Amdahl's Law + Bus Contention Model:
    Ideal Speedup: S(N) = N
    Amdahl Speedup: S(N) = 1 / ((1 - P) + P / N) where P = 0.90 (90% parallelizable)
    Realistic Contention Speedup: Due to shared bus arbitration, cache invalidations
    (MESI snooping), and memory controller queuing delay:
    Contention Penalty factor = 1 + alpha * (N - 1)^1.35
    """
    cores = cfg.get("cores", 4)
    requests_count = len(trace)
    
    # Base sequential cycles (100 cycles per transaction in execution unit)
    base_sequential_cycles = requests_count * 120
    
    # Parallel fraction (ticket booking steps that can run independently)
    p_parallel = 0.92
    p_serial = 1.0 - p_parallel
    
    # Amdahl's Law theoretical speedup
    amdahl_speedup = 1.0 / (p_serial + (p_parallel / cores))
    
    # Bus and Cache Coherence Contention model
    # alpha represents memory traffic contention factor (higher under peak workloads)
    workload = cfg.get("workload", "Peak booking")
    alpha = 0.045 if workload == "Peak booking" else 0.025 if workload == "Normal booking" else 0.015
    contention_penalty = 1.0 + (alpha * ((cores - 1) ** 1.30))
    
    # Realistic execution cycles with contention
    parallel_cycles = max(1, int((base_sequential_cycles / amdahl_speedup) * contention_penalty))
    actual_speedup = base_sequential_cycles / parallel_cycles
    
    # Efficiency per core
    parallel_efficiency = (actual_speedup / cores) * 100.0
    
    # Throughput (Transactions per Million Cycles)
    throughput_per_mcycle = (requests_count / (parallel_cycles / 1_000_000))
    
    # Generate multi-core scaling curve for plotting (1 to 16 cores)
    scaling_curve = []
    for c in range(1, 17):
        c_amdahl = 1.0 / (p_serial + (p_parallel / c))
        c_contention = 1.0 + (alpha * ((c - 1) ** 1.30))
        c_actual = c_amdahl / c_contention
        scaling_curve.append({
            "cores": c,
            "ideal": float(c),
            "amdahl": c_amdahl,
            "actual": c_actual
        })
        
    return {
        "cores": cores,
        "sequential_cycles": base_sequential_cycles,
        "parallel_cycles": parallel_cycles,
        "actual_speedup": actual_speedup,
        "amdahl_speedup": amdahl_speedup,
        "parallel_efficiency": parallel_efficiency,
        "throughput_per_mcycle": throughput_per_mcycle,
        "scaling_curve": scaling_curve
    }


# =====================================================================
# 7. 32-BIT ADDRESS DECODER (INTERACTIVE HARDWARE TOOL)
# =====================================================================

def decode_address_hardware(hex_address_str, cache_cfg, vm_cfg):
    """
    Decodes any 32-bit memory address into:
    1. Cache Hierarchy fields: Tag, Set Index, Block Offset
    2. Virtual Memory fields: Virtual Page Number (VPN), Page Offset, Physical Page Number (PPN)
    """
    try:
        clean_str = hex_address_str.strip()
        if clean_str.startswith("0x") or clean_str.startswith("0X"):
            clean_str = clean_str[2:]
        addr_int = int(clean_str, 16) & 0xFFFFFFFF
    except Exception:
        addr_int = 0x004A2F8C  # Default sample address if invalid
        
    binary_32 = format(addr_int, "032b")
    
    # --- Cache breakdown ---
    block_size = cache_cfg.get("block_size", 64)
    l1_kb = cache_cfg.get("cache_kb", 8)
    assoc_str = cache_cfg.get("associativity", "4-way")
    
    total_blocks = max(1, (l1_kb * 1024) // block_size)
    ways_map = {"Direct mapped": 1, "2-way": 2, "4-way": 4, "8-way": 8, "Fully associative": total_blocks}
    ways = ways_map.get(assoc_str, 4)
    ways = max(1, min(total_blocks, ways))
    sets = max(1, total_blocks // ways)
    
    offset_bits_cache = int(math.log2(block_size))
    index_bits_cache = int(math.log2(sets))
    tag_bits_cache = 32 - (offset_bits_cache + index_bits_cache)
    
    tag_val = addr_int >> (offset_bits_cache + index_bits_cache)
    index_val = (addr_int >> offset_bits_cache) & ((1 << index_bits_cache) - 1) if index_bits_cache > 0 else 0
    offset_val = addr_int & ((1 << offset_bits_cache) - 1)
    
    # --- Virtual Memory breakdown ---
    page_size_kb = vm_cfg.get("page_size_kb", 4)
    page_size_bytes = page_size_kb * 1024
    offset_bits_vm = int(math.log2(page_size_bytes))
    vpn_bits_vm = 32 - offset_bits_vm
    
    vpn_val = addr_int >> offset_bits_vm
    page_offset_val = addr_int & ((1 << offset_bits_vm) - 1)
    
    # Simulated physical translation
    simulated_ppn = (vpn_val * 7 + 3) % vm_cfg.get("frames", 32)
    physical_addr = (simulated_ppn << offset_bits_vm) | page_offset_val
    
    return {
        "hex_input": f"0x{addr_int:08X}",
        "binary_32": binary_32,
        "cache": {
            "tag_bits": tag_bits_cache,
            "index_bits": index_bits_cache,
            "offset_bits": offset_bits_cache,
            "tag_val": f"0x{tag_val:X}",
            "index_val": index_val,
            "offset_val": f"0x{offset_val:X}",
            "tag_binary": binary_32[:tag_bits_cache],
            "index_binary": binary_32[tag_bits_cache:tag_bits_cache + index_bits_cache] if index_bits_cache > 0 else "",
            "offset_binary": binary_32[tag_bits_cache + index_bits_cache:]
        },
        "vm": {
            "vpn_bits": vpn_bits_vm,
            "offset_bits": offset_bits_vm,
            "vpn_val": f"0x{vpn_val:05X}",
            "page_offset_val": f"0x{page_offset_val:03X}",
            "simulated_ppn": f"Frame #{simulated_ppn:02d}",
            "physical_addr": f"0x{physical_addr:08X}",
            "vpn_binary": binary_32[:vpn_bits_vm],
            "offset_binary": binary_32[vpn_bits_vm:]
        }
    }


# =====================================================================
# 8. MASTER SIMULATION CONTROLLER & PIPELINE
# =====================================================================

def run_full_rail_simulation(cfg):
    """
    Executes the comprehensive Indian Rail Memory Hierarchy simulation pipeline.
    Combines workload generation, L1/L2 cache, Virtual Memory/TLB,
    IEEE 754 financial arithmetic, DMA/IO comparison, and multi-core parallelism.
    """
    # 1. Generate workload trace
    trace = generate_workload_trace(
        requests_count=cfg["requests"],
        workload_type=cfg["workload"],
        locality=cfg["locality"],
        seed=42
    )
    
    # 2. Run cache hierarchy simulation
    cache_results = simulate_cache_hierarchy(cfg, trace)
    
    # 3. Run virtual memory & paging simulation
    paging_results = simulate_virtual_memory(cfg, trace)
    
    # 4. Run IEEE 754 fare simulation
    fare_results = simulate_fare_processing(
        base_fare=1245.50,
        tatkal_rate=0.30,
        gst_rate=0.05,
        passenger_count=cfg["requests"]
    )
    
    # 5. Run I/O and DMA simulation
    io_results = simulate_io_and_dma(cfg)
    
    # 6. Run parallel multi-core simulation
    parallel_results = simulate_parallel_workers(cfg, trace)
    
    return {
        "cfg": cfg,
        "trace_sample": trace[:8],
        "cache": cache_results,
        "paging": paging_results,
        "fare": fare_results,
        "io": io_results,
        "parallel": parallel_results
    }
