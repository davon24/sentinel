package db

import (
	"log"
	"database/sql"

	_ "github.com/mattn/go-sqlite3"
)

type Config struct {
    Name      string
    Data      string
    Timestamp string
}


func CreateTables(db *sql.DB) {

    configs_table := `CREATE TABLE configs (
        "Name" TEXT PRIMARY KEY NOT NULL,
        "Data" JSON,
        "Timestamp" TEXT);`
    query, err := db.Prepare(configs_table)
    if err != nil {
        log.Fatal(err)
    }
    query.Exec()
    log.Println("Table 'configs' created successfully!")

}

func AddConfigs(db *sql.DB, Name string,Data string, Timestamp string) error {

    records := `INSERT INTO configs (Name, Data, Timestamp) VALUES (?, ?, ?)`
    query, err := db.Prepare(records)
    if err != nil {
        //log.Fatal(err)
	return err
    }
    _, err = query.Exec(Name, Data, Timestamp)
    if err != nil {
        //log.Fatal(err)
	return err
    }
    return nil
}


func FetchConfigs(db *sql.DB) ([]Config, error) {
    rows, err := db.Query("SELECT * FROM configs")
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var configs []Config
    for rows.Next() {
        var config Config
        if err := rows.Scan(&config.Name, &config.Data, &config.Timestamp); err != nil {
            return nil, err
        }
        configs = append(configs, config)
    }

    if err := rows.Err(); err != nil {
        return nil, err
    }

    return configs, nil
}


func PrintConfigs(db *sql.DB) {
    record, err := db.Query("SELECT * FROM configs")
    if err != nil {
        log.Fatal(err)
    }
    defer record.Close()
    for record.Next() {
        var Name string
        var Data string
        var Timestamp string
        record.Scan(&Name, &Data, &Timestamp)
        log.Printf("Config: %s %s %s", Name, Data, Timestamp)
    }
}


