#!/usr/bin/env python3
"""A fake `sd-cli` for the tests (D36): takes the real argv, writes a valid PNG to ``-o`` and prints log lines in the
format of the real one (``piloto/r0/portal/logs/og-s3.log``). Stdlib only; never needs a GPU or a model.

Behaviour, from environment variables:

- ``FAKE_SD_ARGV``: path of a JSON file that gets ``{"argv", "ld_library_path"}``.
- ``FAKE_SD_SLEEP``: seconds to take between the loading and the sampling lines (default 0).
- ``FAKE_SD_PID``: path where its own pid is written.
- ``FAKE_SD_CHILD_PID``: path where the pid of a child ``sleep 60`` (in the same group) is written.
- ``FAKE_SD_FAIL``: print that text and exit with code 3 (no image).
- ``FAKE_SD_NO_IMAGE``: exit 0 without writing the image.
- ``FAKE_SD_NO_TIMES``: leave the timing lines out of the log.
- ``FAKE_SD_GATE_AFTER``: with ``FAKE_SD_GATE`` (a path), print that many step bars, then wait until the file exists (up
  to 30 s) before printing the rest: a test decides when the run goes on, with no timing. Bars end like the real ones
  (``\\r  |==| 3/6 -  1.20s/it - ETA 00:03\\x1b[K``) and, after "sampling completed", a VAE tile bar of 36 follows.
- ``FAKE_SD_REPORT_ZERO``: print the driver's "reported free 0.00 MB" line before the sleep."""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gimg.engine import png_bytes  # noqa: E402


def say(text):
    sys.stdout.write(text + "\n")
    sys.stdout.flush()


def main(argv):
    env = os.environ.get
    if env("FAKE_SD_ARGV"):
        with open(env("FAKE_SD_ARGV"), "w", encoding="utf-8") as fh:
            json.dump({"argv": sys.argv, "ld_library_path": env("LD_LIBRARY_PATH")}, fh)
    if env("FAKE_SD_PID"):
        with open(env("FAKE_SD_PID"), "w", encoding="utf-8") as fh:
            fh.write(str(os.getpid()))
    if env("FAKE_SD_CHILD_PID"):
        child = subprocess.Popen(["sleep", "60"])
        with open(env("FAKE_SD_CHILD_PID"), "w", encoding="utf-8") as fh:
            fh.write(str(child.pid))
    flags = dict(zip(argv, argv[1:]))
    steps = int(flags.get("--steps", "4"))
    times = not env("FAKE_SD_NO_TIMES")
    say("[I] sd.cpp stable-diffusion.cpp fake --- main.cpp:1")
    if times:
        say("[I] loading tensors completed, taking 1.50s (read: 1.00s, memcpy: 0.00s) --- model_loader.cpp:1400")
        say("[I] loading tensors completed, taking 0.25s (read: 0.10s, memcpy: 0.00s) --- model_loader.cpp:1400")
    if env("FAKE_SD_FAIL"):
        say(env("FAKE_SD_FAIL"))
        return 3
    if env("FAKE_SD_REPORT_ZERO"):
        say("[E] ggml_vulkan: Device memory allocation failed: Vulkan0 reported free 0.00 MB --- ggml-vulkan.cpp:1")
    time.sleep(float(env("FAKE_SD_SLEEP") or 0))
    say("[I] sampling using Euler method --- request.cpp:414")
    gate_after = int(env("FAKE_SD_GATE_AFTER") or 0)
    for n in range(1, steps + 1):
        if env("FAKE_SD_GATE") and gate_after and n == gate_after + 1:
            deadline = time.monotonic() + 30
            while not os.path.exists(env("FAKE_SD_GATE")) and time.monotonic() < deadline:
                time.sleep(0.02)
        eta = " - ETA 00:%02d" % (steps - n) if n < steps else ""
        sys.stdout.write("\r  |%s| %d/%d -   1.20s/it%s\x1b[K" % ("=" * n, n, steps, eta))
        sys.stdout.flush()
    sys.stdout.write("\n")
    if times:
        say("[I] sampling completed, taking 4.80s --- image.cpp:907")
    for n in range(1, 37):  # the VAE decodes by tiles and draws its own bar after the steps
        sys.stdout.write("\r  |=>  | %2d/36 -   1.27it/s - ETA 00:%02d\x1b[K" % (n, 36 - n))
    sys.stdout.write("\n")
    sys.stdout.flush()
    if times:
        say("[I] decode_first_stage completed, taking 0.75s --- image.cpp:632")
    if env("FAKE_SD_NO_IMAGE"):
        return 0
    with open(flags["-o"], "wb") as fh:
        fh.write(png_bytes(int(flags.get("-W", 8)), int(flags.get("-H", 8)), (10, 20, 30)))
    say("[I] 1/1 images saved --- main.cpp:572")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
