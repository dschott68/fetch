# Fetch App
This Python application is an implementation of the requirements from 
[ETL off a SQS Queue](https://fetch-hiring.s3.amazonaws.com/data-engineer/pii-masking.pdf)

## Requirements
1. Download [Docker](https://docs.docker.com/get-docker/)

2. Get Docker image for Postgres
  ``` 
  docker pull fetchdocker/data-takehome-postgres
  ```

3. Get Docker image for LocalStack
  ```
  docker pull fetchdocker/data-takehome-localstack
  ```

## Building the application

1. Clone the repository.
  ```
  git clone https://github.com/dschott68/fetch.git
  cd fetch
  ```

2. Start Docker

3. Build the image
  ```
  docker build -t fetch-app .
  ```

## Run the application
After [requirement](https://github.com/dschott68/fetch?tab=readme-ov-file#requirements) and [building the application](https://github.com/dschott68/fetch?tab=readme-ov-file#building-the-application).  

1. Start Docker

2. In a terminal window, go to the directory where the repo was cloned. Start LocalStack and Postgres by running the command:
  ```
  docker-compose up
  ```

3. In a new terminal window, go to the directory where the repo was cloned. Start the application by running the command:
  ```
  docker run -p 4000:80 fetch-app
  ```

## Discussion
### How will you read messages from the queue?

FetchApp uses [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) 
API and resource instance for an object-oriented interface. The implementation 
following the [AWS Sample Tutorial](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/sqs.html#processing-messages).
The message body is converted from JSON to a Python dictionary and then 
yielded for processing. Finally, the message is deleted from the queue.

### What type of data structures should be used?

The message JSON is converted to a Python dictionary.  By using a generator 
function yielding a individual dictionary for each message, no extra collection 
data structure is need to store the messsages. This is more memory-efficient 
for large datasets.

### How will you mask the PII data so that duplicate values can be identified?

FetchApp use SHA-256 hash to mask the values. Duplicate values that are hashed
will result in the same hash value, thus they can be identified by looking for 
duplicate hash values.  SHA-256 hash is widely used and secure. If higher level
of security is a requirement, SHA-512 or even AES 256-bit could be used. 

### What will be your strategy for connecting and writing to Postgres?

FetchApp uses the popular `psycopg2` module for connecting and writing to
Postgres. The connection string is currently supplied by in the `config.ini`
file. For production, the user and password information should not be located
in the `config.ini` file. This information should be obtained using Security
team approved mechanism for access securing stored user and password data. 
For production, both a connection pool and retry logic should be implemented. 
Batch inserts would likely be more performant than individual inserts 
statements. 

### Where and how will your application run?

For the assignment, building a Docker image and running in Docker on the 
localhost makes the most sense as LocalStack and Postgres Docker images were 
supplied. The `Dockerfile` builds the image then `docker run` to run the 
application.

## Questions
### How would you deploy this application in production?

[Tutorial: Using a Lambda function to access an Amazon RDS database](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-lambda-tutorial.html) 
provides an excellect guide to a recommendation on where and how to run this 
application. Since the SQS Queue is already in AWS, it is wise to also run the 
application in AWS. [AWS Lamba](https://aws.amazon.com/lambda/) is a wise 
as it is serverless (saving team from managing infrastructure) and autoscaling.
If scale get too large, then Amazon EKS is a possible path. For how will the
application run, [Building Lambda functions with Python](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html) 
provides a guide. For the deployment, the companies standard CI/CD should be 
used. AWS CodeDeploy is one tool to handling deployment.

### What other components would you want to add to make this production ready?

- Security for keys, user name, password is a must.
- A database conneciton pool.
- Asynchronous I/O for SQS queue read and database write.
- Threading.
- Mocks and unit tests.
- Integration tests.
- Stats for observability.
- Logging improvement.  Remove PII data from logs.
- Exponential backoff retry logic for SQS Queue read, database connection and 
database writes.
- Batch database inserts rather than individual insert statements.
- Tranformation and validation rules for data prior to writing into database.
- Write failed messages out to a separate storage location for easy access for 
investigations.
- Review and implement best practices for `boto3`, SQS, `psycopg2`, Postgres, 
AWS.
- Security review of hashing and PII data.
- DBA review.
- Load testing.

### How can this application scale with a growing dataset

Threading and asynchronous I/O is important.  Since both the SQS queue wait/read 
and the database writes are I/O operations, this is a first area to look at
scale. Several Python modules can be looked at: `asyncio`, `aioboto3`, `aiodbc`. 
Use of a database connection pool is standard and should be implemented even 
before need for scale.

### How can PII be recovered later on?

The current implementation of a SHA-256 hash is not directly recoverable. If 
staying with hash, then orginal data could be stored in a access-controlled 
storage. An alternative to hash is encryption. The secret key can be used to 
recover the PII data via decryption by authorized personnel.

## What are the assumptions you made?

The application shuts down after the queue is empty. Production should wait for 
future messages.

The table INSERT will fail if the data already exists in Postgres. Requirements 
should define how to handle as an update, skip or failure.

The region field is sometimes empty. An appropriate default should be 
specified.

Length of the individual message fields is not check to be sure not longer
than the database column size. Length should be checked and should define
what to do with data that is too long: truncate, fail, etc.

app_version message field is dot-separated string. The table app_version is an
integer. No specification was given for how to handle this. With current
imnplementation 2.3.4 becomes 20304. Should decide if table column should stay 
as integer, change to string or define separate major, minor, patch fields. 
If changed to string, it is useful to make sure the string can be sorted in
lexicographical order to add in comparing older vs newer app versions.

