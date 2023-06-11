package db

import (
	"log"
    "errors"
	"database/sql"

	_ "github.com/mattn/go-sqlite3"
)

type Config struct {
    Name      string
    Data      string
    Timestamp string
}

type Arp struct {
    Mac       string
    Ip        string
    Data      string
    Timestamp string
}



func Version(db *sql.DB) (string, error) {
    
    var version string
    err := db.QueryRow("SELECT SQLITE_VERSION()").Scan(&version)
    if err != nil {
        return "", err
    }
    return version, nil
}


func CreateTables(db *sql.DB) error {

    configs_table := `CREATE TABLE configs (
        "Name" TEXT PRIMARY KEY NOT NULL,
        "Data" JSON,
        "Timestamp" TEXT);`
    query, err := db.Prepare(configs_table)
    if err != nil {
        return err
    }
    _, err = query.Exec()
    if err != nil {
        return err
    }

    arps_table := `CREATE TABLE arps (
        "Mac" TEXT PRIMARY KEY NOT NULL,
        "Ip" TEXT,
        "Data" TEXT,
        "Timestamp" TEXT);`
    query2, err := db.Prepare(arps_table)
    if err != nil {
        return err
    }
    _, err = query2.Exec()
    if err != nil {
        return err
    }

    return nil
}

func UpdateMac(db *sql.DB, Mac string, Ip string, Data string, Timestamp string) error {
    records := `INSERT OR REPLACE INTO arps (Mac, Ip, Data, Timestamp) VALUES (?, ?, ?, ?)`
    query, err := db.Prepare(records)
    if err != nil {
        return err
    }
    _, err = query.Exec(Mac, Ip, Data, Timestamp)
    if err != nil {
        return err
    }
    return nil
}


func AddMac(db *sql.DB, Mac string, Ip string, Data string, Timestamp string) error {
    records := `INSERT INTO arps (Mac, Ip, Data, Timestamp) VALUES (?, ?, ?, ?)`
    query, err := db.Prepare(records)
    if err != nil {
        return err
    }
    _, err = query.Exec(Mac, Ip, Data, Timestamp)
    if err != nil {
        return err
    }
    return nil
}

func AddConfig(db *sql.DB, Name string, Data string, Timestamp string) error {
    records := `INSERT INTO configs (Name, Data, Timestamp) VALUES (?, ?, ?)`
    query, err := db.Prepare(records)
    if err != nil {
        return err
    }
    _, err = query.Exec(Name, Data, Timestamp)
    if err != nil {
        return err
    }
    return nil
}


func DeleteConfig(db *sql.DB, Name string) error {

    query, err := db.Exec("DELETE FROM configs WHERE Name = ?", Name)
    if err != nil {
        return err
    }

    rowsAffected, err := query.RowsAffected()
    if err != nil {
        return err
    }

    if rowsAffected == 0 {
        return errors.New("delete failed")
    }

    return err
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

func FetchArps(db *sql.DB) ([]Arp, error) {
    rows, err := db.Query("SELECT * FROM arps")
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var arps []Arp
    for rows.Next() {
        var arp Arp
        if err := rows.Scan(&arp.Mac, &arp.Ip, &arp.Data, &arp.Timestamp); err != nil {
            return nil, err
        }
        arps = append(arps, arp)
    }

    if err := rows.Err(); err != nil {
        return nil, err
    }

    return arps, nil
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


