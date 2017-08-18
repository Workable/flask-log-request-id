
# Flask-Log-Request-Id

Many load balancers generate a unique id in the beginning of the request that should be forwarded to any backend 
application server in a multi-tier infrastructure. This pattern is also common in microservices infrastructure where 
the same correlation id should be attached to any forwared message so that the initial request can be efficiently
tracked. Adding this id to the log events of each backend service, provides a great tool for 
tracing and debugging problems.
 
**Flask-Log-Request-Id** is an extension for [Flask](http://flask.pocoo.org/) that is used to parse the forwarded
request-id and propagate this information to the rest of the backend infrastructure. A common usage is to inject 
the request_id in the logging system so that any log produced by third party libraries has attached the request_id
that initiated the call.


## Usage

Flask-Log-Request-Id provides the `current_request_id()` function which can be used at any time to get the request
id of the initiated execution chain.


### Example 1: Parse request id and print to stdout
```python
from flask_log_request_id import RequestID, current_request_id

[...]

RequestID(app)


@app.route('/')
def hello():
    print('Current trace id: {}'.format(current_request_id()))
```


### Example 2: Parse request id and send it to to logging

In the following example, we will use the `RequestIDLogFilter` to inject the request id on all log events, and
a custom formatter to print this information. If all these sounds unfamiliar please take a look at [python's logging 
system](https://docs.python.org/3/library/logging.html)


```python
import logging
import logging.config
from random import randint
from flask import Flask
from flask_log_request_id import RequestID, RequestIDLogFilter

def generic_add(a, b):
    """Simple function to add two numbers that is not aware of the trace id"""
    logging.debug('Called generic_add({}, {})'.format(a, b))
    return a + b

app = Flask(__name__)
RequestID(app)

# Setup logging
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - level=%(levelname)s - trace_id=%(trace_id)s - %(message)s"))
handler.addFilter(RequestIDLogFilter())  # << Add trace id contextual filter
logging.getLogger().addHandler(handler)


@app.route('/')
def index():
    a, b = randint(1, 15), randint(1, 15)
    logging.info('Adding two random numbers {} {}'.format(a, b))
    return str(generic_add(a, b))
```

The above will output the following log entries:

```
2017-07-25 16:15:25,912 - __main__ - level=INFO - trace_id=7ff2946c-efe0-4c51-b337-fcdcdfe8397b - Adding two random numbers 11 14
2017-07-25 16:15:25,913 - __main__ - level=DEBUG - trace_id=7ff2946c-efe0-4c51-b337-fcdcdfe8397b - Called generic_add(11, 14)
2017-07-25 16:15:25,913 - werkzeug - level=INFO - trace_id=None - 127.0.0.1 - - [25/Jul/2017 16:15:25] "GET / HTTP/1.1" 200 -
```

### Example 3: Forward request_id to celery tasks

Flask-Log-Request-Id comes with an extension to forward the context of current request_id to the execution of celery tasks



## Configuration

The following parameters can be configured through Flask's configuration system:

| Configuration Name | Description |
| ------------------ | ----------- |
| **LOG_REQUEST_ID_GENERATE_IF_NOT_FOUND**| In case the request does not hold any request id, the extension will generate one. Otherwise `current_request_id` will return None. |
| **LOG_REQUEST_ID_LOG_ALL_REQUESTS** | If True, it will emit a log event at the request containing all the details as `werkzeug` would done along with the `request_id` . |
| **LOG_REQUEST_ID_G_OBJECT_ATTRIBUTE** | This is the attribute of `Flask.g` object to store the current request id. Should be changed only if there is a problem. Use `current_request_id()` to fetch the current id. |
