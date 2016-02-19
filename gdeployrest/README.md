##gdeploy API usage

> gdeploy REST API currently supports only JSON format.
> This is a beta version. There is no Authentication or Authorization
> mechanisms integrated.


gdeploy being a framework that accepts the configuration for whatever
infrastructure one means to deploy in a configuration file now has a
REST API that can accept these configuration in JSON format.

In this release of the API, the user can feed whichever configuration
she wants in a JSON format and get it running. These configuration can
be updated and re-run as per user requirements.

To have the API endpoint running, execute:

`python api.py <port> <host ip>`

###API

To add setup configurations:

* Method: POST
* Endpoint: /gdeploy/addconfig/{id}
* Content-Type: application/json
* JSON Request:  The configuration sections and options expected for any
  setup as per the configuration file are expected here as well. The
  only difference is this should be provided in JSON format.
Example:
```json
{
  'hosts': '10.70.46.13',
  'backend-setup': {
        'devices': 'vd{a,b}'
        }
}
```

To list already fed setup configurations:

* Method: GET
* Endpoint: /gdeploy/getconfig/{id}
* Content-Type: application/json
* JSON Request: Empty
* JSON Response: Will list the section


To run deployment using one particular configuration

* Method: POST
* Endpoint: /gdeploy/deployconfig/{id}
* Content-Type: application/json
* JSON Request: Empty
