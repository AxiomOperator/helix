package config

import (
	"bufio"
	"os"
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
