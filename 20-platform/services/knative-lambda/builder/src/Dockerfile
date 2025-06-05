FROM golang:1.24 as builder

WORKDIR /app

COPY go.mod .
COPY *.go .
COPY templates/ templates/

RUN go mod download
RUN go mod tidy
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o lambda-builder .

FROM alpine:3.18

RUN apk --no-cache add ca-certificates

WORKDIR /app

COPY --from=builder /app/lambda-builder .
COPY --from=builder /app/templates/ templates/

CMD ["./lambda-builder"] 