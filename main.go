package main

import (
	"fmt"
//	"log"
	"os"
	"time"
    "encoding/json"
	"database/sql"

	_ "github.com/mattn/go-sqlite3"

	"sentinel/golang/db"
)

var version = "2.0.0-dev-pre-0"

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
		    fmt.Println("Version:", version)
            printSqlite3Version()
	    case "list-configs":
		    listConfigs(configs)
	    case "add-config":
            addConfig(configs)
	    case "delete-config":
            deleteConfig(configs)

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
  add-config name json
      - Add a new config with the specified name, json
      - Example: add-config config-1 '{"key":1}'
  delete-config name

`
    fmt.Println(usage)
}


func printSqlite3Version() {

    database, err := sql.Open("sqlite3", "sentinel.db")
    if err != nil {
        return
    }
    defer database.Close()

    version, err := db.Version(database)
    if err != nil {
        return
    }

    fmt.Println("Sqlite:", version)
}

func addConfig(configs []db.Config) {

	if len(os.Args) != 4 {
		fmt.Println("Invalid arguments. Usage: add-config name json")
		return
	}

	// Timestamp
	now := time.Now()
	timestamp := now.Format("2006-01-02T15:04:05")

	// Validate data as JSON
	isJSON := json.Valid([]byte(os.Args[3]))
	if !isJSON {
		fmt.Println("Invalid JSON!")
		return
	}

    //open database connect
	database, err := sql.Open("sqlite3", "sentinel.db")
	if err != nil {
		fmt.Println(err)
		return
	}
	defer database.Close()

    //add config data
	if err = db.AddConfig(database, os.Args[2], os.Args[3], timestamp); err != nil {
		fmt.Println(err)
		return
	}

	fmt.Println("Config added successfully!")
}

func deleteConfig(configs []db.Config) {

    if len(os.Args) != 3 {
        fmt.Println("Invalid arguments. Usage: delete-config name")
        return
    }

    //open database connect
    database, err := sql.Open("sqlite3", "sentinel.db")
    if err != nil {
		fmt.Println(err)
        return
    }
    defer database.Close()

    //delete config data
    if err = db.DeleteConfig(database, os.Args[2]); err != nil {
		fmt.Println(err)
        return
    }

    fmt.Println("Config deleted successfully!")
}



func listConfigs(configs []db.Config) {
	//configs, err := getConfigs()
	//if err != nil {
	//	log.Fatal(err)
	//}

	//fmt.Println("Configs:")
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

//db, err := sql.Open("sqlite3", ":memory:")

