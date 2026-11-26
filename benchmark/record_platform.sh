#!/usr/bin/env bash
# record_platform.sh -- writes everything a reviewer may ask about the machine.
# Usage: ./record_platform.sh > platform.txt
CORE="${CORE:-2}"
sec(){ printf '\n===== %s =====\n' "$1"; }
sec "Date (UTC)";            date -u
sec "Hostname";              hostname
sec "Kernel";                uname -a
sec "OS";                    cat /etc/os-release 2>/dev/null
sec "Virtualisation";        (systemd-detect-virt 2>/dev/null || echo "systemd-detect-virt not available"); grep -m1 -o hypervisor /proc/cpuinfo || echo "no hypervisor flag in /proc/cpuinfo"
sec "CPU (lscpu)";           lscpu
sec "CPU model";             grep -m1 "model name" /proc/cpuinfo
sec "pclmulqdq / avx2";      for f in pclmulqdq avx2 constant_tsc nonstop_tsc; do grep -qw "$f" /proc/cpuinfo && echo "$f: yes" || echo "$f: no"; done
sec "Pinned core";           echo "benchmark pinned to logical CPU $CORE"; lscpu -e 2>/dev/null | awk -v c="$CORE" 'NR==1 || $1==c'
sec "Core type of pinned CPU (hybrid Intel: P-core vs E-core)"
  cat /sys/devices/system/cpu/cpu$CORE/topology/core_cpus_list 2>/dev/null
  cat /sys/devices/cpu_core/cpus 2>/dev/null | sed 's/^/P-cores (cpu_core): /'
  cat /sys/devices/cpu_atom/cpus 2>/dev/null | sed 's/^/E-cores (cpu_atom): /'
sec "Frequency settings"
  echo "governor (cpu$CORE): $(cat /sys/devices/system/cpu/cpu$CORE/cpufreq/scaling_governor 2>/dev/null || echo n/a)"
  echo "driver:              $(cat /sys/devices/system/cpu/cpu$CORE/cpufreq/scaling_driver 2>/dev/null || echo n/a)"
  echo "min/max kHz:         $(cat /sys/devices/system/cpu/cpu$CORE/cpufreq/scaling_min_freq 2>/dev/null) / $(cat /sys/devices/system/cpu/cpu$CORE/cpufreq/scaling_max_freq 2>/dev/null)"
  echo "intel_pstate no_turbo: $(cat /sys/devices/system/cpu/intel_pstate/no_turbo 2>/dev/null || echo n/a)  (1 = turbo off)"
  echo "cpufreq boost:       $(cat /sys/devices/system/cpu/cpufreq/boost 2>/dev/null || echo n/a)"
  echo "SMT active:          $(cat /sys/devices/system/cpu/smt/active 2>/dev/null || echo n/a)"
sec "Memory";                free -h
sec "Load average";          cat /proc/loadavg
sec "Compiler";              g++ --version | head -1
sec "Libraries"
  (dpkg -l 2>/dev/null | grep -E "libntl|libgf2x|libgmp" ) || true
  if [ -n "$CONDA_PREFIX" ]; then (conda list 2>/dev/null | grep -E "^(ntl|gf2x|gmp) ") || true; fi
sec "Motherboard / BIOS (needs sudo; skipped if not allowed)"
  sudo -n dmidecode -s system-product-name 2>/dev/null; sudo -n dmidecode -s bios-version 2>/dev/null || echo "not available without sudo"
