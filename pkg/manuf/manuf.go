package manuf

import (
	"bufio"
	"embed"
	"log"
	"strings"
)

//go:embed resources/manuf
var EmbedFS embed.FS

func SearchManufacturer(mac string, content string) string {
	scanner := bufio.NewScanner(strings.NewReader(content))

	for scanner.Scan() {
		line := scanner.Text()
		parts := strings.Split(line, "\t")

		if len(parts) >= 3 && strings.HasPrefix(parts[0], mac) {
			return parts[1] + " (" + parts[2] + ")"
		}
	}

	if err := scanner.Err(); err != nil {
		log.Println("Error reading embedded file:", err)
	}

	return "Manufacturer Not Found"
}

