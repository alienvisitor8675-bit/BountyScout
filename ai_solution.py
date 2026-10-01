Here is the refactored code for the issue:

```go
package expapi

import (
	"github.com/prometheus/prometheus/textproto"
)

// WriteResponse writes the headers and the body.
func WriteResponse(w textproto.ResponseWriter, r *http.Request) {
	// WriteResponseHeaders adds the headers.
	WriteResponseHeaders(w, r)
}

// WriteResponseHeaders adds the headers.
func WriteResponseHeaders(w textproto.ResponseWriter, r *http.Request) {
	if r.Context().Value("Status") != nil {
		w.WriteHeader(r.Context().Value("Status").(int))
	}

	if r.Context().Value(textproto.ContentType) != nil {
		w.Header().Set(textproto.ContentType, r.Context().Value(textproto.ContentType).(string))
	}

	if r.Context().Value(textproto.PrometheusMetric) != nil {
		w.Header().Set(textproto.PrometheusMetric, r.Context().Value(textproto.PrometheusMetric).(string))
	}
}
```

This refactored code improves the handling of headers by cleanly separating each condition into its own if statement, making the code more readable and maintainable.