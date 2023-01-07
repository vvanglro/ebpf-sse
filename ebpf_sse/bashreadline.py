# https://github.com/iovisor/bcc/blob/b57dbb397cb110433c743685a7d1eb1fb9c3b1f9/tools/bashreadline.py

from __future__ import print_function
import httpx
from bcc import BPF
from time import strftime

client = httpx.Client(base_url="http://localhost:8000")
b = BPF(src_file="bashreadline.c")
b.attach_uretprobe(name="/bin/bash", sym="readline", fn_name="printer")


def print_event(cpu, data, size):
    event = b["events"].event(data)
    resp = client.post(url='/message', params={"event": "BashReadline", "message": "%-9s %-7d %-7d %s" % (
        strftime("%H:%M:%S"), event.uid, event.pid,
        event.str.decode('utf-8', 'replace'))})
    assert resp.json().get("success") is True


b["events"].open_perf_buffer(print_event)
while 1:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        exit()
