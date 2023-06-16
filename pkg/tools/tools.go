package tools

import (
	"bytes"
	"fmt"
	"log"
	"os/exec"
	"sync"
    "strings"
)

func RunCommandv1(command string, args ...string) (string, error) {

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

func RunCmd(command string) (string, error) {
	//cmd := exec.Command(command)
	cmd := exec.Command("bash", "-c", command)
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

    /*	
    err := cmd.Run()
	if err != nil {
		return "", fmt.Errorf("command execution failed: %v: %s", err, stderr.String())
	}
    */

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

//func CaptureCommand(command string, args ...string) (string, error) {
    //cmd := exec.Command(command, args...)
func CommandOutput(command string) (string, error) {

	//cmd := exec.Command(command)
    cmd := exec.Command("bash", "-c", command)

	output, err := cmd.Output()
	if err != nil {
		exitErr, ok := err.(*exec.ExitError)
		if !ok {
			return "", fmt.Errorf("failed to run command: %v", err)
		}

		return "", fmt.Errorf("command exited with error: %v", exitErr)
	}

	return string(output), nil
}


func RunCommand(command string) (string, int, error) {

    parts := strings.Fields(command)
    cmd := exec.Command(parts[0], parts[1:]...)

	// Capture the standard output
	output, err := cmd.Output()
	if err != nil {
		// Check if the error is an exit status error
		exitErr, ok := err.(*exec.ExitError)
		if !ok {
			return "", -1, err
		}

		// Get the exit status
		exitCode := exitErr.ExitCode()
		return "", exitCode, nil
	}

	// Get the exit status
	exitCode := cmd.ProcessState.ExitCode()

	return string(output), exitCode, nil
}


