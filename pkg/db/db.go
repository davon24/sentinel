package db

import (
    //"fmt"
    "log"
    "errors"
    "database/sql"

    _ "github.com/mattn/go-sqlite3"
)

type Record struct {
    Id        int
    Name      string
    Data      string
    Mac       string //arps
    Ip        string //arps 
    Exit      int    //outputs
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
        "Timestamp" DATETIME DEFAULT CURRENT_TIMESTAMP);`
    query1, err := db.Prepare(configs_table)
    if err != nil {
        return err
    }
    _, err = query1.Exec()
    if err != nil {
        return err
    }

    jobs_table := `CREATE TABLE jobs (
        "Name" TEXT PRIMARY KEY NOT NULL,
        "Data" JSON,
        "Timestamp" DATETIME DEFAULT CURRENT_TIMESTAMP);`
    query2, err := db.Prepare(jobs_table)
    if err != nil {
        return err
    }
    _, err = query2.Exec()
    if err != nil {
        return err
    }

    arps_table := `CREATE TABLE arps (
        "Mac"  TEXT PRIMARY KEY NOT NULL,
        "Ip"   TEXT,
        "Data" TEXT,
        "Timestamp" DATETIME DEFAULT CURRENT_TIMESTAMP);`
    query3, err := db.Prepare(arps_table)
    if err != nil {
        return err
    }
    _, err = query3.Exec()
    if err != nil {
        return err
    }

    outputs_table := `CREATE TABLE outputs (
        "Name" TEXT PRIMARY KEY NOT NULL,
        "Data" TEXT,
        "Exit" INT,
        "Timestamp" DATETIME DEFAULT CURRENT_TIMESTAMP);`
    query4, err := db.Prepare(outputs_table)
    if err != nil {
        return err
    }
    _, err = query4.Exec()
    if err != nil {
        return err
    }

    return nil
}

    // Update Mac Record with auto sqlite timestamp (no Timestamp)
func ReplaceMac(db *sql.DB, Mac string, Ip string, Data string) error {
    records := `INSERT OR REPLACE INTO arps (Mac, Ip, Data) VALUES (?, ?, ?)`
    query, err := db.Prepare(records)
    if err != nil {
        return err
    }
    _, err = query.Exec(Mac, Ip, Data)
    if err != nil {
        return err
    }
    return nil
}


func ReplaceMacRecord(db *sql.DB, Mac string, Ip string, Data string, Timestamp string) error {
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


    // Add Mac Record with auto sqlite timestamp (no Timestamp)
func AddMac(db *sql.DB, Mac string, Ip string, Data string) error {
    records := `INSERT INTO arps (Mac, Ip, Data) VALUES (?, ?, ?)`
    query, err := db.Prepare(records)
    if err != nil {
        return err
    }
    _, err = query.Exec(Mac, Ip, Data)
    if err != nil {
        return err
    }
    return nil
}

func AddMacRecord(db *sql.DB, Mac string, Ip string, Data string, Timestamp string) error {
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

    // Add Record with auto sqlite timestamp
func AddRecord(db *sql.DB, table string, Name string, Data string) error {
    records := `INSERT INTO ` + table + ` (Name, Data) VALUES (?, ?)`
    query, err := db.Prepare(records)
    if err != nil {
        return err
    }
    _, err = query.Exec(Name, Data)
    if err != nil {
        return err
    }
    return nil
}


func UpdateRecord(database *sql.DB, table string, Name string, Data string) error {
    // Prepare the SQL statement
    //statement, err := database.Prepare(fmt.Sprintf("UPDATE %s SET Data = ? WHERE Name = ?", table))
    statement, err := database.Prepare("UPDATE " + table + " SET Data = ? WHERE Name = ?")
    if err != nil {
        return err
    }
    defer statement.Close()

    // Execute the SQL statement
    _, err = statement.Exec(Data, Name)
    if err != nil {
        return err
    }

    return nil
}

func ReplaceRecord(database *sql.DB, table string, Name string, Data string) error {
    // Prepare the SQL statement
    statement, err := database.Prepare("INSERT OR REPLACE " + table + " SET Data = ? WHERE Name = ?")
    if err != nil {
        return err
    }
    defer statement.Close()

    // Execute the SQL statement
    _, err = statement.Exec(Data, Name)
    if err != nil {
        return err
    }

    return nil
}




func AddRecordRecord(db *sql.DB, table string, Name string, Data string, Timestamp string) error {
    records := `INSERT INTO ` + table + ` (Name, Data, Timestamp) VALUES (?, ?, ?)`
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

func DeleteRecord(db *sql.DB, table string, Name string) error {

    query, err := db.Exec("DELETE FROM " + table + " WHERE Name = ?", Name)
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

func FetchOutputs(db *sql.DB) ([]Record, error) {
    rows, err := db.Query("SELECT rowid,* FROM outputs")
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var records []Record
    for rows.Next() {
        var record Record
        if err := rows.Scan(&record.Id, &record.Name, &record.Data, &record.Exit, &record.Timestamp); err != nil {
            return nil, err
        }
        records = append(records, record)
    }

    if err := rows.Err(); err != nil {
        return nil, err
    }

    return records, nil
}

func FetchOutput(db *sql.DB, name string) ([]Record, error) {
    rows, err := db.Query("SELECT rowid,* FROM outputs WHERE Name = ?", name)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var records []Record
    for rows.Next() {
        var record Record
        if err := rows.Scan(&record.Id, &record.Name, &record.Data, &record.Exit, &record.Timestamp); err != nil {
            return nil, err
        }
        records = append(records, record)
    }

    if err := rows.Err(); err != nil {
        return nil, err
    }

    return records, nil
}




func FetchRecords(db *sql.DB, table string) ([]Record, error) {
    rows, err := db.Query("SELECT * FROM " + table)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var records []Record
    for rows.Next() {
        var record Record
        if err := rows.Scan(&record.Name, &record.Data, &record.Timestamp); err != nil {
            return nil, err
        }
        records = append(records, record)
    }

    if err := rows.Err(); err != nil {
        return nil, err
    }

    return records, nil
}


func FetchRecord(db *sql.DB, table string, name string) ([]Record, error) {
    rows, err := db.Query("SELECT * FROM " + table + " WHERE Name = ?", name)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var records []Record
    for rows.Next() {
        var record Record
        if err := rows.Scan(&record.Name, &record.Data, &record.Timestamp); err != nil {
            return nil, err
        }
        records = append(records, record)
    }

    if err := rows.Err(); err != nil {
        return nil, err
    }

    return records, nil
}



func FetchRecordRows(db *sql.DB, table string) ([]Record, error) {
    rows, err := db.Query("SELECT rowid,* FROM " + table)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var records []Record
    for rows.Next() {
        var record Record
        if err := rows.Scan(&record.Id, &record.Name, &record.Data, &record.Timestamp); err != nil {
            return nil, err
        }
        records = append(records, record)
    }

    if err := rows.Err(); err != nil {
        return nil, err
    }

    return records, nil
}


//func FetchArps(db *sql.DB) ([]Arp, error) {
func FetchArps(db *sql.DB) ([]Record, error) {
    rows, err := db.Query("SELECT * FROM arps")
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    //var arps []Arp
    var records []Record
    for rows.Next() {
        var record Record
        //if err := rows.Scan(&arp.Mac, &arp.Ip, &arp.Data, &arp.Timestamp); err != nil {
        if err := rows.Scan(&record.Mac, &record.Ip, &record.Data, &record.Timestamp); err != nil {
            return nil, err
        }
        records = append(records, record)
    }

    if err := rows.Err(); err != nil {
        return nil, err
    }

    return records, nil
}

func FetchArpsRows(db *sql.DB) ([]Record, error) {
    rows, err := db.Query("SELECT rowid,* FROM arps")
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var records []Record
    for rows.Next() {
        var record Record
        if err := rows.Scan(&record.Id, &record.Mac, &record.Ip, &record.Data, &record.Timestamp); err != nil {
            return nil, err
        }
        records = append(records, record)
    }

    if err := rows.Err(); err != nil {
        return nil, err
    }

    return records, nil
}



func PrintRecords(db *sql.DB, table string) {
    record, err := db.Query("SELECT * FROM " + table)
    if err != nil {
        log.Fatal(err)
    }
    defer record.Close()
    for record.Next() {
        var Name string
        var Data string
        var Timestamp string
        record.Scan(&Name, &Data, &Timestamp)
        log.Printf("Record: %s %s %s", Name, Data, Timestamp)
    }
}


func FetchTableRows(db *sql.DB, table string) ([]map[string]interface{}, error) {
    query := "SELECT rowid,* FROM " + table
    rows, err := db.Query(query)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    columns, err := rows.Columns()
    if err != nil {
        return nil, err
    }

    var result []map[string]interface{}
    values := make([]interface{}, len(columns))
    scanArgs := make([]interface{}, len(values))
    for i := range values {
        scanArgs[i] = &values[i]
    }

    for rows.Next() {
        err = rows.Scan(scanArgs...)
        if err != nil {
            return nil, err
        }

        row := make(map[string]interface{})
        for i, col := range values {
            if col != nil {
                row[columns[i]] = col
            }
        }
        result = append(result, row)
    }

    if err := rows.Err(); err != nil {
        return nil, err
    }

    return result, nil
}


func RunSQLStatement(db *sql.DB, query string, args ...interface{}) error {
    records := query
    preparedQuery, err := db.Prepare(records)
    if err != nil {
        return err
    }
    _, err = preparedQuery.Exec(args...)
    if err != nil {
        return err
    }
    return nil
}

// Usage:
// err := RunSQLStatement(db, "INSERT OR REPLACE INTO arps (Mac, Ip, Data, Timestamp) VALUES (?, ?, ?, ?)", Mac, Ip, Data, Timestamp)
// if err != nil {
// // handle error
// }

/*
func SQLStatement(db *sql.DB, query string, args ...interface{}) ([]*sql.Row, error) {
    rows, err := db.Query(query, args...)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var resultRows []*sql.Row
    for rows.Next() {
        var row *sql.Row
        if err := rows.Scan(); err != nil {
            return nil, err
        }

        resultRows = append(resultRows, row)

        //row = new(sql.Row)
        //resultRows = append(resultRows, row.Scan)
        //row := rows // Assign rows (type *sql.Rows) to row (type *sql.Row)
    }
    if err := rows.Err(); err != nil {
        return nil, err
    }
    return resultRows, nil
}
*/

/*
func SQLStatement(db *sql.DB, query string, args ...interface{}) ([]*sql.Row, error) {
    rows, err := db.Query(query, args...)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var resultRows []*sql.Row
    columns, _ := rows.Columns()
    scanArgs := make([]interface{}, len(columns))
    values := make([]sql.RawBytes, len(columns))

    for i := range values {
        scanArgs[i] = &values[i]
    }

    for rows.Next() {
        // Create a new instance of *sql.Row
        row := new(sql.Row)

        if err := rows.Scan(scanArgs...); err != nil {
            return nil, err
        }

        // Append the row to the resultRows slice
        resultRows = append(resultRows, row)
    }

    if err := rows.Err(); err != nil {
        return nil, err
    }

    return resultRows, nil
}
*/

/*
func SQLStatement(db *sql.DB, query string, args ...interface{}) ([]*sql.Row, error) {
    rows, err := db.QueryRow(query, args...)
    if err != nil {
        return nil, err
    }

    resultRows := []*sql.Row{rows} // Append the initial row to the slice

    return resultRows, nil
}
*/

/*
func SQLStatement(db *sql.DB, query string, args ...interface{}) (*sql.Row, error) {
    row := db.QueryRow(query, args...)

    return row, nil
}
*/

func SQLStatement(db *sql.DB, query string, args ...interface{}) ([]*sql.Rows, error) {
    rows, err := db.Query(query, args...)
    if err != nil {
        return nil, err
    }

    var resultRows []*sql.Rows
    resultRows = append(resultRows, rows)

    return resultRows, nil
}


func SaveOutput(db *sql.DB, Name string, Data string, Exit int) error {
    records := `INSERT OR REPLACE INTO outputs (Name, Data, Exit) VALUES (?, ?, ?)`
    query, err := db.Prepare(records)
    if err != nil {
        return err
    }
    _, err = query.Exec(Name, Data, Exit)
    if err != nil {
        return err
    }
    return nil
}










