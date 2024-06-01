FROM golang:latest

WORKDIR /

COPY go.mod go.sum ./
RUN go mod download

COPY *.go ./

RUN CGO_ENABLED=0 GOOS=linux go build -o /metrics

EXPOSE 8080

CMD ["/metrics"]