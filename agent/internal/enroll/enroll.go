package enroll

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"runtime"
	"strings"
	"time"

	"linux-command-center/agent/internal/config"
)

type response struct {
	NodeID     string `json:"node_id"`
	AgentToken string `json:"agent_token"`
}

func Run(serverURL string, enrollmentToken string, configPath string) error {
	if serverURL == "" {
		return fmt.Errorf("server URL is required")
	}
	if enrollmentToken == "" {
		return fmt.Errorf("enrollment token is required")
	}

	hostname, _ := os.Hostname()
	machineID := readMachineID()
	if machineID == "" {
		machineID = hostname
	}

	payload := map[string]string{
		"enrollment_token": enrollmentToken,
		"machine_id":       machineID,
		"hostname":         hostname,
		"os_name":          readOSName(),
		"kernel":           readFirstLine("/proc/sys/kernel/osrelease"),
		"architecture":     runtime.GOARCH,
	}
	body, err := json.Marshal(payload)
	if err != nil {
		return err
	}

	client := http.Client{Timeout: 15 * time.Second}
	resp, err := client.Post(strings.TrimRight(serverURL, "/")+"/agent/enroll", "application/json", bytes.NewReader(body))
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("enrollment failed with status %s", resp.Status)
	}

	var enrolled response
	if err := json.NewDecoder(resp.Body).Decode(&enrolled); err != nil {
		return err
	}

	cfg := config.Default()
	cfg.ServerURL = strings.TrimRight(serverURL, "/")
	cfg.NodeID = enrolled.NodeID
	cfg.AgentToken = enrolled.AgentToken
	if err := config.Save(configPath, cfg); err != nil {
		return err
	}

	fmt.Printf("enrolled node %s\n", enrolled.NodeID)
	return nil
}

func readMachineID() string {
	for _, path := range []string{"/etc/machine-id", "/var/lib/dbus/machine-id"} {
		contents, err := os.ReadFile(path)
		if err == nil {
			return strings.TrimSpace(string(contents))
		}
	}
	return ""
}

func readOSName() string {
	contents, err := os.ReadFile("/etc/os-release")
	if err != nil {
		return runtime.GOOS
	}
	for _, line := range strings.Split(string(contents), "\n") {
		key, value, ok := strings.Cut(line, "=")
		if ok && key == "PRETTY_NAME" {
			return strings.Trim(strings.TrimSpace(value), `"`)
		}
	}
	return runtime.GOOS
}

func readFirstLine(path string) string {
	contents, err := os.ReadFile(path)
	if err != nil {
		return runtime.GOOS
	}
	return strings.TrimSpace(string(contents))
}
