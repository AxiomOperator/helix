package config

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"
)

const DefaultPath = "/etc/linux-command-agent/config.toml"

type Config struct {
	ServerURL                string
	NodeID                   string
	AgentToken               string
	HeartbeatIntervalSeconds int
	InventoryIntervalSeconds int
	LogLevel                 string
}

func Default() Config {
	return Config{
		HeartbeatIntervalSeconds: 15,
		InventoryIntervalSeconds: 300,
		LogLevel:                 "info",
	}
}

func Load(path string) (Config, error) {
	if path == "" {
		path = DefaultPath
	}

	cfg := Default()
	file, err := os.Open(path)
	if err != nil {
		return cfg, err
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}

		key, value, ok := strings.Cut(line, "=")
		if !ok {
			continue
		}

		key = strings.TrimSpace(key)
		value = strings.Trim(strings.TrimSpace(value), `"`)

		switch key {
		case "server_url":
			cfg.ServerURL = value
		case "node_id":
			cfg.NodeID = value
		case "agent_token":
			cfg.AgentToken = value
		case "heartbeat_interval_seconds":
			if parsed, err := strconv.Atoi(value); err == nil {
				cfg.HeartbeatIntervalSeconds = parsed
			}
		case "inventory_interval_seconds":
			if parsed, err := strconv.Atoi(value); err == nil {
				cfg.InventoryIntervalSeconds = parsed
			}
		case "log_level":
			cfg.LogLevel = value
		}
	}

	return cfg, scanner.Err()
}

func Save(path string, cfg Config) error {
	if path == "" {
		path = DefaultPath
	}

	if err := os.MkdirAll(filepath.Dir(path), 0o700); err != nil {
		return err
	}

	contents := fmt.Sprintf(`server_url = %q
node_id = %q
agent_token = %q
heartbeat_interval_seconds = %d
inventory_interval_seconds = %d
log_level = %q
`, cfg.ServerURL, cfg.NodeID, cfg.AgentToken, cfg.HeartbeatIntervalSeconds, cfg.InventoryIntervalSeconds, cfg.LogLevel)
	return os.WriteFile(path, []byte(contents), 0o600)
}
