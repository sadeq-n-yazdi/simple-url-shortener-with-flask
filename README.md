# Simple Shortener

This is a very simple and unsecure URL shortener service.

**Note**: Do not use for production. Just created for fun and provided as is
without any guaranty in any way.

## To Do

- add NGNIX as web server
  - add multiple web server hosts
- Database
  - setup master-slave with one write node and multiple read node
- add docker-compose.yaml file
- move credential to configurations (and inject to service using environment variables)
- improve service functions
  - create custom short urls
  - add edit function for custom short urls
  - add validation
  - add black list for the URLs
  - add disable funtion for records
  - change code to OOP
    - add abstraction layers
    - add support other DB engines like Postgres, HBasae, Scylladb, CockroachDB, and so on
  - etc. sky is not limited
  