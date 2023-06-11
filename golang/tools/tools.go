package tools

import (
	"bytes"
	"fmt"
	"log"
	"os/exec"
	"sync"
)

func RunCommand(command string, args ...string) (string, error) {

	cmd := exec.Command(command, args...)

	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	var wg sync.WaitGroup
	wg.Add(1)

	go func() {
		defer wg.Done()
		if err := cmd.Run(); err != nil {
			log.Fatalf("Command execution failed: %v", err)
		}
	}()

	wg.Wait()

	if stderr.Len() > 0 {
		return "", fmt.Errorf("Error executing %s command: %s", command, stderr.String())
	}

	return stdout.String(), nil

}

