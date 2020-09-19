package main

import (
	"bufio"
	"bytes"
	"compress/gzip"
	"crypto/rand"
	"crypto/tls"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net"
	"net/textproto"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/Pallinder/go-randomdata"
)

func timeTrack(start time.Time, name string) {
	elapsed := time.Since(start)
	log.Printf("%s took %s", name, elapsed)
}

func ATOS(asciiNum []int) string {
	res := ""
	for i := 0; i < len(asciiNum); i++ {
		character := string(asciiNum[i])
		res += (character)
	}
	return res
}

var reqFinalPart string
var reqFirstPart string

func main() { //make it faster

	firstRawData := `ig_sig_key_version=4&signed_body=503bf1bc1f6d6d176003451330b3ae08c43ac43548beae987cc46d15cea142c1.{"phone_id": "bed5b6c0-7526-4625-91ce-0ba5a34a8a27", "_csrftoken": "missing", "username": "`
	SecondRawData := `", "password": "what???!@", "device_id": "android-485bf80eec6f65c4", "guid": "801e56b0-68bd-4f71-b8d0-552f712fdb6a", "login_attempt_count": "0"}`
	RawDataSize := len([]byte(firstRawData)) + len([]byte(SecondRawData))

	headers := make(map[string]string)
	headers["Host"] = "i.instagram.com"
	headers["User-Agent"] = "Instagram 107.0.0.27.121 Android (19/4.4.2; 480dpi; 1152x1920; Meizu; MX4; mx4; mt6595; en_US)"
	headers["Accept"] = "*/*"
	headers["Cookie2"] = "$Version=1"
	headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
	headers["X-IG-Connection-Type"] = "WIFI"
	headers["Accept-Language"] = "en-US"
	headers["X-FB-HTTP-Engine"] = "Liger"
	//headers["Accept-Encoding"] = "gzip, deflate"
	headers["Connection"] = "Keep-Alive"

	_req := parseRequest("i.instagram.com", "/api/v1/accounts/login/", "post", headers, nil, "NULL?")

	reqParts := strings.Split(_req, "Content-Length: 5")
	//...[Content-Length: 5]\r\n\r\n
	reqFirstPart = reqParts[0] // == all without last \r\n\r\n
	reqFinalPart = reqParts[1] // == \r\n\r\n

	Conn, err := net.Dial(ATOS([]int{116, 99, 112, 52}), "i.instagram.com:443")
	if err != nil {
		panic(err)
	}
	cf := &tls.Config{Rand: rand.Reader, InsecureSkipVerify: true}
	ssl := tls.Client(Conn, cf)
	defer ssl.Close()

	var firstReq time.Time
	res := []time.Time{}
	loops := 100
	looped := 0
	var lastSince time.Duration
	var lastTime time.Time
	started := time.Now()

	var wg sync.WaitGroup
	wg.Add(1)

	go func() { //make it faster (+ strings, if, switch (contants) or remove, multithreading)
		//defer timeTrack(time.Now(), "Done All")
		defer timeTrack(firstReq, "Done All")
		defer wg.Done()

		tp := textproto.NewReader(bufio.NewReader(ssl))
		var totalData int
		var contentLength int
		var gzipped bool

		for {

			switch looped {
			case 100:
				lastTime = time.Now()
				timeTrack(started, "Done All")
				return
			}

			line, _ := tp.ReadLine()

			totalData += len(line)

			var tmp strings.Builder
			tmp.WriteString(line)
			tmp.WriteString("AAAAAAAAAAAAAAAA")
			_tmp := tmp.String()

			switch _tmp[:16] {
			case "Content-Encoding":
				gzipped = true
			}

			switch _tmp[:14] {
			case "Content-Length":
				contentLength, _ = strconv.Atoi(line[16:])
			}

			switch line {
			case "":

				var message string
				buffer := make([]byte, 4096)

				io.ReadAtLeast(tp.R, buffer, contentLength)
				buffer = buffer[:contentLength*2] //?? if it just gizp or what ?

				if gzipped {

					r, _ := gzip.NewReader(bytes.NewReader(buffer))

					result, _ := ioutil.ReadAll(r)
					message = string(result)

				} else {

					message = string(buffer)

				}

				println(message)

				switch looped {
				case 0:

					lastSince = time.Since(firstReq)
					lastTime = time.Now()
					res = append(res, lastTime)
					fmt.Printf("%s\n", lastSince)

				default:

					timeSinceLastResponse := time.Since(res[len(res)-1])
					lastSince = timeSinceLastResponse
					lastTime = time.Now()
					res = append(res, lastTime)
					fmt.Printf("%s\n", timeSinceLastResponse)

				}

				println()
				totalData = 0
				contentLength = 0
				looped++
			}

		}

	}()

	t := time.Now()
	//multithread
	firstReq = time.Now()
	//
	for i := 0; i < loops; i++ {
		//multithread
		go func() {
			var _RawRequest strings.Builder
			us := randomdata.RandStringRunes(15)
			contentLen := (RawDataSize + len(us))
			_RawRequest.WriteString(reqFirstPart)
			_RawRequest.WriteString("Content-Length: ")
			_RawRequest.WriteString(strconv.Itoa(contentLen))
			_RawRequest.WriteString(reqFinalPart)
			_RawRequest.WriteString(firstRawData)
			_RawRequest.WriteString(us)
			_RawRequest.WriteString(SecondRawData)
			println(_RawRequest.String())
			ssl.Write([]byte(_RawRequest.String()))
			_RawRequest.Reset()
		}()

	}
	timeToWriteAll := time.Since(t)
	fmt.Printf("time to write all the requests: %s\n", timeToWriteAll)
	wg.Wait()
	fmt.Printf("time to get all the response: %s\n", lastTime)

}

func parseRequest(host string, path string, method string, headers map[string]string, data map[string]string, rawData string) string {

	method = strings.ToUpper(method)
	rawRequest := fmt.Sprintf("%s %s HTTP/1.1\r\n", strings.ToUpper(method), path)

	if method == "GET" && (data != nil || rawData != ``) {
		var rawQuery string
		if rawData != "" {
			rawQuery = rawData
		} else {
			i := 0
			for key, value := range data {
				if i == len(data)-1 {
					rawQuery += fmt.Sprintf("%s=%s", key, value)
				} else {
					rawQuery += fmt.Sprintf("%s=%s&", key, value)
				}
				i++
			}
		}
		query := fmt.Sprintf("%s?%s", path, rawQuery)
		rawRequest = fmt.Sprintf("%s %s HTTP/1.1\r\n", strings.ToUpper(method), query)
	}

	var rawHeaders string
	for key, value := range headers {
		rawHeaders += fmt.Sprintf("%s: %s\r\n", key, value)
	}

	if !strings.Contains(strings.ToLower(rawHeaders), "host") {
		rawRequest += fmt.Sprintf("Host: %s\r\n", host)
	}

	_data := ""
	if method == "POST" && (data != nil || rawData != "") {

		if rawData != "" {
			_data = rawData
		} else {
			i := 0
			for key, value := range data {
				if i == len(data)-1 {
					_data += fmt.Sprintf("%s=%s", key, value)
				} else {
					_data += fmt.Sprintf("%s=%s&", key, value)
				}
				i++
			}
		}
		if !strings.Contains(strings.ToLower(rawHeaders), "content-length") {
			rawHeaders += fmt.Sprintf("Content-Length: %s\r\n", strconv.Itoa(len([]byte(_data))))
		}

	}
	rawRequest += fmt.Sprintf("%s\r\n", rawHeaders)
	//Content-Length: 5\r\n\r\n
	if _data != "" && _data != "NULL?" {
		rawRequest += _data
	}

	return rawRequest
}
