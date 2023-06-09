
package db

import (
	"log"
	"database/sql"

	_ "github.com/mattn/go-sqlite3"
)


func CreateTables(db *sql.DB) {

    users_table := `CREATE TABLE users (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "FirstName" TEXT,
        "LastName" TEXT,
	"Desc" TEXT,
        "Number" INT);`
    query, err := db.Prepare(users_table)
    if err != nil {
        log.Fatal(err)
    }
    query.Exec()
    log.Println("Table 'users' created successfully!")

    configs_table := `CREATE TABLE configs (
        "name" TEXT PRIMARY KEY NOT NULL,
        "timestamp" TEXT,
        "data" JSON);`
    query2, err := db.Prepare(configs_table)
    if err != nil {
        log.Fatal(err)
    }
    query2.Exec()
    log.Println("Table 'configs' created successfully!")

}

func AddUsers(db *sql.DB, FirstName string, LastName string, Desc string, Number int) {
    records := `INSERT INTO users(FirstName, LastName, Desc, Number) VALUES (?, ?, ?, ?)`
    query, err := db.Prepare(records)
    if err != nil {
        log.Fatal(err)
    }
    _, err = query.Exec(FirstName, LastName, Desc, Number)
    if err != nil {
        log.Fatal(err)
    }
}

func FetchRecords(db *sql.DB) {
    record, err := db.Query("SELECT * FROM users")
    if err != nil {
        log.Fatal(err)
    }
    defer record.Close()
    for record.Next() {
        var id int
        var FirstName string
        var LastName string
        var Desc string
        var Number int
        record.Scan(&id, &FirstName, &LastName, &Desc, &Number)
        log.Printf("User: %d %s %s %s %d", id, FirstName, LastName, Desc, Number)
    }
}

func ReadConfigs(db *sql.DB) {
    record, err := db.Query("SELECT * FROM configs")
    if err != nil {
        log.Fatal(err)
    }
    defer record.Close()
    for record.Next() {
        var name string
        var timestamp string
        var data string
        record.Scan(&name, &timestamp, &data)
        log.Printf("Config: %s %s %s", name, timestamp, data)
    }
}


