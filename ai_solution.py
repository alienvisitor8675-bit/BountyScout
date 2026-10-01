```go
package quic

import (
	"context"
)

type Hijack interface {
	WriteStatus(code int, message string) error
}

func (h *Hijack) WriteStatus(code int, message string) error {
	if h.statusWritten {
		return nil
	}
	// Rest of the implementation
}
```