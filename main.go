package main

import (
    "fmt"
    "strings"
    "os"
    "time"
    "sync"
    "os/signal"
    "syscall"
    "errors"
    "io/ioutil"
    "strconv"
    "encoding/json"
    "database/sql"

    _ "github.com/mattn/go-sqlite3"

    "sentinel/pkg/db"
    "sentinel/pkg/tools"
    "sentinel/pkg/manuf"

)

var version = "2.0.0.dev-🧨-1-July-10.1"

func main() {

    //DEBUG=1 go run main.go
    PrintDebug("Debug mode enabled")

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

        case "arps", "run-arps":
            //runArps()
            var wg sync.WaitGroup
            wg.Add(1)
            go runArps_v1(&wg) // Run runArps() as a goroutine
            wg.Wait() // Wait for runArps() to complete

        case "task", "run-task":
            runTask(os.Args[2])

        case "list-macs", "macs", "list-arps":
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
  list-job name
  add-job name json
  del-job name

  run-jobs
  run-job name [--force]
  list-outputs
  list-output name
  del-output

  # task: arps (arp + manuf)
  arps|run-arps|run-task arps|task arps
  macs|list-macs|list-arps
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
	//Name    string `json:"name,omitempty"`
	//Task    string `json:"task,omitempty"`
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


func PrintDebug(message string) {
	debugMode := os.Getenv("DEBUG")
	if debugMode != "" {
		fmt.Println(message)
	}
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

    PrintDebug("runJobs")

    // read jobs
    database, err := sql.Open("sqlite3", "sentinel.db")
    if err != nil {
        fmt.Println(err)
    }
    defer database.Close()

    jobs, err := db.FetchRecordRows(database, "jobs")
    if err != nil {
        fmt.Println(err)
    }

    for _, job := range jobs {

        PrintDebug(job.Name + " " + job.Data + " " + job.Timestamp)

        var jobData JobData

        err := json.Unmarshal([]byte(job.Data), &jobData)
        if err != nil {
            fmt.Println("Error parsing job.Data:", err)
        }

        PrintDebug("Run JOB: " + job.Name + " Start " + jobData.Start + " Repeat " + jobData.Repeat + " Time " + jobData.Time + " Done " + jobData.Done)


        // Time || Repeat

        switch {

        case jobData.Time != "":

            PrintDebug("Time job...")

            if jobData.Start == "" {

                PrintDebug("Run Time job...")

                err := runJob(job.Name, jobData)
                if err != nil {
                    fmt.Println("Error running job.Data:", err)
                }

            }


        case jobData.Repeat != "":

            PrintDebug("Repeat job...")

            if jobData.Start == "" {

                PrintDebug("Run Repeat job...")

                err := runJob(job.Name, jobData)
                if err != nil {
                    fmt.Println("Error running job.Data:", err)
                }

            } else {

                PrintDebug("Repeat job Start exists, check if Done...")

                if jobData.Done != "" { // done not empty, so done

                    PrintDebug("OK to Repeat job Start Done is "+ jobData.Done)

                    // get repeat time interval
                    PrintDebug("Repeat this time interval: "+ jobData.Repeat)

                    // Parse time strings into time.Time objects
                    jobDone, err := time.Parse("2006-01-02 15:04:05", jobData.Done)
                    if err != nil {
                        fmt.Println("Error parsing time:", err)
                    }


                    // Calculate time difference
                    //now := time.Now() //now: 2023-06-25 16:15:59.352279 -0700 PDT m=+0.001295211
                    now := time.Now().UTC()
                    elapsed := now.Sub(jobDone)

                    PrintDebug("jobDone:"+ jobDone.String())
                    PrintDebug("nowTime:"+ now.String())
                    PrintDebug("Elapsed:"+ elapsed.String())

                    // Parse Repeat value "1h", "5m", "30s", ...
                    PrintDebug("Repeat Value:"+ jobData.Repeat)

                    // Get the value and unit from the interval string
                    var value int64
                    var unit string

                    switch {
                    case strings.HasSuffix(jobData.Repeat, "hour"), strings.HasSuffix(jobData.Repeat, "hr"), strings.HasSuffix(jobData.Repeat, "h"):
                        value, unit = parseInterval(jobData.Repeat, "h", "hour")
                    case strings.HasSuffix(jobData.Repeat, "minute"), strings.HasSuffix(jobData.Repeat, "min"), strings.HasSuffix(jobData.Repeat, "m"):
                        value, unit = parseInterval(jobData.Repeat, "min", "minute")
                    case strings.HasSuffix(jobData.Repeat, "second"), strings.HasSuffix(jobData.Repeat, "sec"), strings.HasSuffix(jobData.Repeat, "s"):
                        value, unit = parseInterval(jobData.Repeat, "s", "second")
                    default:
                        fmt.Println("Unknown interval string:", unit)
                    } //end-switch-case jobData.Repeat

                    // Calculate the new time by adding the parsed duration
                    duration := calculateDuration(value, unit)

                    // Parse the start time as a time.Time value
                    //startTime, err := time.Parse(time.RFC3339, jobData.Start)
                    startTime, err := time.Parse("2006-01-02 15:04:05", jobData.Start)
                    if err != nil {
                        fmt.Printf("Error parsing start time: %v\n", err)
                    }

                    // Calculate the next repeat time by adding the duration to the start time

                    nextRepeatTime := startTime.Add(duration)
                    PrintDebug("Next Repeat Time: "+ nextRepeatTime.String())


                    // Compare nextRepeatTime with the current time
                    if nextRepeatTime.Before(now) || nextRepeatTime.Equal(now) {

                        //fmt.Println("Next repeat time has past or is equal to the current time.")
                        PrintDebug("run-jobs Run Repeat past due job...")

                        err := runJob(job.Name, jobData)
                        if err != nil {
                            fmt.Println("Error running job.Data:", err)
                        }

                    }




                }

            }

        default:
            PrintDebug("Skip job:"+ job.Name)
        }


    }
}

func runJobName() {

    if len(os.Args) < 3 {
        fmt.Println("Invalid arguments. Usage: run-job name [--force]")
        os.Exit(1)
    }

    PrintDebug("Job Name:"+ os.Args[2])

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

    //PrintDebug(job.String())

    var jobRecord db.Record
    for _, record := range job {
            PrintDebug("Name:"+ record.Name)
            PrintDebug("Data:"+ record.Data)
            PrintDebug("Timestamp:"+ record.Timestamp)

            jobRecord = record
    }

    PrintDebug("Data.2:"+ jobRecord.Data)


    var jobData JobData

    umerr := json.Unmarshal([]byte(jobRecord.Data), &jobData)
    if umerr != nil {
        fmt.Println("Error Unmarshal jobRecord.Data:", umerr)
        os.Exit(1)
    }

    if len(os.Args) > 3 && os.Args[3] == "--force" {

        err := runJob(os.Args[2], jobData)
        if err != nil {
            fmt.Println("Error running job.Data:", err)
        }

    } else {

        PrintDebug("Run jobData Run logic...")


        // Time || Repeat

        switch {

        case jobData.Time != "":

            PrintDebug("Time job...")

            if jobData.Start == "" {

                PrintDebug("Run Time job...")

                err := runJob(os.Args[2], jobData)
                if err != nil {
                    fmt.Println("Error running job.Data:", err)
                    os.Exit(1)
                }

            } else {

                fmt.Println("Finished Start:", jobData.Start, " Done:", jobData.Done)

            }


        case jobData.Repeat != "":

            PrintDebug("Repeat job...")

            if jobData.Start == "" {

                PrintDebug("Run Repeat job...")

                err := runJob(os.Args[2], jobData)
                if err != nil {
                    fmt.Println("Error running job.Data:", err)
                    os.Exit(1)
                }

            } else {

                PrintDebug("Repeat job Start exists, check if Done...")

                if jobData.Done != "" { // done not empty, so done

                    PrintDebug("OK to Repeat job Start is Done "+ jobData.Done)

                    // get repeat time interval
                    PrintDebug("Repeat this time interval: "+ jobData.Repeat)

                    // Parse time strings into time.Time objects
                    jobDone, err := time.Parse("2006-01-02 15:04:05", jobData.Done)
                    if err != nil {
                        fmt.Println("Error parsing time:", err)
                        os.Exit(1)
                    }


                    // Calculate time difference
                    //now := time.Now() //now: 2023-06-25 16:15:59.352279 -0700 PDT m=+0.001295211
                    now := time.Now().UTC()
                    elapsed := now.Sub(jobDone)

                    PrintDebug("jobDone:"+ jobDone.String())
                    PrintDebug("nowTime:"+ now.String())
                    PrintDebug("Elapsed:"+ elapsed.String())

                    // Parse Repeat value "1h", "5m", "30s", ...
                    PrintDebug("Repeat Value:"+ jobData.Repeat)

                    // Get the value and unit from the interval string
                    var value int64
                    var unit string

                    switch {
                    case strings.HasSuffix(jobData.Repeat, "hour"), strings.HasSuffix(jobData.Repeat, "hr"), strings.HasSuffix(jobData.Repeat, "h"):
                        value, unit = parseInterval(jobData.Repeat, "h", "hour")
                    case strings.HasSuffix(jobData.Repeat, "minute"), strings.HasSuffix(jobData.Repeat, "min"), strings.HasSuffix(jobData.Repeat, "m"):
                        value, unit = parseInterval(jobData.Repeat, "min", "minute")
                    case strings.HasSuffix(jobData.Repeat, "second"), strings.HasSuffix(jobData.Repeat, "sec"), strings.HasSuffix(jobData.Repeat, "s"):
                        value, unit = parseInterval(jobData.Repeat, "s", "second")
                    default:
                        fmt.Println("Unknown interval string:", unit)
                        os.Exit(1)
                    } //end-switch-case jobData.Repeat

                    // Calculate the new time by adding the parsed duration
                    duration := calculateDuration(value, unit)


                    // Parse the start time as a time.Time value
                    //startTime, err := time.Parse(time.RFC3339, jobData.Start)
                    startTime, err := time.Parse("2006-01-02 15:04:05", jobData.Start)
                    if err != nil {
                        fmt.Printf("Error parsing start time: %v\n", err)
                        os.Exit(1)
                    }

                    // Calculate the next repeat time by adding the duration to the start time

                    nextRepeatTime := startTime.Add(duration)
                    PrintDebug("Next Repeat Time: "+ nextRepeatTime.String())

                    // Calculate t-minus

                    // calculate how many seconds util nextRepeatTime
                    secondsUntilNextRepeat := int(nextRepeatTime.Sub(time.Now()).Seconds())
                    //fmt.Println("Seconds until next repeat time:", secondsUntilNextRepeat)
                    fmt.Println("Repeat t-minus:", secondsUntilNextRepeat)


                    // Compare nextRepeatTime with the current time
                    if nextRepeatTime.Before(now) || nextRepeatTime.Equal(now) {

                        //fmt.Println("Next repeat time has past or is equal to the current time.")
                        PrintDebug("Run Repeat past due job...")

                        err := runJob(os.Args[2], jobData)
                        if err != nil {
                            fmt.Println("Error running job.Data:", err)
                            os.Exit(1)
                        }

                    }

                } //end-if jobData.Done != ""

            } //end-if-else  jobData.Start == "" 

        default:
            PrintDebug("Skip job:"+ jobData.Job)

        } //end-switch-case Time || Repeat

    }

}


func parseInterval(intervalString, suffix, unit string) (int64, string) {

	//if len(intervalString) < len(suffix) || intervalString[len(intervalString)-len(suffix):] != suffix {

    if len(intervalString) < len(suffix) || !strings.HasSuffix(intervalString, suffix) {
		fmt.Printf("Invalid interval format: %s\n", intervalString)
		return 0, ""
	}

	valueStr := intervalString[:len(intervalString)-len(suffix)]
	value := parseValue(valueStr)
	return value, unit
}

func parseValue(valueStr string) int64 {
	var value int64
	_, err := fmt.Sscan(valueStr, &value)
	if err != nil {
		fmt.Printf("Error parsing value: %v\n", err)
	}
	return value
}

func calculateDuration(value int64, unit string) time.Duration {
	switch unit {
	case "hour":
		return time.Duration(value) * time.Hour
	case "minute":
		return time.Duration(value) * time.Minute
	case "second":
		return time.Duration(value) * time.Second
	default:
		return 0
	}
}



func runJob(jobName string, jobData JobData) error {

    // read configs for Job
    PrintDebug("Read configs for Job... ")


    database, err := sql.Open("sqlite3", "sentinel.db")
    if err != nil {
        return err
    }

    PrintDebug("Fetch Job config "+ jobData.Config)
    config, err := db.FetchRecord(database, "configs", jobData.Config)
    if err != nil {
        return err
    }

    var configRecord db.Record
    for _, record := range config {
            PrintDebug("Name:"+ record.Name)
            PrintDebug("Data:"+ record.Data)
            PrintDebug("Timestamp:"+ record.Timestamp)

            configRecord = record
    }

    PrintDebug("Data.2:"+ configRecord.Data)

    var configData struct {
        Cmd  string `json:"cmd,omitempty"`
        Task string `json:"task,omitempty"`
    }

    //err = json.Unmarshal([]byte(config.Data), &configData)
    err = json.Unmarshal([]byte(configRecord.Data), &configData)
    if err != nil {
        return err
    }

    PrintDebug("Config cmd "+ configData.Cmd)

    switch {
    case configData.Cmd != "" && configData.Task != "":
        // Both configData.Cmd and configData.Task are not empty
        // Execute code for this case
        //performAction(configData.Cmd, configData.Task)
        return errors.New("Both configData.Cmd and configData.Task are not empty")

    case configData.Cmd != "":
        // Only configData.Cmd is not empty
        // Execute code for this case
        //performCmdAction(configData.Cmd)
        /*
        rerr := runCmd(jobData, configData)
        if rerr != nil {
            fmt.Println("Error:", rerr)
        }
        */


                //configData.Cmd != ""

                //now := time.Now()
                now := time.Now().UTC()

                PrintDebug("RUN THIS COMMAND: "+ configData.Cmd)

                jobData.Start = now.Format("2006-01-02 15:04:05")
                updatedData, err := json.Marshal(jobData)
                if err != nil {
                    return err
                }

                PrintDebug("Lets Update Record...")
                err = db.UpdateRecord(database, "jobs", jobName, string(updatedData))
                if err != nil {
                    return err
                }

                PrintDebug("Run Command...")

                stdOut, stdErr, exitCode, err := tools.RunCommand(configData.Cmd)
                if err != nil {
                    stdOut = fmt.Sprintf("Error: %v", err)
                }

                PrintDebug("We have output....")
                PrintDebug(stdOut + " " + stdErr)

                //import "strconv"
                //PrintDebug(stdOut + " " + stdErr + " " + strconv.Itoa(exitCode))

                if exitCode == 1 {
                    stdOut = stdErr
                }

                jobData.Exit = fmt.Sprintf("%d", exitCode)

                updatedData, err = json.Marshal(jobData)
                if err != nil {
                    return err
                }

                if err = db.SaveOutput(database, jobName, stdOut, exitCode); err != nil {
                    return err
                }

                PrintDebug("We are done....")

                //done := time.Now()
                done := time.Now().UTC()
                jobData.Done = done.Format("2006-01-02 15:04:05")
                updatedData2, err := json.Marshal(jobData)
                if err != nil {
                    return err
                }

                err = db.UpdateRecord(database, "jobs", jobName, string(updatedData2))
                if err != nil {
                    return err
                }

                PrintDebug("db.UpdateRecord.2 "+ jobName)

                fmt.Println("Run "+ jobName + " Done")
                //end configData.Cmd

    case configData.Task != "":
        // Only configData.Task is not empty
        // Execute code for this case
        //performTaskAction(configData.Task)
        fmt.Println("Run Task!", configData.Task , " configData.Task")
        //err = runTask(configData.Task)
        //if err != nil {
        //    return err
        //}

                now := time.Now().UTC()

                PrintDebug("RUN THIS TASK: "+ configData.Task)

                jobData.Start = now.Format("2006-01-02 15:04:05")
                updatedData, err := json.Marshal(jobData)
                if err != nil {
                    return err
                }

                PrintDebug("db.1 Update Record...")
                err = db.UpdateRecord(database, "jobs", jobName, string(updatedData))
                if err != nil {
                    return err
                }

                PrintDebug("Run Task...")

                //stdOut, stdErr, exitCode, err := tools.RunCommand(configData.Cmd)
                //if err != nil {
                //    stdOut = fmt.Sprintf("Error: %v", err)
                //}

                //var taskErr string

                err = runTask(configData.Task)
                if err != nil {
                    //return err
                    //taskErr = fmt.Sprintf("%s", err)
                    jobData.Error = fmt.Sprintf("%s", err)
                    updatedData, err = json.Marshal(jobData)
                    if err != nil {
                        return err
                    }
                        
                }

                PrintDebug("We are done Task....")

                //import "strconv"
                //PrintDebug(stdOut + " " + stdErr + " " + strconv.Itoa(exitCode))

                /*
                jobData.Exit = fmt.Sprintf("%d", exitCode)
                updatedData, err = json.Marshal(jobData)
                if err != nil {
                    return err
                }
                */

                /*
                if err = db.SaveOutput(database, jobName, stdOut, exitCode); err != nil {
                    return err
                }
                */

                PrintDebug("Now update done....")

                //done := time.Now()
                done := time.Now().UTC()
                jobData.Done = done.Format("2006-01-02 15:04:05")
                updatedData2, err := json.Marshal(jobData)
                if err != nil {
                    return err
                }

                PrintDebug("db.2 UpdateRecord "+ jobName)
                err = db.UpdateRecord(database, "jobs", jobName, string(updatedData2))
                if err != nil {
                    return err
                }

                fmt.Println("Run "+ jobName + " Done")


    default:
        // Neither configData.Cmd nor configData.Task are not empty
        // Execute code for this case or handle the default scenario
        //handleDefault()
        return errors.New("Neither configData.Cmd nor configData.Task are not empty")
    }



    return nil
}


func runTask(task string) error {

    switch {
    case task == "arps":
        fmt.Println("ARPS")

        var wg sync.WaitGroup
        wg.Add(1)
        go runArps_v1(&wg) // Run runArps() as a goroutine
        wg.Wait() // Wait for runArps() to complete


    case task == "established":
        fmt.Println("ESTABLISHED")
    default:
        return nil
    }

    return nil
}

type PromData struct {
	Prometheus string `json:"prometheus,omitempty"`
	Port       int    `json:"port,omitempty"`
}

func getPrometheusConfig() PromData {
	database, err := sql.Open("sqlite3", "sentinel.db")
	if err != nil {
		return PromData{}
	}
	defer database.Close()

	configs, err := db.FetchRecordRows(database, "configs")
	if err != nil {
		return PromData{}
	}

	for _, config := range configs {

		var promData PromData

		err = json.Unmarshal([]byte(config.Data), &promData)
		if err != nil {
			return PromData{}
		}

		if promData.Prometheus != "" {
			//return configData.Prometheus, nil
			return promData
		}
	}

	//return PromData{}, fmt.Errorf("Prometheus not configured")
	return PromData{}
}


func getPromArps() string {

    database, err := sql.Open("sqlite3", "sentinel.db")
    if err != nil {
        //fmt.Println(err)
        return ""
    }
    defer database.Close()

    rows, err := db.FetchArpsRows(database)
    if err != nil {
        //fmt.Println(err)
        return ""
    }

    var result string

    for _, row := range rows {
        //fmt.Printf("%d %s %s %s %s\n", row.Id, row.Mac, row.Ip, row.Data, row.Timestamp)
        result += fmt.Sprintf(`sentinel_arp{mac="%s",ip="%s",manuf="%s"} 1` + "\n", row.Mac, row.Ip, row.Data)
    }

    return result
}


func writePromFile(filename string) error {
    PrintDebug("Write this prom file... " + filename)

    promStr := `sentinel_up{version="`+ version +`"} 1` + "\n"

    promArps := getPromArps()


    content := promStr + promArps

    //content := []byte(promStr)
    err := ioutil.WriteFile(filename, []byte(content), 0644)
    if err != nil {
         return fmt.Errorf("failed to write prom file: %v", err)
    }

    return nil
}


func runSentry() {

    // get promethues config

    prom := getPrometheusConfig()

    //fmt.Println(prom.Prometheus)
    //fmt.Println(prom.Port)

    var promFile string
    var promPort int

    if prom.Prometheus != "" || prom.Prometheus == "" {
        PrintDebug("Yes we have prom config")

        if prom.Prometheus == "" {
            promFile = "sentinel.prom"
        } else {
            promFile = prom.Prometheus
        }

        if prom.Port != 0 {
            promPort = prom.Port
        }

    }

    PrintDebug(promFile)
    PrintDebug(strconv.Itoa(promPort))


	// Create a channel to receive OS signals
	signals := make(chan os.Signal, 1)
	signal.Notify(signals, syscall.SIGINT, syscall.SIGTERM)

	// Create a channel to control the background process
	jobDone := make(chan struct{})

	// Start the background process
	go func() {
		for {
			select {
			case <-jobDone:
				return
			default:
				runJobs()
				//time.Sleep(500 * time.Millisecond)
				time.Sleep(time.Second) // Adjust the sleep duration as needed
			}
		}
	}()

	// Create a channel to control the background process
	promFileDone := make(chan struct{})

	// Start the background process
    go func() {
        for {
            select {
            case <-promFileDone:
                return
            default:
                err := writePromFile(promFile)
                if err != nil {
                    fmt.Println(err)
                }
                time.Sleep(15 * time.Second) // Adjust the sleep duration as needed
            }
        }
    }()


	// Wait for termination signal
	<-signals

	// Stop the background process
	close(jobDone)
	close(promFileDone)

    e := os.Remove(promFile)
    if e != nil {
	    fmt.Println(e)
    }

	fmt.Println("Program terminated")
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


func runArps_v1(wg *sync.WaitGroup) {

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


/*
func runCmd(jobData *JobData, configData *ConfigData) error {

                //configData.Cmd != ""

                //now := time.Now()
                now := time.Now().UTC()

                PrintDebug("RUN THIS COMMAND: "+ configData.Cmd)

                jobData.Start = now.Format("2006-01-02 15:04:05")
                updatedData, err := json.Marshal(jobData)
                if err != nil {
                    return err
                }

                PrintDebug("Lets Update Record...")
                err = db.UpdateRecord(database, "jobs", jobName, string(updatedData))
                if err != nil {
                    return err
                }

                PrintDebug("Run Command...")

                stdOut, stdErr, exitCode, err := tools.RunCommand(configData.Cmd)
                if err != nil {
                    stdOut = fmt.Sprintf("Error: %v", err)
                }

                PrintDebug("We have output....")
                PrintDebug(stdOut + " " + stdErr)

                //import "strconv"
                //PrintDebug(stdOut + " " + stdErr + " " + strconv.Itoa(exitCode))

                if exitCode == 1 {
                    stdOut = stdErr
                }

                jobData.Exit = fmt.Sprintf("%d", exitCode)

                updatedData, err = json.Marshal(jobData)
                if err != nil {
                    return err
                }

                if err = db.SaveOutput(database, jobName, stdOut, exitCode); err != nil {
                    return err
                }

                PrintDebug("We are done....")

                //done := time.Now()
                done := time.Now().UTC()
                jobData.Done = done.Format("2006-01-02 15:04:05")
                updatedData2, err := json.Marshal(jobData)
                if err != nil {
                    return err
                }

                err = db.UpdateRecord(database, "jobs", jobName, string(updatedData2))
                if err != nil {
                    return err
                }

                PrintDebug("db.UpdateRecord.2 "+ jobName)

                fmt.Println("Run "+ jobName + " Done")
                //end configData.Cmd


    return nil
}
*/


