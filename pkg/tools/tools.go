package tools

import (
	"bytes"
	//"fmt"
	//"log"
	"os/exec"
	"sync"
    "strings"
)

func RunCommandWG(command string, wg *sync.WaitGroup) (string, string, int, error) {
    defer wg.Done()

    parts := strings.Fields(command)
    cmd := exec.Command(parts[0], parts[1:]...)

    // Create buffers to capture stdout and stderr
    var stdout, stderr bytes.Buffer
    cmd.Stdout = &stdout
    cmd.Stderr = &stderr

    // Run the command
    err := cmd.Run()
    if err != nil {
        // Check if the error is an exit status error
        exitErr, ok := err.(*exec.ExitError)
        if !ok {
            return "", "", -1, err
        }

        // Get the exit status
        exitCode := exitErr.ExitCode()
        if exitCode == 1 {
            return stdout.String(), stderr.String(), exitCode, nil
        }

        return "", "", exitCode, nil
    }

    // Get the exit status
    exitCode := cmd.ProcessState.ExitCode()

    return stdout.String(), stderr.String(), exitCode, nil
}

func RunCommand(command string) (string, string, int, error) {

    parts := strings.Fields(command)
    cmd := exec.Command(parts[0], parts[1:]...)

    // Create buffers to capture stdout and stderr
    var stdout, stderr bytes.Buffer
    cmd.Stdout = &stdout
    cmd.Stderr = &stderr

    // Run the command
    err := cmd.Run()
    if err != nil {
        // Check if the error is an exit status error
        exitErr, ok := err.(*exec.ExitError)
        if !ok {
            return "", "", -1, err
        }

        // Get the exit status
        exitCode := exitErr.ExitCode()
        if exitCode == 1 {
            return stdout.String(), stderr.String(), exitCode, nil
        }

        return "", "", exitCode, nil
    }

    // Get the exit status
    exitCode := cmd.ProcessState.ExitCode()

    return stdout.String(), stderr.String(), exitCode, nil
}


