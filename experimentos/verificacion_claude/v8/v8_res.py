"""Exploratorio: perdida a 1 mm (dato analitico, CAP base) con paso dz y filtro pasa-bajos en K (mismo esquema Strang)."""
import sys, numpy as np, scipy.fft as sf, json
import v8_bpm as B
dz = float(sys.argv[1]); Kc = float(sys.argv[2])
h = 0.2; W = 40.0; M = int(W/h); x = (np.arange(2*M+1)-M)*h
n2 = B.cell_n2(x, h); pa, na, u, w, V = B.lp01(x); G = B.cap(x, 28.0, 12.0, 0.5)
Vv = B.K0**2*(n2-B.NREF**2)-1j*G
k = 2*np.pi*np.fft.fftfreq(2*M+1, d=h); K2 = k[:, None]**2+k[None, :]**2
D = np.exp(1j*dz*K2/(2*B.K0*B.NREF)); D = D*(K2 <= Kc**2) if Kc > 0 else D
Pp = np.exp(-1j*dz*Vv/(4*B.K0*B.NREF)); A = pa.astype(complex); P0 = (abs(A)**2).sum()
for i in range(int(round(1000/dz))):
    A = Pp*A; A = sf.ifft2(D*sf.fft2(A, workers=1), workers=1); A = Pp*A
r = dict(dz=dz, Kc=Kc, K_res_m1=float(np.sqrt(2*np.pi*2*B.K0*B.NREF/dz)), loss=float(1-(abs(A)**2).sum()/P0))
print(r, flush=True); json.dump(r, open(f"v8_res_dz{dz:g}_Kc{Kc:g}.json", "w"))
