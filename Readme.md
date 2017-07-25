
# Flask-TraceID

Flask-TraceID can track or provide unique ids for requests. The ids can be injected to the logging
module in order to tag application log events with the id of the request that where produced. Out of the box
it comes with an extractor for [Amazon Trace-ID](http://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-request-tracing.html).


## Usage

Here is an example that catches the current trace id and on request it will print it on the standard output.

```python
from flask_traceid import TraceID, current_trace_id

[...]

TraceID(app)


@app.route('/')
def hello():
print('Current trace id: {}'.format(current_trace_id()))
```


Another example is to catch the trace id and enrich existing logging mechanism with the request's trace id::

```python
def generic_add(a, b):
    """Simple function to add two numbers that is not aware of the trace id"""
    logger.debug('Called generic_add({}, {})'.format(a, b))
    return a + b

app = Flask(__name__)
TraceID(app)

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

Flask-TraceID conforms to Flask's configuration guidelines. The following parameters can be configured through Flask's configuration mechanism and will be obeyed by TraceID

* **TRACEID_EMIT_REQUEST_LOG**: If True it will emit an extra log event at the end of the request as `werkzeug` does while trace_id is still accessible. 