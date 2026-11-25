"""Settle state reader: f, unit P/Q/VIT, PTIE, load-bus VL, RES Q and VDF, trips; means over 26-28 s.
usage: python stage12/settle_read.py <psout> [<psout> ...]"""
import sys, numpy as np, mhi.psout
SB = {1: 15292.0, 2: 12838.0, 3: 6113.0, 4: 13548.0, 5: 200000.0}; UN={1:"32",2:"37",3:"30",4:"31",5:"FR"}
PSB = {1: 3315.0, 2: 223.6, 3: 217.1, 4: 3122.6, 5: 841.1, 6: 210.6, 7: 735.8, 8: 526.5, 9: 440.7, 10: 306.8,
       11: 1552.2, 12: 795.6, 13: 169.0, 14: 3247.4, 15: 765.7, 16: 452.4, 17: 4071.6, 18: 520.0}
for ps in sys.argv[1:]:
    r=mhi.psout.File(ps).run(0)
    def g(p):
        try:
            tr=r.call(p,sep="/"); return np.asarray(tr.domain.data,float),np.asarray(tr.data,float)
        except Exception: return None,None
    t,_=g("Root/Main/SyncUnit[1]/Wspd/0/1"); w=(t>=26)&(t<=28); A=lambda y: float(np.mean(y[w]))
    print("=====",ps, "tend %.2f"%t[-1])
    print("f  ", " ".join("%s %.4f"%(UN[i],A(g(f"Root/Main/SyncUnit[{i}]/Wspd/0/1")[1])/2/np.pi) for i in UN))
    print("P MW", " ".join("%s %.0f"%(UN[i],A(g(f"Root/Main/SyncUnit[{i}]/POUT/0/1")[1])*SB[i]) for i in UN))
    for q in ("QOUT","Q","QE"):
        y=g(f"Root/Main/SyncUnit[1]/{q}/0/1")[1]
        if y is not None:
            print("Q Mvar"," ".join("%s %.0f"%(UN[i],A(g(f"Root/Main/SyncUnit[{i}]/{q}/0/1")[1])*SB[i]) for i in UN)); break
    print("VIT", " ".join("%s %.3f"%(UN[i],A(g(f"Root/Main/SyncUnit[{i}]/VIT/0/1")[1])) for i in UN))
    print("PTIE %.0f"%(-A(g("Root/Main/PTIE/0/1")[1])))
    vl=[]
    for b in list(range(1,40))+["R29","R01"]:
        nm=f"VL{b}" if isinstance(b,int) else f"V{b}"
        y=g(f"Root/Main/{nm}/0/1")[1]
        if y is not None: vl.append("%s %.3f"%(nm,A(y)))
    print("VL", " ".join(vl))
    print("Q RES Mvar", " ".join("%d %.0f"%(k,A(g(f"Root/Main/RES_Plant[{k}]/IQ/0/1")[1]*g(f"Root/Main/RES_Plant[{k}]/VD/0/1")[1])*PSB[k]) for k in PSB))
    print("VDF", " ".join("%d %.3f"%(k,A(g(f"Root/Main/RES_Plant[{k}]/VDF/0/1")[1])) for k in PSB))
    tr=[k for k in PSB if g(f"Root/Main/RES_Plant[{k}]/TRIP/0/1")[1] is not None and g(f"Root/Main/RES_Plant[{k}]/TRIP/0/1")[1].max()>0.5]
    print("trips", tr)
