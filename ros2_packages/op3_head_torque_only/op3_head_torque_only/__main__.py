"""Aktifkan torque ID 19/20 hanya jika posisi dan target sama dan stabil."""
from __future__ import annotations
import json,time
from datetime import datetime,timezone
from pathlib import Path
from dynamixel_sdk import COMM_SUCCESS
from op3_servo_torque_control.cli import ServoBus

HEAD=(19,20)

def inspect_pair(bus):
    return {str(s):bus.inspect(s) for s in HEAD}

def check(pair, baseline=None):
    for sid in HEAD:
        s=pair[str(sid)]
        if s['model']!=1020 or s['operating_mode']!=3 or s['hardware_error']!=0:
            raise RuntimeError(f'ID {sid}: model/mode/error tidak aman')
        if s['goal_position'] != s['present_position']:
            raise RuntimeError(f'ID {sid}: goal dan posisi berbeda; torque tidak dilanjutkan')
        if baseline is not None and s['present_position'] != baseline[str(sid)]['present_position']:
            raise RuntimeError(f'ID {sid}: posisi berubah; operasi dihentikan')

def enable(bus, report):
    if bus.read(200,24)!=1: raise RuntimeError('Daya bus mati')
    for sid in range(1,19):
        if bus.read(sid,64)!=1: raise RuntimeError(f'ID badan {sid} belum torque-on')
    first=inspect_pair(bus);check(first)
    report['first']=first
    time.sleep(.25)
    stable=inspect_pair(bus);check(stable,first)
    report['stable_before']=stable
    if any(stable[str(s)]['torque_enabled'] not in (0,1) for s in HEAD):
        raise RuntimeError('Nilai torque tidak valid')
    for sid in HEAD:
        current=inspect_pair(bus);check(current,stable)
        if current[str(sid)]['torque_enabled']==0:
            result,error=bus.packet.write1ByteTxRx(bus.port,sid,64,1)
            if result!=COMM_SUCCESS or error:
                raise RuntimeError(f'ID {sid}: torque-on gagal: {bus.packet.getTxRxResult(result)} / {bus.packet.getRxPacketError(error)}')
            report['written_ids'].append(sid)
        after=inspect_pair(bus);check(after,stable)
        if after[str(sid)]['torque_enabled']!=1: raise RuntimeError(f'ID {sid}: torque tidak terverifikasi')
        report['samples'].append(after)
    for _ in range(5):
        time.sleep(.1); sample=inspect_pair(bus);check(sample,stable)
        if any(sample[str(s)]['torque_enabled']!=1 for s in HEAD): raise RuntimeError('Torque kepala berubah')
        report['samples'].append(sample)
    return report

def main():
    report={'started_utc':datetime.now(timezone.utc).isoformat(),'status':'starting','operation':'head_torque_only','written_ids':[],'goal_position_writes':0,'samples':[]}
    directory=Path('runs/op3_head_torque_only');directory.mkdir(parents=True,exist_ok=True)
    path=directory/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json')
    try:
        with ServoBus() as bus: enable(bus,report)
        report['status']='completed'
    except Exception as e:
        report['status']='failed';report['error']=str(e)
    report['finished_utc']=datetime.now(timezone.utc).isoformat()
    with path.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps(report,indent=2));print('report='+str(path))
    return 0 if report['status']=='completed' else 1

if __name__=='__main__':raise SystemExit(main())
