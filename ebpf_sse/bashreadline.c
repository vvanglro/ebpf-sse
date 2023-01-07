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
