package server

import (
	"context"
	"log/slog"
	"sync"
)

type EventRingBuffer struct {
	mu     sync.RWMutex
	records []slog.Record
	head   int
	count  int
	size   int
	next   slog.Handler
}

func NewEventRingBuffer(size int, next slog.Handler) *EventRingBuffer {
	return &EventRingBuffer{
		records: make([]slog.Record, size),
		size:    size,
		next:    next,
	}
}

func (r *EventRingBuffer) Enabled(ctx context.Context, level slog.Level) bool {
	return r.next.Enabled(ctx, level)
}

func (r *EventRingBuffer) Handle(ctx context.Context, rec slog.Record) error {
	// Need to clone the record if we are storing it, especially its attrs
	// but slog.Record handles this fairly well.
	cloned := rec.Clone()

	r.mu.Lock()
	r.records[r.head] = cloned
	r.head = (r.head + 1) % r.size
	if r.count < r.size {
		r.count++
	}
	r.mu.Unlock()

	return r.next.Handle(ctx, rec)
}

func (r *EventRingBuffer) WithAttrs(attrs []slog.Attr) slog.Handler {
	return &EventRingBuffer{
		records: r.records, // shared
		head:    r.head,
		count:   r.count,
		size:    r.size,
		next:    r.next.WithAttrs(attrs),
	}
}

func (r *EventRingBuffer) WithGroup(name string) slog.Handler {
	return &EventRingBuffer{
		records: r.records, // shared
		head:    r.head,
		count:   r.count,
		size:    r.size,
		next:    r.next.WithGroup(name),
	}
}

// GetEvents returns a chronologically ordered slice of the recent records.
func (r *EventRingBuffer) GetEvents() []map[string]any {
	r.mu.RLock()
	defer r.mu.RUnlock()

	res := make([]map[string]any, 0, r.count)

	process := func(rec slog.Record) {
		m := make(map[string]any)
		m["time"] = rec.Time.Format("2006-01-02T15:04:05.999Z07:00")
		m["level"] = rec.Level.String()
		m["msg"] = rec.Message
		rec.Attrs(func(a slog.Attr) bool {
			m[a.Key] = a.Value.Any()
			return true
		})
		res = append(res, m)
	}

	if r.count < r.size {
		for i := 0; i < r.count; i++ {
			process(r.records[i])
		}
	} else {
		for i := 0; i < r.size; i++ {
			idx := (r.head + i) % r.size
			process(r.records[idx])
		}
	}
	return res
}
