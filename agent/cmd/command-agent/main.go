package main

import (
	"fmt"
	"os"

	"linux-command-center/agent/internal/config"
	"linux-command-center/agent/internal/enroll"
	"linux-command-center/agent/internal/transport"
	"linux-command-center/agent/internal/version"
)

func main() {
	args := os.Args[1:]
	if len(args) == 0 || args[0] == "help" || args[0] == "--help" || args[0] == "-h" {
		printHelp()
		return
	}

	switch args[0] {
	case "enroll":
		if err := runEnroll(args[1:]); err != nil {
			fmt.Fprintf(os.Stderr, "enroll failed: %v\n", err)
			os.Exit(1)
		}
	case "connect":
		if err := runConnect(args[1:]); err != nil {
			fmt.Fprintf(os.Stderr, "connect failed: %v\n", err)
			os.Exit(1)
		}
	case "version", "--version", "-v":
		fmt.Println(version.String())
	default:
		fmt.Fprintf(os.Stderr, "unsupported command %q\n\n", args[0])
		printHelp()
		os.Exit(1)
	}
}

func runEnroll(args []string) error {
	serverURL := ""
	token := ""
	configPath := config.DefaultPath
	for i := 0; i < len(args); i++ {
		switch args[i] {
		case "--server-url":
			i++
			if i < len(args) {
				serverURL = args[i]
			}
		case "--token":
			i++
			if i < len(args) {
				token = args[i]
			}
		case "--config":
			i++
			if i < len(args) {
				configPath = args[i]
			}
		default:
			return fmt.Errorf("unsupported enroll option %q", args[i])
		}
	}
	return enroll.Run(serverURL, token, configPath)
}

func runConnect(args []string) error {
	configPath := config.DefaultPath
	once := false
	for i := 0; i < len(args); i++ {
		switch args[i] {
		case "--config":
			i++
			if i < len(args) {
				configPath = args[i]
			}
		case "--once":
			once = true
		default:
			return fmt.Errorf("unsupported connect option %q", args[i])
		}
	}
	return transport.Run(configPath, once)
}

func printHelp() {
	fmt.Println("linux-command-agent")
	fmt.Println("")
	fmt.Println("Usage:")
	fmt.Println("  command-agent enroll --server-url http://localhost:8000 --token <enrollment-token> [--config path]")
	fmt.Println("  command-agent connect [--config path] [--once]")
	fmt.Println("  command-agent version")
	fmt.Println("  command-agent --version")
	fmt.Println("  command-agent help")
}
