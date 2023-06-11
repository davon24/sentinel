package main

import (
	"bufio"
	"embed"
	"fmt"
	"os"
	"strings"
)

//go:embed resources/manuf
var embedFS embed.FS

func searchManufacturer(mac string, content string) string {

	scanner := bufio.NewScanner(strings.NewReader(content))

	for scanner.Scan() {

		line := scanner.Text()
		parts := strings.Split(line, "\t")

		//if len(parts) >= 3 && parts[0] == mac {
		if len(parts) >= 3 && strings.HasPrefix(parts[0], mac) {
			//return parts[2]
			return parts[1] + " (" + parts[2] + ")"
		}

	}

	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, "Error reading embedded file:", err)
	}

	return "Manufacturer not found"
}

func main() {

    if len(os.Args) > 1 {

        mac := os.Args[1]
        mac = strings.ToUpper(mac) // Convert mac address to UPPERCASE for matching

        content, err := embedFS.ReadFile("resources/manuf")
        if err != nil {
            fmt.Fprintln(os.Stderr, "Error reading embedded file:", err)
        }

        parts := strings.Split(mac, ":")

        for i := len(parts); i > 0; i-- {
            subMac := strings.Join(parts[:i], ":")
            //fmt.Fprintln(os.Stdout, subMac)
            manufacturer := searchManufacturer(subMac, string(content))
            if manufacturer != "Manufacturer not found" {
                fmt.Printf("Manufacturer for MAC address %s is %s\n", mac, manufacturer)
                return
            }
        }
	    fmt.Printf("Manufacturer not found for MAC address %s\n", mac)

    } else {
        fmt.Fprintln(os.Stderr, "Usage: " + os.Args[0] + " 00:00:00:00:00:00")
        os.Exit(1)
    }

}


