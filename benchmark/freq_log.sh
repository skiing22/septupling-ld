#!/usr/bin/env bash
# freq_log.sh -- samples the current clock of one core every 0.2 s.
# Usage: ./freq_log.sh <core> <outfile>    (stop it with kill)
CORE="$1"; OUT="$2"
echo "unix_time,core_kHz" > "$OUT"
while true; do
  f=$(cat /sys/devices/system/cpu/cpu$CORE/cpufreq/scaling_cur_freq 2>/dev/null \
      || awk -v c="$CORE" '/^processor/{p=$3} /cpu MHz/ && p==c {printf "%d", $4*1000}' /proc/cpuinfo)
  echo "$(date +%s.%N),$f" >> "$OUT"; sleep 0.2
done
