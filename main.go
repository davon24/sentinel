package main

import (
    "fmt"
    "strings"
    "os"
    "time"
    "sync"
    "encoding/json"
    "database/sql"

    _ "github.com/mattn/go-sqlite3"

    "sentinel/pkg/db"
    "sentinel/pkg/tools"
    "sentinel/pkg/manuf"

)

var version = "2.0.0-dev-pre-0000"

func main() {

    err := createDb()
    if err != nil {
        panic(err)
    }

    if len(os.Args) > 1 {

        switch os.Args[1] {

        case "--help", "-help", "help":
            printUsage()
        case "--version", "-version", "version":
            fmt.Println("Version:", version)
            printSqlite3Version()

        case "list-configs", "configs":
            listConfigs()
        case "add-config":
            addConfig()
        case "del-config":
            delConfig()

        case "list-jobs", "jobs":
            listJobs()
        case "add-job":
            addJob()
        case "del-job":
            //delJob()
            fmt.Println("TODO Del Jobs... ")

        case "list-manuf":
            listManuf()
        case "manuf":
            runManuf()

        case "arps":
            //runArps()
            //fmt.Println("FIX runArps") // have () want (*sync.WaitGroup)

            var wg sync.WaitGroup
            wg.Add(1)
            go runArps(&wg) // Run runArps() as a goroutine
            wg.Wait() // Wait for runArps() to complete

        case "list-macs", "macs":
            listMacs()
        case "del-mac":
            //delMacs()
            fmt.Println("TODO Del macs... ")

        case "nmap-scan", "nmap":
            //nmapScan()
            fmt.Println("TODO Nmap Scan... ")
        case "list-nmaps":
            //listNmaps()
            fmt.Println("TODO List nmaps... ")
        case "del-nmap":
            //delNmap()
            fmt.Println("TODO Del namp... ")

        case "sentry":
            runSentry()

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

  configs|list-configs
  add-config name json
  del-config name

  jobs|list-jobs
  add-job name json
  del-job name

  arps
  macs|list-macs
  del-mac mac

  manuf mac
  list-manuf

  nmap-scan [ip/net] [level]
  list-nmaps
  del-nmap ip

  sentry

`
    fmt.Println(usage)
}


func printSqlite3Version() {

    database, err := sql.Open("sqlite3", "sentinel.db")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
    defer database.Close()

    version, err := db.Version(database)
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }

    fmt.Println("Sqlite3:", version)
}

func runSentry() {

    fmt.Println("runSentry")

    // read jobs

    database, err := sql.Open("sqlite3", "sentinel.db")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
    defer database.Close()

    jobs, err := db.FetchRecordRows(database, "jobs")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }

    for _, job := range jobs {
        //fmt.Printf("%d %s %s %s\n", job.Id, job.Name, job.Data, job.Timestamp)
        fmt.Printf("%s %s %s\n", job.Name, job.Data, job.Timestamp)

        // Parse job.Data JSON
        var jobData struct {
            Job     string `json:"job"`
            Repeat  string `json:"repeat"`
            Time    string `json:"time"`
            Start   string `json:"start"`
            Done    string `json:"done"`
            Success string `json:"success"`
            Message string `json:"message"`
        }

        err := json.Unmarshal([]byte(job.Data), &jobData)
        if err != nil {
            fmt.Println("Error parsing job.Data:", err)
            continue // Skip to the next job if parsing fails
        }

        // Access the "job" "repeat" value
        //fmt.Println("Job value:", jobData.Job)
        //fmt.Println("Repeat value:", jobData.Repeat)

        if jobData.Time != "" {
            fmt.Println("Yes, Time Present", jobData.Time)
            // evalute time to run

            now := time.Now()
            //timestamp := now.Format("2006-01-02T15:04:05")

            // Parse jobData.Time into a time.Time object
            //jobTime, err := time.Parse("2006-01-02T15:04:05", jobData.Time)

            jobTime, err := time.Parse("2006-01-02 15:04:05", jobData.Time)
            if err != nil {
                fmt.Println("Error parsing job time:", err)
                return
            }

            /*
             // Convert jobTime to the local time zone
             loc, err := time.LoadLocation("Local")
             if err != nil {
                 fmt.Println("Error loading local time zone:", err)
                 return
             }
             jobTime = jobTime.In(loc)
            */

            //fmt.Println("Current Time:", now)
            //fmt.Println("Job Time:", jobTime)

            // Compare the times
            if now.After(jobTime) {
                fmt.Println("Current time is After the job time.")
                // Run job now

                //go runArps() // Run runArps() as a goroutine

                var wg sync.WaitGroup
                wg.Add(1)
                go runArps(&wg) // Run runArps() as a goroutine
                wg.Wait() // Wait for runArps() to complete


            } else if now.Before(jobTime) {
                fmt.Println("Current time is Before the job time.")
            } else {
                fmt.Println("Current time is the Same as the job time.")
            }


        }


    }

}

func listManuf() {

    fmt.Println("List Manuf...")

    manuf, err := manuf.EmbedFS.ReadFile("resources/manuf")
    if err != nil {
        panic(err)
    }

    fmt.Println(string(manuf))

}

func runManuf() {

    if len(os.Args) != 3 {
        fmt.Println("Invalid arguments. Usage: manuf mac")
        os.Exit(1)
    }

    mac := os.Args[2]
    mac = strings.ToUpper(mac) // Convert mac address to UPPERCASE for matching

    parts := strings.Split(mac, ":")

    content, err := manuf.EmbedFS.ReadFile("resources/manuf")
    if err != nil {
        panic(err)
    }

    var manufact string = "NoManufacturer"
    for i := len(parts); i > 0; i-- {
        
        subMac := strings.Join(parts[:i], ":")
        //fmt.Fprintln(os.Stdout, subMac)
        manufacturer := manuf.SearchManufacturer(subMac, string(content))

        if manufacturer != "Manufacturer Not Found" {
            //fmt.Printf("Manufacturer for MAC address %s is %s\n", mac, manufacturer)
            manufact = manufacturer
            break
        }

    }

    fmt.Println(manufact)

}


func runArps(wg *sync.WaitGroup) {

    defer wg.Done()

    fmt.Println("runArps!")

    output, err := tools.RunCommand("arp", "-an") // Pass any desired command arguments here
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }

    // Manuf content
    content, err := manuf.EmbedFS.ReadFile("resources/manuf")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }

    //Save output to db
    //Open database connect
    database, err := sql.Open("sqlite3", "sentinel.db")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
    defer database.Close()


    lines := strings.Split(output, "\n")
    for _, line := range lines {
        //fmt.Println(line)

        fields := strings.Fields(line)
        if len(fields) >= 4 {
            ip := strings.Trim(fields[1], "()")
            mac := fields[3]

            // Manuf lookup
            mac = strings.ToUpper(mac) // Convert mac address to UPPERCASE for matching
            parts := strings.Split(mac, ":")
            var manufact string  = "NoManuf"
            for i := len(parts); i > 0; i-- {
                subMac := strings.Join(parts[:i], ":")
                manufacturer := manuf.SearchManufacturer(subMac, string(content))
                if manufacturer != "Manufacturer Not Found" {
                    manufact = manufacturer
                    break
                }
            }

            // Timestamp
            //now := time.Now()
            //timestamp := now.Format("2006-01-02T15:04:05")

	    //timestamp := time.Time{} // set timestamp to null value
	    //timestamp := "" // initialize as empty string for null value

            //save record data 
            //if err = db.UpdateMacRecord(database, mac, ip, manufact, timestamp); err != nil {
            if err = db.UpdateMac(database, mac, ip, manufact); err != nil {
                fmt.Println(err)
                return
            }

            fmt.Printf("%s %s %s\n", ip, mac, manufact)

        }

    }

}


func addJob() {

    if len(os.Args) != 4 {
        fmt.Println("Invalid arguments. Usage: add-job name json")
        os.Exit(1)
    }

    // Timestamp
    //now := time.Now()
    //timestamp := now.Format("2006-01-02T15:04:05")

    // Validate data as JSON
    isJSON := json.Valid([]byte(os.Args[3]))
    if !isJSON {
        fmt.Println("Invalid JSON!")
        os.Exit(1)
    }

    //open database connect
    database, err := sql.Open("sqlite3", "sentinel.db")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
    defer database.Close()

    //add job data
    //if err = db.AddRecord(database, "jobs", os.Args[2], os.Args[3], timestamp); err != nil {
    if err = db.AddRecord(database, "jobs", os.Args[2], os.Args[3]); err != nil {
        fmt.Println(err)
        os.Exit(1)
    }

    fmt.Println("Job added successfully!")
}


func addConfig() {

    if len(os.Args) != 4 {
        fmt.Println("Invalid arguments. Usage: add-config name json")
        os.Exit(1)
    }

    // Timestamp
    //now := time.Now()
    //timestamp := now.Format("2006-01-02T15:04:05")

    // Validate data as JSON
    isJSON := json.Valid([]byte(os.Args[3]))
    if !isJSON {
        fmt.Println("Invalid JSON!")
        os.Exit(1)
    }

    //open database connect
    database, err := sql.Open("sqlite3", "sentinel.db")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
    defer database.Close()

    //add config data
    //if err = db.AddRecord(database, "configs", os.Args[2], os.Args[3], timestamp); err != nil {
    if err = db.AddRecord(database, "configs", os.Args[2], os.Args[3]); err != nil {
	    fmt.Println(err)
	    os.Exit(1)
    }

    fmt.Println("Config added successfully!")
}


func delConfig() {

    if len(os.Args) != 3 {
        fmt.Println("Invalid arguments. Usage: del-config name")
        os.Exit(1)
    }

    //open database connect
    database, err := sql.Open("sqlite3", "sentinel.db")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
    defer database.Close()

    //delete config data
    if err = db.DeleteRecord(database, "configs", os.Args[2]); err != nil {
        fmt.Println(err)
        os.Exit(1)
    }

    fmt.Println("Config deleted successfully!")
}

func listMacs() {

    database, err := sql.Open("sqlite3", "sentinel.db")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
    defer database.Close()

    rows, err := db.FetchArpsRows(database)
    //rows, err := db.FetchTableRows(database, "arps")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }

    for _, row := range rows {
    //for _, arp := range arps {
        //fmt.Printf("%d %s %s %s %s\n", arp.Id, arp.Mac, arp.Ip, arp.Data, arp.Timestamp)
        fmt.Printf("%d %s %s %s %s\n", row.Id, row.Mac, row.Ip, row.Data, row.Timestamp)

        //fmt.Printf("%v %v %v %v \n", row["Mac"], row["Ip"], row["Data"], row["Timestamp"])

        /*
		fmt.Print("row data: ")
		for _, value := range row {
			fmt.Printf("%v ", value)
		}
		fmt.Println()
        */

        /*
        for column, value := range row {
            fmt.Printf("%s: %v\n", column, value)
        }
        */

        /*
        for i, value := range row {
            if i > 0 {
                fmt.Print(" ")
            }
            fmt.Print(value)
        }
        */
       
       /*
        isFirstValue := true
        for _, value := range row {
            if !isFirstValue {
                fmt.Print(" ")
            }
            fmt.Print(value)
            isFirstValue = false
        }
        fmt.Println()
        */


    }

}


func listConfigs() {

    database, err := sql.Open("sqlite3", "sentinel.db")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
    defer database.Close()

    //configs, err := db.FetchRecords(database, "configs")
    configs, err := db.FetchRecordRows(database, "configs")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }

    for _, config := range configs {
        //fmt.Printf("%d %s %s %s\n", config.Id, config.Name, config.Data, config.Timestamp)
        fmt.Printf("%s %s %s\n", config.Name, config.Data, config.Timestamp)
    }
}


func listJobs() {

    database, err := sql.Open("sqlite3", "sentinel.db")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
    defer database.Close()

    jobs, err := db.FetchRecordRows(database, "jobs")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }

    for _, job := range jobs {
        //fmt.Printf("%d %s %s %s\n", job.Id, job.Name, job.Data, job.Timestamp)
        fmt.Printf("%s %s %s\n", job.Name, job.Data, job.Timestamp)
    }

}



func createDb() error {

    if _, err := os.Stat("sentinel.db"); os.IsNotExist(err) {
        //return fmt.Errorf("File does not exist")
        file, err := os.Create("sentinel.db")
        if err != nil {
            return err
        }
        file.Close()

        database, err := sql.Open("sqlite3", "sentinel.db")
        if err != nil {
            return err
        }
        defer database.Close()

        db.CreateTables(database)

        fmt.Printf("Created sentinel.db \n")
    }
    //fmt.Printf("File exists\n")
    return nil
}


