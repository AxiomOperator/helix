package transport

import (
	"fmt"
	"net/url"
	"strings"
	"time"

	"github.com/gorilla/websocket"

	"linux-command-center/agent/internal/config"
)

func Run(configPath string, once bool) error {
	cfg, err := config.Load(configPath)
	if err != nil {
		return err
	}
	if cfg.ServerURL == "" || cfg.NodeID == "" || cfg.AgentToken == "" {
		return fmt.Errorf("server_url, node_id, and agent_token are required in config")
	}

	for {
		err := connectOnce(cfg)
		if once {
			return err
		}
		if err != nil {
			fmt.Printf("agent connection failed: %v\n", err)
		} else {
			fmt.Println("agent disconnected")
		}
		time.Sleep(5 * time.Second)
	}
}

func connectOnce(cfg config.Config) error {
	wsURL, err := websocketURL(cfg.ServerURL)
	if err != nil {
		return err
	}

	conn, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
	if err != nil {
		return err
	}
	defer conn.Close()

	fmt.Printf("connected to %s\n", wsURL)
	if err := conn.WriteJSON(map[string]any{
		"type": "agent.auth",
		"payload": map[string]string{
			"node_id":     cfg.NodeID,
			"agent_token": cfg.AgentToken,
		},
	}); err != nil {
		return err
	}

	var authAck map[string]any
	if err := conn.ReadJSON(&authAck); err != nil {
		return err
	}
	if authAck["type"] != "agent.auth.ok" {
		return fmt.Errorf("agent authentication rejected")
	}
	fmt.Println("agent authenticated")

	if err := conn.WriteJSON(map[string]any{
		"type": "agent.hello",
		"payload": map[string]string{
			"node_id": cfg.NodeID,
		},
	}); err != nil {
		return err
	}

	for {
		var message map[string]any
		if err := conn.ReadJSON(&message); err != nil {
			return err
		}
		fmt.Printf("received %v\n", message["type"])
	}
}

func websocketURL(serverURL string) (string, error) {
	parsed, err := url.Parse(strings.TrimRight(serverURL, "/"))
	if err != nil {
		return "", err
	}
	switch parsed.Scheme {
	case "http":
		parsed.Scheme = "ws"
	case "https":
		parsed.Scheme = "wss"
	case "ws", "wss":
	default:
		return "", fmt.Errorf("unsupported server URL scheme %q", parsed.Scheme)
	}
	parsed.Path = strings.TrimRight(parsed.Path, "/") + "/ws/agent"
	return parsed.String(), nil
}
