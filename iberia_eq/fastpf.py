"""Fast Newton-Raphson load flow on pandapower's own admittance matrices, for the pp_v2 calibration loop (RUNLOG S28).

Why: in pp_v2 one pandapower load flow costs 5-15 ms on a 32-bus network, >90 % of it DataFrame <-> matrix glue, and the
exponential loads need an outer fixed-point loop (2-4 load flows per residual). Here:
  - Ybus / Yf / Yt are taken from pandapower once per network topology (rebuild() after any line / trafo change);
  - the calibration shunts (DSO) are added to the Ybus diagonal from their current q_mvar (no rebuild);
  - the exponential loads P0 V^alpha + j Q0 V^beta are part of the Newton mismatch (exact, no outer loop);
  - results the calibration reads (bus V, gen Q, ext-grid P/Q, line P/Q both ends) are written back to net.res_*.
The model is identical to pandapower's: check() compares against pp.runpp and must agree to < 1e-6 pu.
Limits: no Q limits, no taps changing during a solve, one gen per bus, one ext_grid.
"""
import numpy as np, pandapower as pp


class FastPF:
    def __init__(self, net, cal_shunts, exp_loads, alpha, beta):
        """cal_shunts: shunt indices that are knobs (Ybus diagonal, added per solve).
        exp_loads: load indices with exponential law; their P0, Q0 (at 1 pu, scale included) are passed to solve()."""
        self.net, self.cal, self.exp, self.a, self.b = net, np.asarray(cal_shunts), np.asarray(exp_loads), alpha, beta
        self.rebuild()

    def rebuild(self):
        """Take Ybus/Yf/Yt from pandapower with the calibration shunts at zero (call after a topology / parameter change)."""
        net = self.net
        q_keep = net.shunt.loc[self.cal, "q_mvar"].values.copy()
        net.shunt.loc[self.cal, "q_mvar"] = 0.0
        pp.runpp(net, init="results" if net.converged else "auto", max_iteration=50)
        net.shunt.loc[self.cal, "q_mvar"] = q_keep
        ppci = net._ppc["internal"]; lk = net._pd2ppc_lookups
        self.base = ppci["baseMVA"]
        self.Y0 = ppci["Ybus"].toarray(); self.Yf = ppci["Yf"].toarray(); self.Yt = ppci["Yt"].toarray()
        self.bl = np.asarray(lk["bus"])                              # pandapower bus index -> internal index
        nb = self.Y0.shape[0]; self.nb = nb
        br = ppci["branch"]; self.fbus = br[:, 0].real.astype(int); self.tbus = br[:, 1].real.astype(int)
        s, e = lk["branch"]["line"]; self.lrows = np.arange(s, e)  # line rows in branch order
        self.ref = self.bl[net.ext_grid.bus.values]
        self.genbus = self.bl[net.gen.bus.values]
        assert len(set(self.genbus)) == len(self.genbus), "one gen per bus"
        self.pv = np.array(sorted(set(self.genbus) - set(self.ref)))
        self.pq = np.array(sorted(set(range(nb)) - set(self.pv) - set(self.ref)))
        self.calbus = self.bl[net.shunt.bus.values[np.searchsorted(net.shunt.index.values, self.cal)]]
        self.expbus = self.bl[net.load.bus.loc[self.exp].values]
        oth = np.setdiff1d(net.load.index.values, self.exp)
        self.othbus = self.bl[net.load.bus.loc[oth].values]; self.oth = oth
        self.sgbus = self.bl[net.sgen.bus.values]
        self.V = ppci["V"].copy()

    def set_trafo_vk(self, idx, vk):
        """Change vk_percent of 1:1 trafos (no tap, no shift) in Y0 without a rebuild. With pandapower's T model and i0 > 0 this is
        exact to ~1e-8 pu (checked on the pump-station trafos, i0 0.5 %)."""
        net = self.net; s, e = self.net._pd2ppc_lookups["branch"]["trafo"]; rows = np.arange(s, e)
        pos = {t: k for k, t in enumerate(net.trafo.index.values)}
        for t in idx:
            sn, vkr, vk0 = net.trafo.at[t, "sn_mva"], net.trafo.at[t, "vkr_percent"], net.trafo.at[t, "vk_percent"]
            z = lambda v: (vkr + 1j * np.sqrt(v ** 2 - vkr ** 2)) / 100 * self.base / sn
            dy = 1 / z(vk) - 1 / z(vk0); r = rows[pos[t]]; f_, t_ = self.fbus[r], self.tbus[r]
            self.Y0[f_, f_] += dy; self.Y0[t_, t_] += dy; self.Y0[f_, t_] -= dy; self.Y0[t_, f_] -= dy

    def _const_S(self):
        """Constant injections (pu): gens P, sgens, constant loads."""
        net = self.net; S = np.zeros(self.nb, complex)
        ins = net.sgen.in_service.values
        np.add.at(S, self.sgbus[ins], (net.sgen.p_mw.values[ins] + 1j * net.sgen.q_mvar.values[ins]) / self.base)
        np.add.at(S, self.othbus, -(net.load.p_mw.loc[self.oth].values + 1j * net.load.q_mvar.loc[self.oth].values) / self.base)
        np.add.at(S, self.genbus, net.gen.p_mw.values / self.base)
        return S

    def solve(self, P0, Q0, tol=1e-9, maxit=30):
        """P0, Q0: arrays (MW, Mvar at 1 pu) for exp_loads in that order. Returns iterations; raises on divergence."""
        net = self.net; Y = self.Y0.copy()
        Y[self.calbus, self.calbus] += -1j * net.shunt.loc[self.cal, "q_mvar"].values / self.base
        Sc = self._const_S(); p0, q0 = np.asarray(P0) / self.base, np.asarray(Q0) / self.base
        V = self.V.copy(); Vm = np.abs(V); Va = np.angle(V)
        Vm[self.genbus] = net.gen.vm_pu.values; Vm[self.ref] = net.ext_grid.vm_pu.values
        Va[self.ref] = np.deg2rad(net.ext_grid.va_degree.values)
        V = Vm * np.exp(1j * Va)
        pvpq = np.r_[self.pv, self.pq]; npv, npq = len(self.pv), len(self.pq)
        a, b, eb = self.a, self.b, self.expbus
        for it in range(maxit):
            I = Y @ V; S = V * np.conj(I)
            Sl = np.zeros(self.nb, complex); vm = Vm[eb]
            np.add.at(Sl, eb, -(p0 * vm ** a + 1j * q0 * vm ** b))
            F = S - Sc - Sl
            f = np.r_[F[pvpq].real, F[self.pq].imag]
            if np.abs(f).max() < tol: break
            Vn = V / Vm
            dS_dVm = V[:, None] * np.conj(Y * Vn[None, :]) + np.diag(np.conj(I) * Vn)
            dS_dVa = 1j * V[:, None] * np.conj(np.diag(I) - Y * V[None, :])
            dSl = np.zeros(self.nb, complex)
            np.add.at(dSl, eb, -(a * p0 * vm ** (a - 1) + 1j * b * q0 * vm ** (b - 1)))
            dS_dVm = dS_dVm - np.diag(dSl)
            J = np.block([[dS_dVa[np.ix_(pvpq, pvpq)].real, dS_dVm[np.ix_(pvpq, self.pq)].real],
                          [dS_dVa[np.ix_(self.pq, pvpq)].imag, dS_dVm[np.ix_(self.pq, self.pq)].imag]])
            dx = np.linalg.solve(J, -f)
            k = min(1.0, 0.3 / max(np.abs(dx[:npv + npq]).max(), 1e-12), 0.1 / max(np.abs(dx[npv + npq:]).max(initial=0), 1e-12))
            dx *= k                                                 # damped step far from the solution (0.3 rad, 0.1 pu)
            Va[pvpq] += dx[:npv + npq]; Vm[self.pq] += dx[npv + npq:]
            V = Vm * np.exp(1j * Va)
        else:
            raise RuntimeError("fastpf: no convergence")
        if not np.isfinite(V).all() or Vm.min() < 0.5: raise RuntimeError("fastpf: diverged")
        self.V = V; self._write(Y, V, Sc, p0, q0)
        return it

    def _write(self, Y, V, Sc, p0, q0):
        net = self.net; base = self.base; bl = self.bl
        net.res_bus["vm_pu"] = np.abs(V)[bl[net.bus.index.values]]
        net.res_bus["va_degree"] = np.rad2deg(np.angle(V))[bl[net.bus.index.values]]
        S = V * np.conj(Y @ V); vm = np.abs(V)[self.expbus]
        Sl = np.zeros(self.nb, complex); np.add.at(Sl, self.expbus, -(p0 * vm ** self.a + 1j * q0 * vm ** self.b))
        Sg = (S - Sc - Sl) * base                                    # what the gen / slack must inject on top of the rest
        net.res_gen["q_mvar"] = Sg[self.genbus].imag; net.res_gen["p_mw"] = net.gen.p_mw.values
        net.res_gen["vm_pu"] = np.abs(V)[self.genbus]
        net.res_ext_grid["p_mw"] = Sg[self.ref].real; net.res_ext_grid["q_mvar"] = Sg[self.ref].imag
        net.load.loc[self.exp, "p_mw"] = p0 * vm ** self.a * base; net.load.loc[self.exp, "q_mvar"] = q0 * vm ** self.b * base
        r = self.lrows; Sf = V[self.fbus[r]] * np.conj(self.Yf[r] @ V) * base; St = V[self.tbus[r]] * np.conj(self.Yt[r] @ V) * base
        net.res_line["p_from_mw"] = Sf.real; net.res_line["q_from_mvar"] = Sf.imag
        net.res_line["p_to_mw"] = St.real; net.res_line["q_to_mvar"] = St.imag
        net.converged = True

    def check(self, P0, Q0):
        """Solve here, then with pandapower on the same loads; return max |dV| (pu) and max |d gen Q| (Mvar)."""
        self.solve(P0, Q0)
        v1 = self.net.res_bus.vm_pu.values.copy(); q1 = self.net.res_gen.q_mvar.values.copy(); pl1 = self.net.res_line.p_from_mw.values.copy()
        pp.runpp(self.net, init="results")
        return (np.abs(v1 - self.net.res_bus.vm_pu.values).max(), np.abs(q1 - self.net.res_gen.q_mvar.values).max(),
                np.abs(pl1 - self.net.res_line.p_from_mw.values).max())
