package main

import (
	"context"
	"encoding/hex"
	"errors"
	"github.com/gammazero/nexus/v3/client"
	"log"

	//"flag"
	"fmt"
	"github.com/sirupsen/logrus"
	"os"
	"os/signal"
	"time"

	"github.com/gammazero/nexus/v3/router/auth"
	"github.com/gammazero/nexus/v3/router"
	"github.com/gammazero/nexus/v3/wamp"
)

type keyStore struct {
	provider string
	publicKey   string
}

func (ks *keyStore) AuthKey(authid, authmethod string) ([]byte, error) {
	if authid != "jdoe" {
		return nil, errors.New("no such user: " + authid)
	}
	switch authmethod {
	case "cryptosign":
		// Lookup the user's key.
		return hex.DecodeString(ks.publicKey)
	}
	return nil, errors.New("unsupported authmethod")
}

func (ks *keyStore) AuthRole(authid string) (string, error) {
	if authid != "jdoe" {
		return "", errors.New("no such user: " + authid)
	}
	return "user", nil
}

func (ks *keyStore) PasswordInfo(authid string) (string, int, int) {
	return "", 0, 0
}

func (ks *keyStore) Provider() string { return ks.provider }


func main() {
	logger := logrus.New()

	var tks = &keyStore{
		provider:  "static",
		publicKey: "f1c01c480112705361beb5e4eda8544f951abb7ca918f76327a3a5240f352292",
	}

	cryptosign := auth.NewCryptoSignAuthenticator(tks, 10 * time.Second)

	// Create router instance.
	routerConfig := &router.Config{
		RealmConfigs: []*router.RealmConfig{
			{
				URI:           wamp.URI("com.crossbario.fabric"),
				AnonymousAuth: true,
				AllowDisclose: true,
				MetaStrict: true,
				Authenticators: []auth.Authenticator{cryptosign},
			},
		},
		Debug: false,
	}

	nxr, err := router.NewRouter(routerConfig, nil)
	if err == nil {
		defer nxr.Close()
	} else {
		logger.Fatal(err)
	}

	netAddr := "localhost"
	wsPort := 9000

	// Setup listening websocket transport
	// Create websocket server.
	wss := router.NewWebsocketServer(nxr)
	wss.Upgrader.EnableCompression = true
	wss.EnableTrackingCookie = true
	wss.KeepAlive = 30 * time.Second

	// Run websocket server.
	wsAddr := fmt.Sprintf("%s:%d", netAddr, wsPort)
	wsCloser, err := wss.ListenAndServe(wsAddr)
	if err == nil {
		logger.Infoln(fmt.Sprintf("Websocket server listening on ws://%s:%d/ws", netAddr, wsPort))
		defer wsCloser.Close()
	} else {
		logger.Fatal(err)
	}

	cfg := client.Config{
		Realm:  "com.crossbario.fabric",
		Logger: logger,
	}
	callee, _ := client.ConnectLocal(nxr, cfg)

	proc := "crossbarfabriccenter.mrealm.get_status"
	if err = callee.Register(proc, getStatus, nil); err != nil {
		logger.Errorf("Failed to register %q: %s", proc, err)
	}
	log.Printf("Registered procedure %q with router", proc)

	// Wait for SIGINT (CTRL-c), then close servers and exit.
	shutdown := make(chan os.Signal, 1)
	signal.Notify(shutdown, os.Interrupt)
	<-shutdown
}

func getStatus(ctx context.Context, inv *wamp.Invocation) client.InvokeResult {
	now := time.Now()
	results := wamp.List{fmt.Sprintf("UTC: %s", now.UTC())}

	return client.InvokeResult{Args: results}
}
