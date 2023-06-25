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

var version = "2.0.0.dev-pre-0000-0000-000"

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
        case "list-job":
            listJob()
        case "add-job":
            addJob()
        case "del-job":
            delJob()

        case "run-jobs":
            runJobs()
        case "run-job":
            runJobName()
        case "list-outputs":
            listOutputs()
        case "list-output":
            listOutput()
        case "del-output":
            delOutput()

        case "run-sql":
            //runSql()
            fmt.Println("TODO runSql... ")

        case "list-tables":
            listTables()

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
  list-job name
  add-job name json
  del-job name

  run-jobs
  run-job name
  list-outputs
  list-output name
  del-output

  arps
  macs|list-macs
  del-mac mac

  manuf mac
  list-manuf

  nmap-scan [ip/net] [level]
  list-nmaps
  del-nmap ip

  list-tables

  sentry

`
    fmt.Println(usage)
}


type JobData struct {
	Job     string `json:"job,omitempty"`
	Name    string `json:"name,omitempty"`
	Config  string `json:"config,omitempty"`
	Time    string `json:"time,omitempty"`
	Repeat  string `json:"repeat,omitempty"`
	Start   string `json:"start,omitempty"`
	Done    string `json:"done,omitempty"`
	Output  string `json:"output,omitempty"`
	Message string `json:"message,omitempty"`
	Success string `json:"success,omitempty"`
	Error   string `json:"error,omitempty"`
	Exit    string `json:"exit,omitempty"`
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
        fmt.Printf("%s %s %s\n", job.Name, job.Data, job.Timestamp)

        var jobData JobData

        err := json.Unmarshal([]byte(job.Data), &jobData)
        if err != nil {
            fmt.Println("Error parsing job.Data:", err)
            continue
        }

        fmt.Println("Run JOB: ", job.Name, " Start ", jobData.Start, " Repeat ", jobData.Repeat, " Time ", jobData.Time, " Done ", jobData.Done)


        // Time || Repeat

        switch {

        case jobData.Time != "":

            fmt.Println("Time job...")

            if jobData.Start == "" {

                fmt.Println("Run Time job...")

                err := runJob(job.Name, jobData)
                if err != nil {
                    fmt.Println("Error running job.Data:", err)
                    continue
                }

            } else {

                fmt.Println("Time job Start exists")

            }

        case jobData.Repeat != "":

            fmt.Println("Repeat job...")

            if jobData.Start == "" {

                fmt.Println("Run Repeat job...")

                err := runJob(job.Name, jobData)
                if err != nil {
                    fmt.Println("Error running job.Data:", err)
                    continue
                }

            } else {

                fmt.Println("Repeat job Start exists, check if Done...")

                if jobData.Done != "" { // done not empty, so done

                    fmt.Println("OK to Repeat job Start Done is ", jobData.Done)


                }

            }

        default:
            fmt.Println("Skip job:", job.Name)
        }


    }
}

func runJobName() {

    if len(os.Args) < 3 {
        fmt.Println("Invalid arguments. Usage: run-job name [--force]")
        os.Exit(1)
    }

    fmt.Println("Job Name:", os.Args[2])

    // open db
    database, dberr := sql.Open("sqlite3", "sentinel.db")
    if dberr != nil {
        fmt.Println(dberr)
        os.Exit(1)
    }
    defer database.Close()

    // lookup/get job data
    job, joberr := db.FetchRecord(database, "jobs", os.Args[2])
    if joberr != nil {
        fmt.Println(joberr)
        os.Exit(1)
    }

    fmt.Println(job)

    var jobRecord db.Record
    for _, record := range job {
            //fmt.Println("Name:", record.Name)
            //fmt.Println("Data:", record.Data)
            //fmt.Println("Timestamp:", record.Timestamp)

            jobRecord = record
    }

    fmt.Println("Data.2:", jobRecord.Data)


    var jobData JobData

    umerr := json.Unmarshal([]byte(jobRecord.Data), &jobData)
    if umerr != nil {
        fmt.Println("Error parsing job.Data:", umerr)

    }

    if len(os.Args) > 3 && os.Args[3] == "--force" {

        err := runJob(os.Args[2], jobData)
        if err != nil {
            fmt.Println("Error running job.Data:", err)
        }

    } else {

        fmt.Println("Run jobData Run logic...")



        // Time || Repeat

        switch {

        case jobData.Time != "":

            fmt.Println("Time job...")

            if jobData.Start == "" {

                fmt.Println("Run Time job...")

                err := runJob(os.Args[2], jobData)
                if err != nil {
                    fmt.Println("Error running job.Data:", err)
                }

            } else {

                fmt.Println("Time job Start exists")

            }

        case jobData.Repeat != "":

            fmt.Println("Repeat job...")

            if jobData.Start == "" {

                fmt.Println("Run Repeat job...")

                err := runJob(os.Args[2], jobData)
                if err != nil {
                    fmt.Println("Error running job.Data:", err)
                }

            } else {

                fmt.Println("Repeat job Start exists, check if Done...")

                if jobData.Done != "" { // done not empty, so done

                    fmt.Println("OK to Repeat job Start Done is ", jobData.Done)


                }

            }

        default:
            fmt.Println("Skip job:", jobData.Name)
        } //end-switch-case

    }

}

func runJob(jobName string, jobData JobData) error {

    //now := time.Now()

    // read configs for Job
    fmt.Println("Read configs for Job... ")


    database, err := sql.Open("sqlite3", "sentinel.db")
    if err != nil {
        //fmt.Println(err)
        //os.Exit(1)
        return err
    }

    fmt.Println("Fetch Job config ", jobData.Config)
    config, err := db.FetchRecord(database, "configs", jobData.Config)
    if err != nil {
        //fmt.Println(err)
        //os.Exit(1)
        return err
    }

    //fmt.Println(now)
    //fmt.Println(config)
    //fmt.Println(config[0])
    //fmt.Println(config[1])
    //fmt.Println(config[2])


    var configRecord db.Record
    for _, record := range config {
            fmt.Println("Name:", record.Name)
            fmt.Println("Data:", record.Data)
            fmt.Println("Timestamp:", record.Timestamp)

            configRecord = record
    }

    fmt.Println("Data.2:", configRecord.Data)

    var configData struct {
        Cmd string `json:"cmd,omitempty"`
    }

    //err = json.Unmarshal([]byte(config.Data), &configData)
    err = json.Unmarshal([]byte(configRecord.Data), &configData)
    if err != nil {
        //fmt.Println("Error parsing config.Data:", err)
        return err
    }

    fmt.Println("Config cmd ", configData.Cmd)


            if configData.Cmd != "" {

                now := time.Now()

                fmt.Println("RUN THIS COMMAND: ", configData.Cmd)

                jobData.Start = now.Format("2006-01-02 15:04:05")
                updatedData, err := json.Marshal(jobData)
                if err != nil {
                    //fmt.Println("Error marshaling updated data:", err)
                    return err
                }

                fmt.Println("Lets Update Record...")
                err = db.UpdateRecord(database, "jobs", jobName, string(updatedData))
                if err != nil {
                    //fmt.Println("Error updating job:", err)
                    return err
                }

                fmt.Println("Run Command...")

                stdOut, stdErr, exitCode, err := tools.RunCommand(configData.Cmd)
                if err != nil {
                    //fmt.Println("Error tools.RunCommand:", err)
                    stdOut = fmt.Sprintf("Error: %v", err)
                }

                fmt.Println("We have output....")
                fmt.Println(stdOut, stdErr, exitCode)

                if exitCode == 1 {
                    stdOut = stdErr
                }

                jobData.Exit = fmt.Sprintf("%d", exitCode)

                updatedData, err = json.Marshal(jobData)
                if err != nil {
                    //fmt.Println("Error marshaling updated data:", err)
                    return err
                }

                if err = db.SaveOutput(database, jobName, stdOut, exitCode); err != nil {
                    //fmt.Println(err)
                    return err
                }

                fmt.Println("We are done....")

                done := time.Now()
                jobData.Done = done.Format("2006-01-02 15:04:05")
                updatedData2, err := json.Marshal(jobData)
                if err != nil {
                    //fmt.Println("Error marshaling updated data:", err)
                    return err
                }

                //fmt.Println("db.UpdateRecord.1 ", jobName)
                err = db.UpdateRecord(database, "jobs", jobName, string(updatedData2))
                if err != nil {
                    //fmt.Println("Error updating job:", err)
                    return err
                }

                fmt.Println("db.UpdateRecord.2 ", jobName)

            } //end-if configData.Cmd

    return nil
}




func runJob_v1(jobName string, jobData struct {
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
    Exit    string `json:"exit,omitempty"`
}) {

    now := time.Now()

    database, err := sql.Open("sqlite3", "sentinel.db")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }

    fmt.Println("Read configs for Job ") 
    configs, err := db.FetchRecordRows(database, "configs")
    if err != nil {
        fmt.Println(err)
    }

    for _, config := range configs {

        fmt.Printf("Config: %s %s %s\n", config.Name, config.Data, config.Timestamp)

        if jobData.Config == config.Name {
            fmt.Println("Job is Job ", config.Name, jobData.Config)

            var configData struct {
                Cmd string `json:"cmd,omitempty"`
            }

            err := json.Unmarshal([]byte(config.Data), &configData)
            if err != nil {
                fmt.Println("Error parsing config.Data:", err)
                return
            }

            fmt.Println("Config cmd ", configData.Cmd)

            if configData.Cmd != "" {
                fmt.Println("RUN THIS COMMAND: ", configData.Cmd)

                jobData.Start = now.Format("2006-01-02 15:04:05")
                updatedData, err := json.Marshal(jobData)
                if err != nil {
                    fmt.Println("Error marshaling updated data:", err)
                    return
                }

                fmt.Println("Lets Update Record...")
                err = db.UpdateRecord(database, "jobs", jobName, string(updatedData))
                if err != nil {
                    fmt.Println("Error updating job:", err)
                    return
                }

                fmt.Println("Run Command...")

                stdOut, stdErr, exitCode, err := tools.RunCommand(configData.Cmd)
                if err != nil {
                    fmt.Println("Error tools.RunCommand:", err)
                    stdOut = fmt.Sprintf("Error: %v", err)
                }

                fmt.Println("We have output....")
                fmt.Println(stdOut, stdErr, exitCode)

                if exitCode == 1 {
                    stdOut = stdErr
                }

                jobData.Exit = fmt.Sprintf("%d", exitCode)

                updatedData, err = json.Marshal(jobData)
                if err != nil {
                    fmt.Println("Error marshaling updated data:", err)
                    return
                }

                if err = db.SaveOutput(database, jobName, stdOut, exitCode); err != nil {
                    fmt.Println(err)
                    return
                }

                fmt.Println("We are done....")

                done := time.Now()
                jobData.Done = done.Format("2006-01-02 15:04:05")
                updatedData2, err := json.Marshal(jobData)
                if err != nil {
                    fmt.Println("Error marshaling updated data:", err)
                    return
                }

                fmt.Println("db.UpdateRecord.1 ", jobName)
                err = db.UpdateRecord(database, "jobs", jobName, string(updatedData2))
                if err != nil {
                    fmt.Println("Error updating job:", err)
                    return
                }

                fmt.Println("db.UpdateRecord.2 ", jobName)
            }
        } //end-if
    } //end-for
}






func runJobs_v1() {
    fmt.Println("runJobs")

    // read jobs
    database, err := sql.Open("sqlite3", "sentinel.db")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
    defer database.Close()

    //fmt.Println("db.FetchRecordRows 1")
    jobs, err := db.FetchRecordRows(database, "jobs")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
    //fmt.Println("db.FetchRecordRows 2")

    for _, job := range jobs {
        fmt.Printf("%s %s %s\n", job.Name, job.Data, job.Timestamp)

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
            Exit    string `json:"exit,omitempty"`
        }

        err := json.Unmarshal([]byte(job.Data), &jobData)
        if err != nil {
            fmt.Println("Error parsing job.Data:", err)
            continue // Skip to the next job if parsing fails
        }

        if jobData.Time != "" {
            fmt.Println("Yes, Time Present", jobData.Time)

            now := time.Now()
            jobTime, err := time.Parse("2006-01-02 15:04:05", jobData.Time)
            if err != nil {
                fmt.Println("Error parsing job time:", err)
                continue
            }

            if now.After(jobTime) {
                fmt.Println("Current time is After the job time.")

                if jobData.Start == "" {
                    fmt.Println("jobData.Start Job time.")

                    fmt.Println("Read configs for Job ")
                    configs, err := db.FetchRecordRows(database, "configs")
                    if err != nil {
                        fmt.Println(err)
                        continue
                    }

                    for _, config := range configs {
                        fmt.Printf("Config: %s %s %s\n", config.Name, config.Data, config.Timestamp)

                        if jobData.Config == config.Name {
                            fmt.Println("Job is Job ", config.Name, jobData.Config)

                            var configData struct {
                                Cmd string `json:"cmd,omitempty"`
                            }

                            err := json.Unmarshal([]byte(config.Data), &configData)
                            if err != nil {
                                fmt.Println("Error parsing config.Data:", err)
                                continue
                            }

                            fmt.Println("Config cmd ", configData.Cmd)

                            if configData.Cmd != "" {
                                fmt.Println("RUN THIS COMMAND: ", configData.Cmd)

                                jobData.Start = now.Format("2006-01-02 15:04:05")
                                updatedData, err := json.Marshal(jobData)
                                if err != nil {
                                    fmt.Println("Error marshaling updated data:", err)
                                    continue
                                }

                                fmt.Println("Lets Update Record...")
                                err = db.UpdateRecord(database, "jobs", job.Name, string(updatedData))
                                if err != nil {
                                    fmt.Println("Error updating job:", err)
                                    continue
                                }

                                fmt.Println("Run Command...")

                                //var exitCode = -1

                                //var outPut = ""

                                //outPut, exitCode, err := tools.RunCommand(configData.Cmd)
                                stdOut, stdErr, exitCode, err := tools.RunCommand(configData.Cmd)
                                if err != nil {
                                    fmt.Println("Error tools.RunCommand:", err)
                                    //continue

                                    stdOut = fmt.Sprintf("Error: %v", err)
                                    //exitCode = -1
                                    //exitCode = 1
                                    //outPut = stdOut
                                }

                                fmt.Println("We have output....")
                                fmt.Println(stdOut, stdErr, exitCode)

                                if exitCode == 1 {
                                    //exitCode = 1
                                    //outPut = stdErr
                                    stdOut = stdErr
                                }

                                // update json with exitCode
                                //jobData.Exit := exitCode
                                // Update the jobData.Exit field
                                jobData.Exit = fmt.Sprintf("%d", exitCode)

                                updatedData, err = json.Marshal(jobData)
                                if err != nil {
                                    fmt.Println("Error marshaling updated data:", err)
                                    continue
                                }

                                if err = db.SaveOutput(database, job.Name, stdOut, exitCode); err != nil {
                                    fmt.Println(err)
                                    continue
                                }

                                fmt.Println("We are done....")

                                done := time.Now()
                                jobData.Done = done.Format("2006-01-02 15:04:05")
                                updatedData2, err := json.Marshal(jobData)
                                if err != nil {
                                    fmt.Println("Error marshaling updated data:", err)
                                    continue
                                }

                                fmt.Println("db.UpdateRecord.1 ", job.Name)
                                err = db.UpdateRecord(database, "jobs", job.Name, string(updatedData2))
                                if err != nil {
                                    fmt.Println("Error updating job:", err)
                                    continue
                                }

                                fmt.Println("db.UpdateRecord.2 ", job.Name)
                            }

                        }

                    }

                }

                fmt.Println("NoRun: jobData.Start exists on ", job.Name)
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

    output, err := tools.RunCommand_v1("arp", "-an") // Pass any desired command arguments here
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
            if err = db.ReplaceMac(database, mac, ip, manufact); err != nil {
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

func delOutput() {

    if len(os.Args) != 3 {
        fmt.Println("Invalid arguments. Usage: del-output name")
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
    if err = db.DeleteRecord(database, "outputs", os.Args[2]); err != nil {
        fmt.Println(err)
        os.Exit(1)
    }

    fmt.Println("Output deleted successfully!")
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

func listJob() {

    if len(os.Args) != 3 {
        fmt.Println("Invalid arguments. Usage: list-job name")
        os.Exit(1)
    }
    //os.Args[2]


    database, err := sql.Open("sqlite3", "sentinel.db")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
    defer database.Close()

    jobs, err := db.FetchRecord(database, "jobs", os.Args[2])
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }

    for _, job := range jobs {
        fmt.Printf("%d %s %s %s\n", job.Id, job.Name, job.Data, job.Timestamp)
        //fmt.Printf("%s %s %s\n", job.Name, job.Data, job.Timestamp)
    }

}



func listOutputs() {

    database, err := sql.Open("sqlite3", "sentinel.db")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
    defer database.Close()

    records, err := db.FetchOutputs(database)
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }

    for _, record := range records {
        fmt.Println(record.Id, record.Name, record.Exit, record.Timestamp)
        fmt.Println(record.Data)
        //fmt.Printf("%d %s %s %d %s\n",record.Id, record.Name, record.Data, record.Exit, record.Timestamp)
        //fmt.Printf("%s %s %s\n", job.Name, job.Data, job.Timestamp)
    }

}

func listOutput() {

    if len(os.Args) != 3 {
        fmt.Println("Invalid arguments. Usage: list-output name")
        os.Exit(1)
    }
    //os.Args[2]


    database, err := sql.Open("sqlite3", "sentinel.db")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
    defer database.Close()

    records, err := db.FetchOutput(database, os.Args[2])
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }

    for _, record := range records {
        fmt.Printf("%d %s %s %s\n", record.Id, record.Name, record.Data, record.Timestamp)
        //fmt.Printf("%s %s %s\n", job.Name, job.Data, job.Timestamp)
    }

}


func listTables() {

    database, err := sql.Open("sqlite3", "sentinel.db")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
    defer database.Close()

    //tables, err := db.SQLStatement(database, "SELECT name FROM sqlite_schema WHERE type='table' ORDER BY name;")
    //tables, err := db.SQLStatement(database, "SELECT * FROM configs;")
    tables, err := db.SQLStatement(database, "SELECT name FROM sqlite_schema WHERE type='table' ORDER BY name;")
    if err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
    //defer tables.Close()

    // Iterate over the rows returned by the SQL statement
    for _, rows := range tables {
        for rows.Next() {
            var tableName string
            if err := rows.Scan(&tableName); err != nil {
                fmt.Println(err)
                continue
            }
            // Process each table name as needed
            fmt.Println(tableName)
        }
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


