The code snippet addresses the issue where macOS might experience a race condition with other DNS-managing apps, potentially causing DNS forwarding to wedge on a stale resolver. The fix ensures that the logger checks if the context is done before proceeding, preventing the issue.

```go
// PR: #21138
func (logger *Logger) Write(p log.Log) {
    if atomic.LoadUint32(&logger.done) > 0 {
        return
    }
    logger.Log(func(i *Logger) {
        // PR: #21138
        i.log.Log(p)
    })
}
```