
# Flask-Log-Request-Id

Many load balancers in order to track the life-cycle of request, they generate a unique id in the beginning of the 
request that should be forwarded to any backend application server that processes this request. This pattern is also
common in microservices infrastructure where the same correlation id should be used by each micro-service that serves
the same initial request. Adding this id to the log events of each backend service, provides a great tool for 
tracing and debugging problems.
 
**Flask-Log-Request-Id** is an extension for [Flask](http://flask.pocoo.org/) that is used to parse the forwarded
request-id  and propagate this information to the rest of the backend infrastructure. A common usage is to inject 
the request_id in the logging system so that any log produced by third party libraries has attached the request_id
that initiated the call.


## Usage

Here is an example that catches the current trace id and on request it will print it on the standard output.

```python
from flask_log_request_id import RequestID, current_request_id

[...]

RequestID(app)


@app.route('/')
def hello():
    print('Current trace id: {}'.format(current_request_id()))
```


Another example is to catch the trace id and enrich existing logging mechanism with the request's trace id::

```python
def generic_add(a, b):
    """Simple function to add two numbers that is not aware of the trace id"""
    logger.debug('Called generic_add({}, {})'.format(a, b))
    return a + b

app = Flask(__name__)
RequestID(app)

# Setup logging
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - level=%(levelname)s - trace_id=%(trace_id)s - %(message)s"))
handler.addFilter(ContextualFilter())  # << Add trace id contextual filter
logging.getLogger().addHandler(handler)


@app.route('/')
def index():
    a, b = randint(1, 15), randint(1, 15)
    logger.info('Adding two random numbers {} {}'.format(a, b))
    return str(generic_add(a, b))
```

The above will output the following log entries:

```
2017-07-25 16:15:25,912 - __main__ - level=INFO - trace_id=7ff2946c-efe0-4c51-b337-fcdcdfe8397b - Adding two random numbers 11 14
2017-07-25 16:15:25,913 - __main__ - level=DEBUG - trace_id=7ff2946c-efe0-4c51-b337-fcdcdfe8397b - Called generic_add(11, 14)
2017-07-25 16:15:25,913 - werkzeug - level=INFO - trace_id=None - 127.0.0.1 - - [25/Jul/2017 16:15:25] "GET / HTTP/1.1" 200 -
```

## Configuration

Flask-Log-Request-ID follows Flask's configuration guidelines. The following parameters can be configured through 
Flask's configuration mechanism and will be obeyed by the extension

* **LOG_REQUEST_ID_EMIT_REQUEST_LOG**: If True it will emit an extra log event at the end of the request as `werkzeug` 
does while `request_id` is still accessible. 