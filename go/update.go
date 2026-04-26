package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"sync"
	"time"
)
type ProductUpdate struct {
	GtinStatus string `json:"gtinStatus"`
}

const (
	ID_FILE      = "testing.txt"
	WORKER_COUNT = 20
	BASE_URL     = "https://serviceplattform.gs1.de/api/master_data_service/v1/product"
	AUTH_TOKEN   =  os.Getenv("gs1_token") 

func worker(id int, jobs <-chan string, wg *sync.WaitGroup, client *http.Client) {
	defer wg.Done()

	for productID := range jobs {
		fullURL := fmt.Sprintf("%s/%s", BASE_URL, productID)

		productData, err := fetchProduct(client, fullURL)
		if err != nil {
			fmt.Printf("[Worker %d] Error fetching %s: %v\n", id, productID, err)
			continue
		}

		productData["gtinStatus"] = "ACTIVE"

		err = updateProduct(client, BASE_URL, productData)
		if err != nil {
			fmt.Printf("[Worker %d] Error updating %s: %v\n", id, productID, err)
			continue
		}

		fmt.Printf("[Worker %d] Success: %s\n", id, productID)
	}
}

func fetchProduct(client *http.Client, url string) (map[string]interface{}, error) {
	req, _ := http.NewRequest("GET", url, nil)
	req.Header.Set("Authorization", "Bearer "+AUTH_TOKEN)
	req.Header.Set("Accept", "application/json")

	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("GET failed with status: %d", resp.StatusCode)
	}

	var data map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&data); err != nil {
		return nil, err
	}
	return data, nil
}

func updateProduct(client *http.Client, url string, data map[string]interface{}) error {
	payload := []map[string]interface{}{data}

	jsonData, _ := json.Marshal(payload)
	req, _ := http.NewRequest("PUT", url, bytes.NewBuffer(jsonData))
	req.Header.Set("Authorization", "Bearer "+AUTH_TOKEN)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusNoContent {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("PUT failed: %d - %s", resp.StatusCode, string(body))
	}
	return nil
}

func main() {
	file, err := os.Open(ID_FILE)
	if err != nil {
		fmt.Printf("File error: %v\n", err)
		return
	}
	defer file.Close()

	jobs := make(chan string, 100)
	var wg sync.WaitGroup
	client := &http.Client{Timeout: 30 * time.Second}

	for w := 1; w <= WORKER_COUNT; w++ {
		wg.Add(1)
		go worker(w, jobs, &wg, client)
	}

	scanner := bufio.NewScanner(file)
	startTime := time.Now()
	count := 0

	for scanner.Scan() {
		line := scanner.Text()
		if line != "" {
			jobs <- line
			count++
		}
		if count%500 == 0 {
			fmt.Printf("Progress: %d IDs queued. Time: %v\n", count, time.Since(startTime).Round(time.Second))
		}
	}

	close(jobs)
	wg.Wait()
	fmt.Printf("Done! Processed %d entries in %v\n", count, time.Since(startTime))
}
