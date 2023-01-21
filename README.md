# ebpf-sse

Unite eBPF and Server-sent events

## run (m1 mac)

```shell
docker-compose -f docker-compose-m1.yml up
```

Enter http://127.0.0.1:7778/ebpf_sse/sse.html in Google Chrome, Then enter the container and execute the command to see
it on the web page.

```shell
docker exec -it  ebpf-sse-web-1  bash
```
https://user-images.githubusercontent.com/43594924/211340761-874c0fc7-3d34-4313-b35f-e1c5e7164252.mov

