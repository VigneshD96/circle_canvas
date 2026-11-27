import numpy as np, wave
SR=44100; DUR=59.0; N=int(SR*DUR); rs=np.random.RandomState(7)
mix=np.zeros((N,2))
def put(sig,t,gain=1.0,pan=0.0):
    i=int(t*SR); s=sig[:max(0,N-i)]*gain
    l,r=np.cos((pan+1)*np.pi/4),np.sin((pan+1)*np.pi/4)
    mix[i:i+len(s),0]+=s*l*1.414; mix[i:i+len(s),1]+=s*r*1.414
def env(n,a=0.005,d=0.3,s=0.0,rel=None):
    t=np.arange(n)/SR; e=np.minimum(1,t/a)*np.exp(-t/d)*(1-s)+s
    if rel: e*=np.clip((n/SR-t)/rel,0,1)
    return e
def hz(m): return 440*2**((m-69)/12)
def tone(f,dur,kind='sine',vib=0,vr=5.5):
    n=int(dur*SR); t=np.arange(n)/SR; ph=2*np.pi*np.cumsum(f*(1+vib*np.sin(2*np.pi*vr*t)*np.minimum(1,t/0.25)))/SR
    if kind=='sine': return np.sin(ph)
    if kind=='flute': return np.sin(ph)+0.25*np.sin(2*ph)+0.08*np.sin(3*ph)+0.04*rs.randn(n)*np.minimum(1,t/0.05)
    if kind=='pluck': return sum(np.sin(k*ph)*np.exp(-t*(2+k*1.5))/k for k in range(1,7))
    if kind=='box': return (np.sin(ph)+0.4*np.sin(4.0*ph))*np.exp(-t*3)
def lp(x,a=0.15):
    y=np.zeros_like(x); acc=0
    for i in range(len(x)): acc+=a*(x[i]-acc); y[i]=acc
    return y
D=62  # D4
# ---------- act 1 bed (0-18.4): soft pad + music box, D major ----------
for t0,ch in zip(np.arange(0,18.4,4.6),[[50,57,62,66],[47,55,62,67],[43,55,59,62],[45,52,57,61]]):
    for m in ch:
        s=tone(hz(m),5.2,'sine',vib=0.003)*env(int(5.2*SR),a=1.2,d=99,rel=1.5)
        put(s,t0,0.035)
box=[74,78,81,78,76,74,73,74, 71,74,78,76,74,73,71,69, 74,78,81,83,81,78,76,74, 73,76,74,73,71,69,71,74]
for k,m in enumerate(box):
    t0=0.6+k*0.55
    if t0<18.2: put(tone(hz(m),1.2,'box'),t0,0.05,pan=0.3*np.sin(k))
# ---------- song (18.4-59): 80 BPM, D major, wavy flute lead, bass, synth tabla ----------
B=60/80; T0=18.4
prog=[50,47,43,45]*8   # D Bm G A (roots)
chords={50:[62,66,69],47:[62,66,71],43:[62,67,71],45:[61,64,69]}
bar=4*B
for k,r in enumerate(prog):
    t=T0+k*bar
    if t>=58.6: break
    full = t>=46.8
    for q in range(4):  # bass on beats 1 and 3, plus pickup
        if q in (0,2): put(tone(hz(r-12),B*1.6,'pluck')*env(int(B*1.6*SR),d=0.6),t+q*B,0.30)
    for q in range(8):  # strummed chord pluck on off-beats
        if q%2==1 or full:
            for j,m in enumerate(chords[r]): put(tone(hz(m),0.9,'pluck'),t+q*B/2+j*0.012,0.045 if not full else 0.06,pan=-0.4)
    pad=sum(tone(hz(m),bar+0.4,'sine',vib=0.004) for m in chords[r])*env(int((bar+0.4)*SR),a=0.4,d=99,rel=0.4)
    put(pad,t,0.03 if not full else 0.05,pan=0.2)
# synth tabla: dayan (pitched ring) + bayan (low bend)
def dayan(): n=int(0.35*SR); t=np.arange(n)/SR; return np.sin(2*np.pi*hz(74)*t+0.4*np.sin(2*np.pi*hz(86)*t))*np.exp(-t*14)+0.3*rs.randn(n)*np.exp(-t*90)
def bayan(): n=int(0.5*SR); t=np.arange(n)/SR; f=95+60*np.exp(-t*8); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*6)
pat=[('b',0),('d',0.5),('d',1.0),('b',1.5),('d',2.0),('b',2.5),('d',3.0),('d',3.5)]
t=T0
while t<58.6:
    full=t>=46.8
    for w,o in pat: put(bayan() if w=='b' else dayan(), t+o*B, (0.32 if w=='b' else 0.14)*(1.15 if full else 1), pan=0.15)
    if full:
        for o in np.arange(0,4,0.25): put(rs.randn(int(0.04*SR))*np.exp(-np.arange(int(0.04*SR))/SR*120),t+o*B,0.03,pan=0.5)
    t+=bar
# lead melody (wavy flute), (midi, beats); verse then a higher chorus at 46.8
verse=[(74,1),(76,0.5),(78,1.5),(76,1),(74,2),(71,1),(73,1),(74,2),(None,2),(78,1),(79,0.5),(81,1.5),(79,1),(78,1),(76,2),(74,1),(76,3),(None,2)]
chorus=[(81,1),(83,1),(81,1),(78,1),(79,1.5),(78,0.5),(76,2),(78,1),(81,1),(83,2),(86,1),(83,1),(81,4),(79,1),(78,1),(76,1),(74,1),(73,1),(74,3)]
def play(seq,t,gain):
    for m,b in seq:
        if m is not None:
            d=b*B; s=tone(hz(m),d+0.15,'flute',vib=0.012,vr=5.2)*env(int((d+0.15)*SR),a=0.04,d=99,rel=0.12)
            put(s,t,gain,pan=-0.1)
        t+=b*B
    return t
t=T0+bar
while t<46.0: t=play(verse,t,0.11)
t=46.8
while t<57.5: t=play(chorus,t,0.13)
# ---------- SFX synced to picture ----------
def static(d,g=1): n=int(d*SR); x=rs.randn(n); return lp(x,0.6)*(0.6+0.4*np.sin(np.arange(n)/SR*2*np.pi*7))*g
put(static(2.3)*env(int(2.3*SR),a=0.1,d=99,rel=0.3),0.0,0.05)
put(static(1.5)*env(int(1.5*SR),a=0.3,d=99,rel=0.2),6.29,0.08)
def slide(f0,f1,d):
    n=int(d*SR); t=np.arange(n)/SR; f=f0*(f1/f0)**(t/d); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.minimum(1,t/0.02)*np.clip((d-t)/0.1,0,1)
put(slide(1900,600,0.6),7.9,0.13); put(bayan(),8.45,0.35)         # sigh "aww" + thump
put(slide(500,1100,0.18),9.9,0.08)                                 # "?" boing
def click(): n=int(0.06*SR); t=np.arange(n)/SR; return (rs.randn(n)*np.exp(-t*300)+np.sin(2*np.pi*1800*t)*np.exp(-t*120))
for c in (13.5,13.92,15.0,15.42): put(click(),c,0.25)              # dial clicks
put(tone(hz(86),0.6,'box'),17.3,0.08)                              # idea sparkle
put(lp(rs.randn(int(0.5*SR)),0.3)*np.hanning(int(0.5*SR)),21.0,0.16,pan=0.6)  # whoosh: dashes off
put(static(0.4),25.88,0.07); put(tone(hz(88),0.9,'box'),26.25,0.12)           # picture snaps back: ding
for k,m in enumerate([86,90,93]): put(tone(hz(m),0.8,'box'),28.3+k*0.12,0.07) # triumph sparkle
for k,m in enumerate([93,90,95,98]): put(tone(hz(m),0.9,'box'),34.4+k*0.1,0.07,pan=0.3)  # kulfi lands
put(tone(hz(91),0.8,'box'),40.0,0.07)
put(tone(hz(93),1.2,'box'),52.6,0.08); put(rs.randn(int(0.12*SR))*np.exp(-np.arange(int(0.12*SR))/SR*40),54.1,0.08)  # bite crunch
# fade out at the end
mix[int(57.6*SR):]*=np.linspace(1,0,N-int(57.6*SR))[:,None]
# loudness: RMS to about -14.6 dBFS, limiter, soft clip
rms=np.sqrt(np.mean(mix**2)); mix*=10**(-14.6/20)/rms
g=np.ones(N); env_=0.0; rel=np.exp(-1/(0.08*SR)); peak=np.max(np.abs(mix),1); thr=0.85
for i in range(N):
    p=peak[i]; env_=p if p>env_ else env_*rel+p*(1-rel)
    g[i]=min(1,thr/env_) if env_>0 else 1
mix*=g[:,None]; mix=np.tanh(mix/0.7)*0.7
w=wave.open('score.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes()); w.close()
print('ok')
