package main

import (
	"fmt"
	"log"
	"os"
	"time"
	"database/sql"

	_ "github.com/mattn/go-sqlite3"

	"sentinel/golang/db"
)

var version = "1.0.0"

func main() {

    configs, err := getConfigs()
    if err != nil {
        panic(err)
    }

    // Use the retrieved configs as needed
    //for _, config := range configs {
    //		fmt.Printf("Retrieved Config: %s %s %s\n", config.Name, config.Data, config.Timestamp)
    //}

    if len(os.Args) > 1 {

	switch os.Args[1] {
	case "--help", "-help", "help":
		printUsage()
	case "--version", "-version", "version":
		fmt.Println("Version: ", version)
	case "list-configs":
		listConfigs(configs)
	case "update-config":

		if len(os.Args) != 4 {
			fmt.Println("Invalid arguments. Usage: update-config name data")
			return
		}
		//err := addConfig(os.Args[2], os.Args[3], os.Args[4])

		//currentTime := time.Now()
		//timestamp := currentTime.Format("2006-01-02 15:04:05")


                now := time.Now()
		//err := addConfig(os.Args[2], os.Args[3], timestamp)
		err := addConfig(os.Args[2], os.Args[3], now.Format(time.RFC822))
		if err != nil {
			log.Fatal(err)
		}
		fmt.Println("Config added successfully!")

	default:
		fmt.Println("Invalid argument ", os.Args[1])
	
	}

    }

}

func printUsage() {

    usage := `Usage: sentinel [options]

Options:
  --help|-help|help           Display this help message
  --version|-version|version  Display version

  list-configs
    update-config name data
      - Add a new config with the specified name, data
      - Example: add-config config-1 "{}"
    delete-config name
    clear-configs

`
    fmt.Println(usage)
}

//func addConfig() {
//	db.AddConfigs(database, "config-1", "{}", "2023-06-09")
//}


func addConfig(name, data, timestamp string) error {
	database, err := sql.Open("sqlite3", "sentinel.db")
	if err != nil {
		return err
	}
	defer database.Close()

	if err = db.AddConfigs(database, name, data, timestamp); err != nil {
		return err
	}

	return nil
}



func listConfigs(configs []db.Config) {
	//configs, err := getConfigs()
	//if err != nil {
	//	log.Fatal(err)
	//}

	fmt.Println("Configs:")
	for _, config := range configs {
		fmt.Printf("%s %s %s\n", config.Name, config.Data, config.Timestamp)
	}
}


func getConfigs() ([]db.Config, error) {

	var configs []db.Config

	if _, err := os.Stat("sentinel.db"); err == nil {
		//fmt.Printf("File exists\n")
		database, err := sql.Open("sqlite3", "sentinel.db")
		if err != nil {
			return nil, err
		}
		defer database.Close()

		configs, err = db.FetchConfigs(database)
		if err != nil {
			return nil, err
		}

		//for _, config := range configs {
		//	fmt.Printf("Config: %s %s %s\n", config.Name, config.Data, config.Timestamp)
		//}

	} else {
		//fmt.Printf("Create db file\n")
		file, err := os.Create("sentinel.db")
		if err != nil {
			return nil, err
		}
		file.Close()

		database, err := sql.Open("sqlite3", "sentinel.db")
		if err != nil {
			return nil, err
		}
		defer database.Close()

		db.CreateTables(database)

		// db.AddUsers(database, "Karl", "Rink", "Golang Developer", 2023)
		configs, err = db.FetchConfigs(database)
		if err != nil {
			return nil, err
		}
	}

	return configs, nil
}


