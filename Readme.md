### Installation:
`pip install .`
  
### Prerequisites:
you will need following certificates in your workdir:
 * for Kafka service:
   * `ca.pem`
   * `service.cert`
   * `service.key`
 * for Postgres service:
   * `ca_pg.pem`
   
database:
`create_tables.sql`

also you will have to export following environment variables:
 * `DB_URL={full database url with username, password, port, db name and ssl mode true}`
 * `SERVICE_URI={kafka host}:{kafka port}`

### Usage:
##### Run producer:
`$ fomars-kafka-producer`
##### Run consumer:
`$ fomars-kafka-consumer`
##### Stop:
Ctrl+C or SIGINT
