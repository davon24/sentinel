package main

import (
    "fmt"
    "os"
    "strings"

    "sentinel/pkg/manuf"
)


func main() {

    if len(os.Args) > 1 {

        mac := os.Args[1]
        mac = strings.ToUpper(mac) // Convert mac address to UPPERCASE for matching

        content, err := manuf.EmbedFS.ReadFile("resources/manuf")
        if err != nil {
            fmt.Fprintln(os.Stderr, "Error reading embedded file:", err)
        }

        parts := strings.Split(mac, ":")
        for i := len(parts); i > 0; i-- {
            subMac := strings.Join(parts[:i], ":")
            manufacturer := manuf.SearchManufacturer(subMac, string(content))
            if manufacturer != "Manufacturer Not Found" {
                fmt.Printf("%s\n", manufacturer)
                return
            }
        }
	    fmt.Printf("Manufacturer Not Found %s\n", mac)

    } else {
        fmt.Fprintln(os.Stderr, "Usage: " + os.Args[0] + " 00:00:00:00:00:00")
        os.Exit(1)
    }

}
