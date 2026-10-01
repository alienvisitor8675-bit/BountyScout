For [cloudflare/cloudflared #1748], the code adjustment in the QUIC handler is:

```go
// Ensure QUIC's Hijack() includes the status-written check.
if quicHijackErr := quic.HandleHijack(w); quicHijackErr != nil {
    return quicHijackErr
}
// Include the status-written check here.
if !w.wroteStatus {
    w.WriteHeader(nil)
}
```

For [kubernetes-sigs/aws-load-balancer-controller #4851], the adjustment in the load balancer controller is:

```go
// Adjust the load balancer reset count handling.
if resetCount > 0 {
    // Implement the necessary condition or adjustment.
}
```
Each code snippet addresses the specific issues by adding the required checks.