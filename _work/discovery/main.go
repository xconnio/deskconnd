package discovery

import (
	"fmt"
	"github.com/grandcat/zeroconf"
	"os"
)

var mdns *zeroconf.Server

func PublishName(realm string, serviceName string) *zeroconf.Server {
	hostname, _ := os.Hostname()
	if mdns == nil {
		mdns, _ = zeroconf.Register(hostname, fmt.Sprintf("_%s._tcp", serviceName), "local.",
			5020, []string{fmt.Sprintf("realm=%s", realm)}, nil)
		return mdns
	}
	return nil
}

func UnPublish() bool {
	if mdns == nil {
		return false
	} else {
		mdns.Shutdown()
		return true
	}
}
