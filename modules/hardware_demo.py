"""
RailCOA — Hardware Demonstration & Academic Knowledge Base
==========================================================
Course: Computer Organization and Architecture (UE25CS2302)
Faculty: Dr. Neelambike S | GM University | 40 Marks Evaluation

This module provides ready-to-run hardware code and documentation:
1. CPUlator Assembly Programs (ARMv7 & RISC-V 32)
2. CircuitVerse Digital Logic Circuit Specifications & Truth Tables
3. Tinkercad Hardware Interfacing Diagrams & Arduino C++ Code
4. Rapid-Fire Viva Voce Preparation Guide (10 Core Q&A)
5. Complete 12-Page Project Report Text & Contribution Matrix
"""

CPULATOR_ARM_CODE = """/*
 ============================================================================
  RailCOA — Indian Rail Ticketing Engine Assembly Demonstration (ARMv7)
  Target Simulator: CPUlator (ARMv7 DE1-SoC / Generic ARM)
  https://cpulator.01xz.net/?sys=arm
  
  Demonstrates:
  1. Base fare + Tatkal charge integer arithmetic
  2. Booking request loop counting & decrement
  3. Memory Load/Store instructions (LDR/STR) simulating seat map allocation
  4. Device polling / status branch (Programmed I/O vs Interrupt flag)
 ============================================================================
*/

.global _start
.text

_start:
    // Initialize pointers and values
    LDR   R0, =BOOKING_COUNT     // R0 = Pointer to number of bookings to process
    LDR   R1, [R0]               // R1 = Loop Counter (e.g. 5 tickets)
    
    LDR   R2, =BASE_FARE         // R2 = Pointer to Base Fare (e.g. 1245)
    LDR   R2, [R2]               // Load Base Fare into R2
    
    LDR   R3, =TATKAL_CHARGE     // R3 = Pointer to Tatkal Surcharge (373)
    LDR   R3, [R3]               // Load Tatkal Charge into R3
    
    LDR   R4, =TOTAL_REVENUE     // R4 = Pointer to Accumulated Revenue in RAM
    MOV   R5, #0                 // R5 = Running Total Revenue Accumulator
    
    LDR   R6, =SEAT_BITMAP       // R6 = Pointer to Seat Allocation Bitmap in RAM
    LDR   R7, [R6]               // R7 = Initial Seat Bitmap (e.g. 0x00000000)

BOOKING_LOOP:
    CMP   R1, #0                 // Check if bookings remain
    BEQ   FINISH_SIMULATION      // If counter == 0, branch to finish

    // --- 1. Arithmetic: Total Ticket Fare Calculation ---
    ADD   R8, R2, R3             // R8 = Base Fare (R2) + Tatkal Charge (R3)
    ADD   R5, R5, R8             // Accumulate to total revenue (R5)

    // --- 2. Memory Load/Store: Seat Map Allocation ---
    LSL   R9, R1, #1             // Generate simulated bit mask for seat
    ORR   R7, R7, R9             // Set allocated seat bit in bitmap
    STR   R7, [R6]               // STORE updated seat bitmap back to RAM!

    // --- 3. I/O Polling Branch: Simulate Storage Ticket Log Flush ---
    LDR   R10, =DEVICE_STATUS    // R10 = Pointer to Memory-Mapped I/O Status
POLL_DEVICE:
    LDR   R11, [R10]             // Read device status register
    CMP   R11, #1                // 1 = Device Ready, 0 = Device Busy
    BNE   POLL_DEVICE            // Busy-wait loop (Programmed I/O simulation!)

    // Decrement loop counter and repeat
    SUB   R1, R1, #1             // Decrement booking request counter
    B     BOOKING_LOOP

FINISH_SIMULATION:
    STR   R5, [R4]               // Store final accumulated revenue to RAM
    B     FINISH_SIMULATION      // Halt loop

// ============================================================================
// DATA SECTION (Memory Mapped Variables in RAM)
// ============================================================================
.data
.align 2
BOOKING_COUNT:   .word 5         // Process 5 passenger bookings
BASE_FARE:       .word 1245      // Base Fare in Rupees
TATKAL_CHARGE:   .word 373       // 30% Tatkal Premium Charge
TOTAL_REVENUE:   .word 0         // Stored final total
SEAT_BITMAP:     .word 0x00000000// 32-bit Coach Seat Allocation Mask
DEVICE_STATUS:   .word 1         // 1 = I/O Controller Ready (simulated)
.end
"""

CPULATOR_RISCV_CODE = """# ============================================================================
#  RailCOA — Indian Rail Ticketing Engine Assembly Demonstration (RISC-V RV32I)
#  Target Simulator: CPUlator (RISC-V RV32)
#  https://cpulator.01xz.net/?sys=riscv
# ============================================================================

.global _start
.text

_start:
    la   t0, BOOKING_COUNT       # Load address of counter
    lw   s0, 0(t0)               # s0 = Booking request count
    
    la   t1, BASE_FARE
    lw   s1, 0(t1)               # s1 = Base Fare (1245)
    
    la   t2, TATKAL_CHARGE
    lw   s2, 0(t2)               # s2 = Tatkal Surcharge (373)
    
    li   s3, 0                   # s3 = Accumulated Revenue = 0
    la   s4, SEAT_MAP            # s4 = Seat Map Array pointer

booking_loop:
    beqz s0, done                # If requests == 0, exit loop
    
    # 1. Arithmetic: Fare computation
    add  t3, s1, s2              # t3 = Base + Tatkal
    add  s3, s3, t3              # Revenue += Fare
    
    # 2. Memory Store: Update Seat Map
    sw   s0, 0(s4)               # Store booking ID into current seat slot
    addi s4, s4, 4               # Advance to next seat memory word
    
    # Decrement booking requests
    addi s0, s0, -1
    j    booking_loop

done:
    la   t4, TOTAL_REVENUE
    sw   s3, 0(t4)               # Store total revenue into RAM
halt:
    j    halt

.data
BOOKING_COUNT: .word 6
BASE_FARE:     .word 1245
TATKAL_CHARGE: .word 373
TOTAL_REVENUE: .word 0
SEAT_MAP:      .space 64
"""

CIRCUITVERSE_GUIDE = {
    "circuits": [
        {
            "name": "1. Set-Associative Cache Tag Comparator",
            "objective": "Verifies whether incoming memory address tag matches stored cache line tag and is valid.",
            "components": [
                "2x 8-bit Hex Input Pins (Incoming Tag vs Stored Cache Tag)",
                "1x 1-bit Input Pin (Cache Line Valid Bit)",
                "1x 8-bit Multi-bit Equality Comparator (or 8x XNOR gates + 8-input AND gate)",
                "1x 2-input AND gate (Combines Tag Match Output & Valid Bit)",
                "1x Green Output LED (CACHE HIT)",
                "1x Red Output LED (CACHE MISS via Inverter)"
            ],
            "truth_table": [
                {"Valid Bit": "0", "Tag A": "0x4A", "Tag B": "0x4A", "Comparator": "1", "Hit LED": "0 (OFF)", "Miss LED": "1 (ON)", "Condition": "Cold / Invalid Line"},
                {"Valid Bit": "1", "Tag A": "0x4A", "Tag B": "0x4A", "Comparator": "1", "Hit LED": "1 (ON)", "Miss LED": "0 (OFF)", "Condition": "Cache HIT"},
                {"Valid Bit": "1", "Tag A": "0x4A", "Tag B": "0x7F", "Comparator": "0", "Hit LED": "0 (OFF)", "Miss LED": "1 (ON)", "Condition": "Cache MISS (Tag Mismatch)"}
            ],
            "design_tip": "In CircuitVerse, group 8 XOR gates in parallel inverted by an 8-input AND gate to construct an instantaneous 8-bit equality comparator."
        },
        {
            "name": "2. IEEE 754 Floating-Point Exponent Comparator & Alignment Unit",
            "objective": "Compares exponents of two single-precision numbers ($E_1$ and $E_2$) to shift smaller mantissa for addition.",
            "components": [
                "2x 8-bit Input Pins (Exponent A and Exponent B)",
                "1x 8-bit Subtractor (Computes $\\Delta E = E_A - E_B$)",
                "1x Sign/Borrow Flag Detector",
                "1x Multiplexer (Routes larger exponent to output stage and magnitude to Barrel Shifter)"
            ],
            "truth_table": [
                {"$E_A$": "133 (2^6)", "$E_B$": "130 (2^3)", "$\\Delta E$": "3", "Shift Action": "Shift Mantissa B right by 3 bit positions", "Output Exp": "133"},
                {"$E_A$": "128 (2^1)", "$E_B$": "128 (2^1)", "$\\Delta E$": "0", "Shift Action": "No shift required", "Output Exp": "128"}
            ],
            "design_tip": "Use CircuitVerse ALU or 8-bit Subtractor element connected to a 2:1 MUX controlled by the Subtractor's Borrow Out pin."
        },
        {
            "name": "3. Direct Memory Access (DMA) Bus Controller",
            "objective": "Orchestrates Bus Request (BR) from I/O device, Bus Grant (BG) from CPU, and generates memory address burst.",
            "components": [
                "16-bit Binary Up-Counter (Memory Address Register)",
                "16-bit Down-Counter (Transfer Word Counter)",
                "Zero-Detect Comparator (Transfer Complete Flag)",
                "Bus Request / Bus Grant D-Flip-Flop handshake latch",
                "Interrupt Request (IRQ) Output Pin to CPU"
            ],
            "truth_table": [
                {"DMA State": "IDLE", "BR Input": "0", "BG Input": "0", "Counter": "Inactive", "IRQ Output": "0", "Status": "CPU controls system bus"},
                {"DMA State": "REQUEST", "BR Input": "1", "BG Input": "0", "Counter": "Hold", "IRQ Output": "0", "Status": "DMA waiting for CPU to release bus"},
                {"DMA State": "TRANSFER", "BR Input": "1", "BG Input": "1", "Counter": "Counting", "IRQ Output": "0", "Status": "DMA master of system bus (Burst)"},
                {"DMA State": "COMPLETE", "BR Input": "0", "BG Input": "1", "Counter": "Zero", "IRQ Output": "1", "Status": "Transfer done; Interrupt sent to CPU"}
            ],
            "design_tip": "Connect the Word Down-Counter's Zero output directly to the IRQ pin and to the reset pin of the Bus Request flip-flop."
        }
    ]
}

TINKERCAD_SPECS = {
    "title": "Tinkercad Hardware Interfacing: RailCOA Storage & Cache Status Display",
    "microcontroller": "Arduino Uno R3",
    "peripherals": [
        "16x2 I2C Liquid Crystal Display (LCD)",
        "1x Green LED (Cache Hit indicator connected to Digital Pin 8)",
        "1x Red LED (Cache Miss indicator connected to Digital Pin 9)",
        "1x Blue LED (DMA Bus Master active connected to Digital Pin 10)",
        "1x Pushbutton (Simulate Tatkal Request Trigger connected to Digital Pin 2 / INT0)"
    ],
    "arduino_code": """/*
  RailCOA — Arduino Hardware Indicator Simulator for Tinkercad
*/
#include <LiquidCrystal.h>

const int PIN_HIT = 8;
const int PIN_MISS = 9;
const int PIN_DMA = 10;
const int PIN_BUTTON = 2;

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

volatile int bookingCount = 0;
volatile bool newRequest = false;

void setup() {
  pinMode(PIN_HIT, OUTPUT);
  pinMode(PIN_MISS, OUTPUT);
  pinMode(PIN_DMA, OUTPUT);
  pinMode(PIN_BUTTON, INPUT_PULLUP);
  
  lcd.begin(16, 2);
  lcd.print("IRCTC COA Server");
  lcd.setCursor(0, 1);
  lcd.print("Status: READY");
  delay(1000);
}

void loop() {
  if (digitalRead(PIN_BUTTON) == LOW) {
    bookingCount++;
    // Simulate Cache Access
    if (bookingCount % 4 != 0) {
      digitalWrite(PIN_HIT, HIGH);
      digitalWrite(PIN_MISS, LOW);
      lcd.clear();
      lcd.print("Cache: HIT (L1)");
    } else {
      digitalWrite(PIN_HIT, LOW);
      digitalWrite(PIN_MISS, HIGH);
      lcd.clear();
      lcd.print("Cache: MISS -> RAM");
      
      // Trigger DMA Storage Dump
      digitalWrite(PIN_DMA, HIGH);
      delay(300);
      digitalWrite(PIN_DMA, LOW);
    }
    lcd.setCursor(0, 1);
    lcd.print("Booking #");
    lcd.print(bookingCount);
    delay(400);
    digitalWrite(PIN_HIT, LOW);
    digitalWrite(PIN_MISS, LOW);
  }
}
"""
}

VIVA_VOCE_PREP = [
    {
        "q": "1. What is the fundamental difference between Direct-Mapped and Set-Associative Cache?",
        "ans": "In a direct-mapped cache, each memory block maps to exactly one specific cache line (Index = Block Address % Sets, where Sets = Total Blocks). If multiple hot addresses share the same index, severe conflict misses occur (thrashing). In an N-way set-associative cache, each index points to a set containing N lines; the block can reside in any of the N lines, drastically reducing conflict misses at the expense of tag comparator hardware and multiplexer latency."
    },
    {
        "q": "2. How does Average Memory Access Time (AMAT) change when introducing an L2 cache?",
        "ans": "Without L2: AMAT = L1 Hit Time + (L1 Miss Rate * Main Memory Latency). With L2: AMAT = L1 Hit Time + L1 Miss Rate * [L2 Hit Time + (L2 Miss Rate * Main Memory Latency)]. Since L2 lookup is fast (~8 cycles vs ~80 cycles for DRAM), the effective penalty of an L1 miss drops substantially from 80 cycles down to ~15 cycles, keeping CPU stall cycles low."
    },
    {
        "q": "3. Why does Tatkal peak booking cause higher cache miss rates than normal hours?",
        "ans": "During Tatkal peak (10:00 AM), tens of thousands of concurrent requests target a very small working set of hot train seat maps (e.g. Vande Bharat/Rajdhani). Although temporal locality is high, the high volume of write locks and cache line invalidations cause set conflicts and false sharing in multi-core caches, requiring larger associativity (4-way or 8-way) to prevent thrashing."
    },
    {
        "q": "4. What is a Translation Lookaside Buffer (TLB) and how does it prevent the 2-memory-access penalty of paging?",
        "ans": "Standard paging requires two memory accesses for every data instruction: first to read the Page Table Entry (PTE) in RAM to translate Virtual Page Number (VPN) to Physical Frame Number (PFN), and second to access the actual data. The TLB is a high-speed on-chip associative cache storing recent VPN-to-PFN translations. On a TLB hit (1 cycle), the translation occurs in parallel without accessing RAM, achieving near 99% single-cycle translation."
    },
    {
        "q": "5. Why should financial ticketing servers avoid IEEE 754 floating-point arithmetic for fare calculations?",
        "ans": "IEEE 754 single-precision (32-bit) represents fractional numbers in base-2 powers ($2^{-1}, 2^{-2}, \\dots$). Common decimal fractions like 0.05 (5% GST) or 0.10 cannot be represented exactly in binary and become infinite recurring fractions ($0.000011001100\\dots_2$). Over thousands of seat bookings, accumulated rounding and cancellation errors create discrepancies between collected revenues and bank ledgers. Financial engines must use integer minor units (paise) or BCD / Decimal arithmetic."
    },
    {
        "q": "6. Compare Programmed I/O, Interrupt-Driven I/O, and Direct Memory Access (DMA).",
        "ans": "In Programmed I/O (PIO), the CPU executes a busy-wait polling loop checking device status registers for every single word, consuming 100% CPU cycles. In Interrupt-Driven I/O, the device interrupts the CPU when ready, freeing the CPU during wait times, but the CPU still executes an Interrupt Service Routine (ISR) for every block. In DMA, a dedicated hardware controller directly transfers large data blocks between memory and storage; the CPU is involved only for initial setup and a single completion interrupt, freeing 99%+ CPU cycles."
    },
    {
        "q": "7. What is the difference between DMA Burst Mode and Cycle-Stealing Mode?",
        "ans": "In Burst Mode, the DMA controller requests the bus and retains uninterrupted mastership until the entire data block is transferred; the CPU is halted from accessing memory during this burst. In Cycle-Stealing Mode, the DMA controller transfers one word at a time, stealing bus cycles only when the CPU is performing internal operations (non-memory cycles), allowing concurrent CPU instruction execution."
    },
    {
        "q": "8. What is Write-Through vs. Write-Back cache policy, and what is the role of the 'Dirty Bit'?",
        "ans": "In Write-Through, every write to cache is simultaneously written to main memory. It is simple and ensures memory consistency, but consumes high bus bandwidth. In Write-Back, writes are made only to the cache line; a 'Dirty Bit' flag is set to 1. The block is written back to main memory ONLY when it is evicted by a replacement policy, saving massive bus write traffic."
    },
    {
        "q": "9. Why does increasing CPU cores from 4 to 16 not yield a 4x throughput increase?",
        "ans": "According to Amdahl's Law and shared-memory bus contention, non-parallelizable serialization (mutex locks on train seat maps, PNR database commits) limits ideal scaling. Furthermore, multiple cores accessing shared L2/L3 cache and main memory experience bus arbitration stalls and cache coherence invalidations (e.g. MESI protocol broadcasts), creating diminishing returns at high core counts."
    },
    {
        "q": "10. In a 32-bit virtual address with 4 KB page size, how are the address bits divided?",
        "ans": "Page size = 4 KB = $4096 = 2^{12}$ bytes, so Page Offset requires 12 bits (bits 0 to 11). The remaining $32 - 12 = 20$ bits (bits 12 to 31) represent the Virtual Page Number (VPN). This supports $2^{20} = 1,048,576$ virtual pages per process."
    }
]

ACADEMIC_REPORT_DATA = {
    "title": "Simulation and Evaluation of Cache-Memory Hierarchy and Interfacing for Indian Rail Ticketing Servers",
    "course_code": "UE25CS2302",
    "course_name": "Computer Organization and Architecture",
    "faculty": "Dr. Neelambike S",
    "institution": "GM University, P.B. Road, Davanagere - 577 006, Karnataka, India",
    "team_members": [
        {"name": "Team Member 1", "role": "Lead Architect & Cache Hierarchy Specialist", "contribution": "Cache simulation models (Direct, Set-Assoc, Fully Assoc, LRU/FIFO, Write-Through/Back) & AMAT derivation", "percentage": "25%"},
        {"name": "Team Member 2", "role": "Virtual Memory & Memory Management Lead", "contribution": "Virtual memory paging engine, TLB implementation, Page Table, EMAT and page fault replacement", "percentage": "25%"},
        {"name": "Team Member 3", "role": "I/O, DMA & Arithmetic Simulation Specialist", "contribution": "Programmed I/O vs Interrupt vs DMA controller models, and IEEE 754 vs Decimal fee processing", "percentage": "25%"},
        {"name": "Team Member 4", "role": "Parallelism, UI/UX Dashboard & Hardware Demos", "contribution": "Multi-core contention models, CircuitVerse schematics, CPUlator assembly code, and Streamlit UX", "percentage": "25%"}
    ]
}

