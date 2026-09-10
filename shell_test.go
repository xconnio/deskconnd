package deskconn_test

import (
	"bytes"
	"context"
	"fmt"
	"sync"
	"testing"

	"github.com/stretchr/testify/require"

	"github.com/xconnio/deskconn"
	"github.com/xconnio/xconn-go"
)

func setupDeskconn(t *testing.T) (*xconn.Session, *xconn.Session) {
	t.Helper()
	callee, caller := setupRouterAndConnectSessions(t)
	d := deskconn.NewDeskconn(nil, nil, nil, false, t.TempDir())
	require.NoError(t, d.Register(callee))
	return callee, caller
}

func TestExecHandlerMissingKey(t *testing.T) {
	_, caller := setupDeskconn(t)

	sent := false
	callResp := caller.Call(deskconn.ProcedureExec).
		ProgressSender(func(ctx context.Context) *xconn.Progress {
			if !sent {
				sent = true
				return xconn.NewProgress([]byte("payload-without-key-marker"))
			}
			return xconn.NewFinalProgress()
		}).Do()

	require.ErrorContains(t, callResp.Err, "missing encryption key")
}

func TestExecHandlerKeyExchange(t *testing.T) {
	_, caller := setupDeskconn(t)

	clientPubKey, clientPrivKey, err := deskconn.CreateX25519KeyPair()
	require.NoError(t, err)

	var cbErr error
	var closeOnce sync.Once
	progressChan := make(chan *xconn.Progress, 16)
	closeChan := func() { closeOnce.Do(func() { close(progressChan) }) }
	firstMsg := true
	firstServerMsg := true

	callResp := caller.Call(deskconn.ProcedureExec).
		ProgressSender(func(ctx context.Context) *xconn.Progress {
			if firstMsg {
				firstMsg = false
				return xconn.NewProgress(
					append([]byte("SIZE:80:24:KEY:"), clientPubKey...),
					[]string{"echo", "hello"},
				)
			}
			select {
			case p, ok := <-progressChan:
				if !ok {
					return xconn.NewFinalProgress()
				}
				return p
			case <-ctx.Done():
				return xconn.NewFinalProgress()
			}
		}).
		ProgressReceiver(func(pr *xconn.ProgressResult) {
			if len(pr.Args()) == 0 {
				closeChan()
				return
			}
			data, _ := pr.Args()[0].([]byte)
			if !firstServerMsg {
				return
			}
			firstServerMsg = false
			if !bytes.HasPrefix(data, []byte("KEY:")) {
				cbErr = fmt.Errorf("expected KEY: prefix in first server message")
				closeChan()
				return
			}
			sharedSecret, kErr := deskconn.PerformKeyExchange(clientPrivKey, data[4:])
			if kErr != nil {
				cbErr = kErr
				closeChan()
				return
			}
			if _, kErr = deskconn.DeriveKeyHKDF(sharedSecret, []byte("frontendToBackend")); kErr != nil {
				cbErr = kErr
				closeChan()
			}
		}).Do()

	require.NoError(t, cbErr)
	require.NoError(t, callResp.Err)
}
