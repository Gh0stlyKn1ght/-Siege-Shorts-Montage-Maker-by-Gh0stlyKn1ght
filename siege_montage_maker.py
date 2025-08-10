#!/usr/bin/env python3
import argparse, re, subprocess, shutil

def run(cmd, **kw):
    return subprocess.run(cmd, check=True, text=True, capture_output=True, **kw)

def ffprobe_duration(path):
    out = run([
        "ffprobe","-v","error",
        "-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1", path
    ]).stdout.strip()
    return float(out)

def detect_silence(inp, noise_db, min_silence):
    p = subprocess.run([
        "ffmpeg","-hide_banner","-i", inp,
        "-af", f"silencedetect=noise={noise_db}dB:d={min_silence}",
        "-f","null","-"
    ], text=True, capture_output=True)
    stderr = p.stderr
    starts = [float(m.group(1)) for m in re.finditer(r"silence_start:\s*([0-9.]+)", stderr)]
    ends   = [float(m.group(1)) for m in re.finditer(r"silence_end:\s*([0-9.]+)", stderr)]
    return starts, ends

def build_keep_intervals(dur, starts, ends, pad, min_segment, merge_gap):
    events = sorted([(t,'s') for t in starts] + [(t,'e') for t in ends], key=lambda x:x[0])
    silence, open_s = [], None
    for t,typ in events:
        if typ=='s': open_s = t
        else:
            if open_s is None: silence.append((0.0, t))
            else: silence.append((open_s, t)); open_s = None
    if open_s is not None: silence.append((open_s, dur))

    keep, cur = [], 0.0
    for s,e in silence:
        if s > cur: keep.append((cur, s))
        cur = max(cur, e)
    if cur < dur: keep.append((cur, dur))

    keep = [(max(0, s - pad), min(dur, e + pad)) for s,e in keep]
    if not keep: return []
    merged = [keep[0]]
    for s,e in keep[1:]:
        ps,pe = merged[-1]
        if s - pe < merge_gap: merged[-1] = (ps, max(pe, e))
        else: merged.append((s,e))
    merged = [(s,e) for s,e in merged if (e - s) >= min_segment]
    return merged

def has_encoder(name: str) -> bool:
    exe = shutil.which("ffmpeg")
    if not exe: return False
    out = subprocess.run([exe, "-hide_banner", "-encoders"], text=True, capture_output=True).stdout
    return name in out

def build_select_filter(intervals):
    terms = [f"between(t\\,{s:.3f}\\,{e:.3f})" for (s,e) in intervals]
    return "1" if not terms else "+".join(terms)

def build_filter_complex(intervals, scale, shorts, fps, speed):
    select_expr = build_select_filter(intervals)
    chain = f"[0:v]select='{select_expr}',setpts=(N/FRAME_RATE/TB)/{speed}"
    if shorts:
        chain += ",scale=-2:1920,crop=1080:1920:(iw-1080)/2:0"
    elif scale:
        chain += f",scale={scale}"
    chain += f",fps={fps},format=yuv420p[vout]"
    return chain

def main():
    ap = argparse.ArgumentParser(description="Siege montage maker with music-start support")
    ap.add_argument("-i","--input", required=True)
    ap.add_argument("-o","--output", required=True)
    ap.add_argument("--music", default="PYTI - I Wanna Dance [NCS Release].mp3")
    ap.add_argument("--music-start", type=float, default=0.0, help="Start point in seconds for the music track")
    ap.add_argument("--noise", type=float, default=-38.0)
    ap.add_argument("--min-silence", type=float, default=0.35)
    ap.add_argument("--pad", type=float, default=0.18)
    ap.add_argument("--merge-gap", type=float, default=0.30)
    ap.add_argument("--min-segment", type=float, default=0.18)
    ap.add_argument("--speed", type=float, default=5.0)
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--scale", default="")
    ap.add_argument("--shorts", action="store_true")
    ap.add_argument("--nvenc", action="store_true")
    ap.add_argument("--h264", action="store_true")
    ap.add_argument("--hevc", action="store_true")
    ap.add_argument("--preset", default="p5")
    ap.add_argument("--cq", type=int, default=20)
    ap.add_argument("--crf", type=int, default=20)
    ap.add_argument("--bitrate", default="")
    ap.add_argument("--shortest", action="store_true")
    ap.add_argument("--yt", action="store_true")
    args = ap.parse_args()

    dur = ffprobe_duration(args.input)
    starts, ends = detect_silence(args.input, args.noise, args.min_silence)
    intervals = build_keep_intervals(dur, starts, ends, args.pad, args.min_segment, args.merge_gap)
    if not intervals:
        intervals = [(0.0, dur)]

    fcomplex = build_filter_complex(intervals, args.scale, args.shorts, args.fps, args.speed)

    vcodec = "libx264"
    if args.nvenc:
        if args.hevc and has_encoder("hevc_nvenc"):
            vcodec = "hevc_nvenc"
        elif has_encoder("h264_nvenc"):
            vcodec = "h264_nvenc"

    cmd = ["ffmpeg","-hide_banner","-y","-fflags","+genpts","-i", args.input]

    if args.music_start and args.music_start > 0:
        cmd += ["-ss", str(args.music_start)]
    cmd += ["-i", args.music]

    cmd += ["-filter_complex", fcomplex,"-map","[vout]","-map","1:a"]

    yt_flags = []
    if args.yt:
        yt_flags = [
            "-pix_fmt","yuv420p","-g", str(args.fps*2),
            "-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709"
        ]

    if vcodec.endswith("_nvenc"):
        cmd += ["-c:v", vcodec, "-preset", args.preset, "-cq", str(args.cq)]
        if args.bitrate:
            cmd += ["-rc","vbr_hq","-b:v", args.bitrate, "-maxrate", args.bitrate, "-bufsize", args.bitrate]
        cmd += yt_flags
    else:
        cmd += ["-c:v","libx264","-preset", args.preset, "-crf", str(args.crf)] + yt_flags

    cmd += ["-vsync","cfr","-r", str(args.fps), "-c:a","aac","-b:a","192k","-ar","48000"]
    if args.shortest:
        cmd += ["-shortest"]
    cmd += ["-movflags","+faststart", args.output]

    print("Running FFmpeg...")
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)
    print("Done ->", args.output)

if __name__ == "__main__":
    main()
