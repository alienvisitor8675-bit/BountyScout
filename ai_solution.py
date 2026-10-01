```go
func maybeAddFwmarkToDstIfUnset(m *cilium.NDRoute) {
    if m.src_valid_mark == 1 {
        mDst := m.Dst.(*cilium.NDRoute).Dst
        if mDst.src_valid_mark == 0 {
            mDst.fwmark = m.fwmark
            mDst.src_valid_mark = 1
        }
    }
}
```