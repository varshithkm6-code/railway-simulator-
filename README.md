# 🚆 RailCOA — Indian Rail Ticketing Server Simulator
### COA Problem-Based Learning (PBL) | Course Code: UE25CS2302
**Institution:** GM University, Davanagere | Department of Computer Science & Engineering / FET  
**Faculty Member:** Dr. Neelambike S  
**Total Evaluation Marks:** 40 Marks  
**Project Title:** *Simulation and Evaluation of Cache-Memory Hierarchy and Interfacing for Indian Rail Ticketing Servers*

---

## 🌟 Executive Overview
**RailCOA** is an educational, interactive architectural testbed designed to model and evaluate the complete memory and I/O subsystem of high-concurrency Indian Railway (IRCTC) reservation engines. 

During the critical **10:00 AM Tatkal booking window**, sudden bursts of passenger requests create acute latency bottlenecks, cache thrashing, and memory bus contention across train seat maps, PNR hash tables, and payment ledgers. This simulator quantitatively models these phenomena across all syllabus units (Units 4–6: Memory Hierarchy, Storage, Arithmetic, and Parallelism).

---

## 🖥️ Modern UI/UX Dashboard Features
The web application is built in pure, self-contained Python with Streamlit and styled using modern dark-mode glassmorphic aesthetics:

1. **📊 Executive Overview & Architecture:**
   - 8 Real-time Stat Cards (L1/L2 Hit Ratios, AMAT, TLB Hit Rate, Page Faults, DMA Saved Cycles, Multi-Core Speedup, Effective CPI, IEEE 754 Drift).
   - Interactive Memory Subsystem Pipeline Flowchart.
   - Real-time IRCTC Access Trace inspector with actual train names (Vande Bharat, Mumbai Rajdhani, Bhopal Shatabdi).

2. **🧠 Multi-Level Cache Hierarchy (L1 & L2):**
   - Configurable Cache Size (1 KB – 64 KB), Block Size (16 B – 128 B), and Associativity (Direct-Mapped, 2-Way, 4-Way, 8-Way, Fully Associative).
   - Replacement Policies: **LRU** (Least Recently Used), **FIFO**, and **Random**.
   - Write Policies: **Write-Back** (with Dirty Bit tracking and eviction writebacks) vs **Write-Through**.
   - Step-by-step mathematical **AMAT** (Average Memory Access Time) LaTeX derivation.

3. **🗂️ Virtual Memory, Page Table & TLB:**
   - 32-bit Virtual Address Translation model (VPN + Page Offset $\rightarrow$ PPN).
   - 16-entry high-speed Translation Lookaside Buffer (TLB).
   - Inverted Page Table inspector and Page Fault handling (8,000-cycle disk transfer penalty).
   - Step-by-step **EMAT** (Effective Memory Access Time) formulation.

4. **💰 IEEE 754 Floating-Point Fee Engine:**
   - Interactive 32-bit Single-Precision bitfield inspector (1 Sign bit, 8 Biased Exponent bits, 23 Mantissa bits).
   - Real Indian Railway fare calculation: Base Fare + 30% Tatkal Surcharge + 5% GST + 50% Cancellation Refund.
   - Hardware Float32 vs Arbitrary-Precision Financial Decimal comparison highlighting cumulative ledger drift.

5. **💾 Storage I/O Interfacing & DMA Controller:**
   - Quantitative evaluation of **Programmed I/O (PIO)**, **Interrupt-Driven I/O**, and **Direct Memory Access (DMA)**.
   - Models **Burst Mode** vs **Cycle-Stealing Mode**.
   - CPU cycles saved and CPU busy-time utilization percentages.

6. **⚡ Multi-Core Parallel Workers & Bus Contention:**
   - Scalable 1 to 16 concurrent booking cores.
   - Amdahl’s Law theoretical speedup ($P = 92\%$) vs realistic memory bus and MESI cache coherence contention penalty.
   - System throughput in Transactions per Million Cycles.

7. **🔍 Interactive 32-Bit Address Decoder:**
   - Enter any hexadecimal memory address (e.g. `0x004A2F8C`).
   - Instant visual slicing into Cache Tag, Index, Offset bits AND Virtual Memory VPN and Offset bits!

8. **🔌 Hardware & Assembly Demonstrations:**
   - Ready-to-run **CPUlator** assembly programs (ARMv7 & RISC-V RV32I) for ticket counting loops, memory load/stores, and device status polling.
   - **CircuitVerse** digital logic specifications and truth tables for:
     1. Set-Associative Cache Tag Comparator
     2. IEEE 754 Exponent Comparator & Alignment Unit
     3. DMA Bus Controller & Handshake Logic
   - **Tinkercad** Arduino C++ status display wiring code.

9. **🎓 Academic Documentation & Viva Voce Exam Prep:**
   - Complete 12-page project report structure meeting GM University guidelines.
   - Individual contribution declaration table for 4 team members (25% each).
   - Top 10 rapid-fire Viva Voce questions with detailed model answers.

---

## 🚀 How to Run the Application

The application is written strictly in Python without any external Node/React dependencies.

### Step 1: Open PowerShell in Project Directory
```powershell
cd C:\Users\kpmun\Downloads\COA_Rail_Ticketing_Simulator\COA_Rail_Ticketing_Simulator
```

### Step 2: Launch Streamlit
```powershell
python -m streamlit run app.py
```

### Step 3: Access in Your Browser
Open: [http://localhost:8501](http://localhost:8501)

---

## 🎯 Demonstration Order for Viva / Presentation (100% Score Strategy)

1. **Overview Tab:** Select the preset *"⚡ 10:00 AM Tatkal Rush"* in the sidebar. Show how temporal locality jumps to 90% and explain the IRCTC booking trace.
2. **Cache Tab:** Compare *"Direct mapped"* vs *"4-way"* set-associative cache. Point out how 4-way associativity drops miss ratio and lowers AMAT.
3. **Virtual Memory Tab:** Explain the 16-entry TLB hit rate and how page faults trigger disk fetches. Show the EMAT formula.
4. **IEEE 754 Tab:** Show the single-precision binary breakdown (Sign, Exponent, Mantissa) and explain why the accumulated rounding error requires banks/railways to use decimal or integer minor units (paise).
5. **I/O & DMA Tab:** Point out the millions of CPU cycles saved by DMA over Programmed I/O during passenger chart logging.
6. **Parallelism Tab:** Increase worker cores from 4 to 16 and explain why speedup flattens due to shared bus contention (Amdahl's Law).
7. **Hardware Tab:** Copy the ARM assembly code and show it running live inside [CPUlator](https://cpulator.01xz.net/?sys=arm).
