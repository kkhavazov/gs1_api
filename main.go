package main

import (
	"bufio"
	"bytes"
	"fmt"
	"net/http"
	"os"
	"sync"
	"time"
)

const (
	ID_FILE      = "product_ids.txt"
	WORKER_COUNT = 25 // Number of concurrent connections
	API_URL      = "https://serviceplattform.gs1.de/api/master_data_service/v1/product"
	AUTH_TOKEN   = "YOUR_ACCESS_TOKEN"
)

func worker(id int, jobs <-chan string, wg *sync.WaitGroup, client *http.Client) {
	defer wg.Done()

	for productID := range jobs {
		// 1. Prepare the update payload (Example: changing status)
		// Check documentation for the exact JSON structure required
		jsonBody := []byte(`{"status": "ACTIVE"}`)

		url := API_URL + productID
		req, err := http.NewRequest("PATCH", url, bytes.NewBuffer(jsonBody))
		if err != nil {
			fmt.Printf("Worker %d: Error creating request for %s: %v\n", id, productID, err)
			continue
		}

		req.Header.Set("Authorization", "Bearer "+AUTH_TOKEN)
		req.Header.Set("Content-Type", "application/json")

		// 2. Execute Request
		resp, err := client.Do(req)
		if err != nil {
			fmt.Printf("Worker %d: Network error on %s: %v\n", id, productID, err)
			continue
		}

		// 3. Handle Rate Limiting
		if resp.StatusCode == 429 {
			fmt.Printf("Worker %d: Rate limited! Backing off...\n", id)
			time.Sleep(5 * time.Second)
		} else if resp.StatusCode != 200 && resp.StatusCode != 204 {
			fmt.Printf("Worker %d: Failed ID %s with status %d\n", id, productID, resp.StatusCode)
		}

		resp.Body.Close()

		// Optional: Add a small delay to stay under strict rate limits
		// time.Sleep(100 * time.Millisecond)
	}
}

func main() {
	// Open the ID file
	file, err := os.Open(ID_FILE)
	if err != nil {
		fmt.Printf("Error opening file: %v\n", err)
		return
	}
	defer file.Close()

	jobs := make(chan string, 100) // Buffer to keep workers busy
	var wg sync.WaitGroup

	// Create a custom client with a timeout
	client := &http.Client{
		Timeout: 30 * time.Second,
	}

	// Start the Worker Pool
	for w := 1; w <= WORKER_COUNT; w++ {
		wg.Add(1)
		go worker(w, jobs, &wg, client)
	}

	// Stream IDs from file into the jobs channel
	scanner := bufio.NewScanner(file)
	count := 0
	for scanner.Scan() {
		id := scanner.Text()
		if id != "" {
			jobs <- id
			count++
			if count%1000 == 0 {
				fmt.Printf("Queued %d IDs...\n", count)
			}
		}
	}

	close(jobs) // Signal workers that no more IDs are coming
	wg.Wait()   // Wait for all workers to finish remaining jobs

	if err := scanner.Err(); err != nil {
		fmt.Printf("Error reading file: %v\n", err)
	}

	fmt.Println("Finished processing all IDs.")
}
