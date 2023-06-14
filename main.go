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

var version = "2.0.0-dev-pre-0000-0"

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
            delJob()
        case "run-jobs":
            runJobs()

        case "list-manuf":
            listManuf()
        case "manuf":
            runManuf()

        case "arps":
            //runArps()
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
            //runSentry()
            fmt.Println("TODO runSentry... ")

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

  run-jobs

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

func runJobs() {

    fmt.Println("runJobs")

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

        // Parse job.Data JSON omitempty
        var jobData struct {
            Job     string `json:"job,omitempty"`
            Config  string `json:"config,omitempty"`
            Time    string `json:"time,omitempty"`
            Repeat  string `json:"repeat,omitempty"`
            Start   string `json:"start,omitempty"`
            Done    string `json:"done,omitempty"`
            Output  string `json:"output,omitempty"`
            Message string `json:"message,omitempty"`
            Success string `json:"success,omitempty"`
            Error   string `json:"error,omitempty"`
        }

        // Parse config.Data JSON omitempty
        var configData struct {
            Cmd     string `json:"cmd,omitempty"`
        }


        type Config struct {
            Name      string
            Data      string
            Timestamp string
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
            jobTime, err := time.Parse("2006-01-02 15:04:05", jobData.Time)
            if err != nil {
                fmt.Println("Error parsing job time:", err)
                return
            }

            //fmt.Println("Current Time:", now)
            //fmt.Println("Job Time:", jobTime)

            // Compare the times
            if now.After(jobTime) {
                fmt.Println("Current time is After the job time.")
                // Run job now

                // if empty Start
                if jobData.Start == "" {

                    fmt.Println("jobData.Start Job time.")


                    fmt.Println("Read configs for Job ")
                    // read job config
                    configs, err := db.FetchRecordRows(database, "configs")
                    if err != nil {
                        fmt.Println(err)
                        return
                    }

                    var config Config // Declare the config variable outside the loop
                    for _, conf := range configs {

                        config = Config{
                            Name:      conf.Name,
                            Data:      conf.Data,
                            Timestamp: conf.Timestamp,
                        }

                        fmt.Printf("Config: %s %s %s\n", config.Name, config.Data, config.Timestamp)
                    }

                    fmt.Println("This is config.Name ", config.Name)
                    fmt.Println("This is config.Data ", config.Data)

                    // print job job-2 {"time": "2099-12-31 00:00:00", "config": "config-1"}
                    // print config config-1 {"cmd": "arp -an"}

                    fmt.Println("job jobData.Config ", jobData.Config) //config-1

                    fmt.Println("config config.Name ", config.Name) //config-1

                    fmt.Println("Done Read configs Job ")

                    // Config exists for job
                    if jobData.Config == config.Name {

                        fmt.Println("Job is Job ", config.Name, jobData.Config)

                        // Read config json config.Data
                        err := json.Unmarshal([]byte(config.Data), &configData)
                        if err != nil {
                            fmt.Println("Error parsing config.Data:", err)
                            continue // Skip to the next if parsing fails
                        }

                        // Access the "cmd"
                        fmt.Println("Config cmd ", configData.Cmd)

                        // if cmd
                        if configData.Cmd != "" {

                            // command to run
                            fmt.Println("RUN THIS COMMAND: ", configData.Cmd)

                            // update jobData.start jobTime
                            //jobData.Start = jobTime.Format("2006-01-02 15:04:05")
                            jobData.Start = now.Format("2006-01-02 15:04:05")

                            // Marshal the updated jobData back to JSON
                            updatedData, err := json.Marshal(jobData)
                            if err != nil {
                                fmt.Println("Error marshaling updated data:", err)
                                continue // Skip to the next job if marshaling fails
                            }

                            // Update the job.Data in the database with the updated JSON
                            err = db.UpdateRecord(database, "jobs", job.Name, string(updatedData))
                            if err != nil {
                                fmt.Println("Error updating job:", err)
                                continue // Skip to the next job if updating fails
                            }


                            /*
                            //go runArps() as a goroutine
                            var wg sync.WaitGroup
                            wg.Add(1)
                            go runArps(&wg) // Run runArps() as a goroutine
                            wg.Wait() // Wait for runArps() to complete
                            */

                            // Run Command...
                            //output, err := runCmd("arp -an")
                            //output, err := tools.RunCommand("arp", "-an")

                            //output, err := runCmd("arp -an")
                            output, err := tools.RunCmd(configData.Cmd)
                            if err != nil {
                                fmt.Println("Error tools.RunCmd:", err)
                            }


                            fmt.Println(output)

                            // Save output...  WORK

                            // job done
                            done := time.Now()
                            jobData.Done = done.Format("2006-01-02 15:04:05")

                            // Marshal the updated jobData back to JSON
                            updatedData2, err := json.Marshal(jobData)
                            if err != nil {
                                fmt.Println("Error marshaling updated data:", err)
                                continue // Skip to the next job if marshaling fails
                            }

                            // Update the job.Data in the database with the updated JSON
                            err = db.UpdateRecord(database, "jobs", job.Name, string(updatedData2))
                            if err != nil {
                                fmt.Println("Error updating job:", err)
                                continue // Skip to the next job if updating fails
                            }

                        } // end-if configData.Cmd

                    } // end-if job is job match

                } // end-if jobData.Start

                fmt.Println("NoRun: jobData.Start exist on ", job.Name)
                //done.done


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

func delJob() {

    if len(os.Args) != 3 {
        fmt.Println("Invalid arguments. Usage: del-job name")
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
    if err = db.DeleteRecord(database, "jobs", os.Args[2]); err != nil {
        fmt.Println(err)
        os.Exit(1)
    }

    fmt.Println("Job deleted successfully!")
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
        fmt.Printf("%d %s %s %s %s\n", row.Id, row.Mac, row.Ip, row.Data, row.Timestamp)
        //fmt.Printf(" %v %v %v %v \n", row["Id"], row["Mac"], row["Ip"], row["Data"], row["Timestamp"])

    }

}


func listConfigs() {

    database, err := sql.Open("sqlite3", "sentinel.db")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
    defer database.Close()

    configs, err := db.FetchRecordRows(database, "configs")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }

    for _, config := range configs {
        fmt.Printf("%d %s %s %s\n", config.Id, config.Name, config.Data, config.Timestamp)
        //fmt.Printf("%s %s %s\n", config.Name, config.Data, config.Timestamp)
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
        fmt.Printf("%d %s %s %s\n", job.Id, job.Name, job.Data, job.Timestamp)
        //fmt.Printf("%s %s %s\n", job.Name, job.Data, job.Timestamp)
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


