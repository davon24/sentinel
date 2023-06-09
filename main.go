
package main

import (
	//"log"
	"os"
	"fmt"
	"database/sql"

	_ "github.com/mattn/go-sqlite3"

	"sentinel/golang/db"
)


func main() {

    if _, err := os.Stat("sentinel.db"); err == nil {
        fmt.Printf("File exists\n")
        database, _ := sql.Open("sqlite3", "sentinel.db")
	db.ReadConfigs(database)
        //db.FetchRecords(database)

    } else {
        file, err := os.Create("sentinel.db")
        if err != nil {
            //log.Fatal(err)
	    panic(err)
        }
	file.Close()
        database, _ := sql.Open("sqlite3", "sentinel.db")
	db.CreateTables(database)

	db.AddUsers(database, "Karl", "Rink", "Golang Developer", 2023)
	database.Close()
    }


}


