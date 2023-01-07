# https://github.com/iovisor/bcc/blob/b57dbb397cb110433c743685a7d1eb1fb9c3b1f9/tools/bashreadline.py

from __future__ import print_function
from bcc import BPF
from time import strftime

# load BPF program
bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>
struct str_t {
    u32 pid;
    u32 uid;
    char str[80];
};
BPF_PERF_OUTPUT(events);
int printer(struct pt_regs *ctx) {
    struct str_t data  = {};
    char comm[TASK_COMM_LEN] = {};
    if (!PT_REGS_RC(ctx))
        return 0;
    u32 uid = bpf_get_current_uid_gid() & 0xffffffff;
    data.uid = uid;
    data.pid = bpf_get_current_pid_tgid() >> 32;
    bpf_probe_read_user(&data.str, sizeof(data.str), (void *)PT_REGS_RC(ctx));
    bpf_get_current_comm(&comm, sizeof(comm));
    if (comm[0] == 'b' && comm[1] == 'a' && comm[2] == 's' && comm[3] == 'h' && comm[4] == 0 ) {
        events.perf_submit(ctx,&data,sizeof(data));
    }
    return 0;
};
"""

b = BPF(text=bpf_text)
b.attach_uretprobe(name="/bin/bash", sym="readline", fn_name="printer")

# header
print("%-9s %-7s %-7s %s" % ("TIME", "UID", "PID", "COMMAND"))


def print_event(cpu, data, size):
    event = b["events"].event(data)
    print("%-9s %-7d %-7d %s" % (strftime("%H:%M:%S"), event.uid, event.pid,
                                 event.str.decode('utf-8', 'replace')))


b["events"].open_perf_buffer(print_event)
while 1:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        exit()
