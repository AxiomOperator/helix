package main

import (
	"fmt"
	"os"

	"linux-command-center/agent/internal/version"
)

func main() {
	args := os.Args[1:]
	if len(args) == 0 || args[0] == "help" || args[0] == "--help" || args[0] == "-h" {
		printHelp()
		return
	}

	switch args[0] {
	case "version", "--version", "-v":
		fmt.Println(version.String())
	default:
		fmt.Fprintf(os.Stderr, "unsupported command %q\n\n", args[0])
		printHelp()
		os.Exit(1)
	}
}

func printHelp() {
	fmt.Println("linux-command-agent")
	fmt.Println("")
	fmt.Println("Usage:")
	fmt.Println("  command-agent version")
	fmt.Println("  command-agent --version")
	fmt.Println("  command-agent help")
}
