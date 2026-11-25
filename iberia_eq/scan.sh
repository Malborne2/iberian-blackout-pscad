#!/bin/zsh
# usage: SCAN_OUT=dir iberia_eq/scan.sh TAG "ENV=.. ENV=.." [TAG "ENV=.."] ...
# Cold pp_v2 fits in parallel, one per core (RUNLOG S28 sec 9). Common settings: FAST=1 OBJ=2 CORR=v2 CHG=phys SH_ARA_NW=0,
# --frsc 1500 --kres 0.2 --route 1.0 --flowcal --mincirc 2 --vkg 5. Per run: $SCAN_OUT/run_TAG.txt, state st_TAG.pkl, net net_TAG.p.
# PY selects the interpreter (default python3).
cd "$(dirname "$0")"; SP=${SCAN_OUT:-scan_out}; mkdir -p "$SP"; PY=${PY:-python3}
while [ $# -gt 1 ]; do
  tag=$1; envs=$2; shift 2
  env FAST=1 OBJ=2 CORR=v2 CHG=phys SH_ARA_NW=0 STATE=$SP/st_$tag.pkl DUMP_NET=$SP/net_$tag.p PYTHONWARNINGS=ignore ${=envs} \
    $PY -u pp_v2.py --frsc 1500 --kres 0.2 --route 1.0 --flowcal --mincirc 2 --vkg 5 > $SP/run_$tag.txt 2>&1 &
done
wait; echo all done
