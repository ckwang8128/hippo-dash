import os
import logging
from flask import Flask, render_template, Response, send_from_directory, request, current_app

flask_app = Flask(__name__)
logging.basicConfig()
log = logging.getLogger(__name__)


@flask_app.route("/")
def main():
    return render_template('main.html', title='Inventory')

@flask_app.route("/small")
def small():
    return render_template('small.html', title='pyDashie')

@flask_app.route("/dashboard/<dashlayout>/")
def custom_layout(dashlayout):
    return render_template('%s.html'%dashlayout, title='pyDashie')

@flask_app.route("/assets/application.js")
def javascripts():
    if not hasattr(current_app, 'javascripts'):
        import coffeescript
        scripts = [
            'assets/javascripts/jquery.js',
            'assets/javascripts/es5-shim.js',
            'assets/javascripts/d3.v2.min.js',

            'assets/javascripts/batman.js',
            'assets/javascripts/batman.jquery.js',

            'assets/javascripts/jquery.gridster.js',
            'assets/javascripts/jquery.leanModal.min.js',

            #'assets/javascripts/dashing.coffee',
            'assets/javascripts/dashing.gridster.coffee',

            'assets/javascripts/jquery.knob.js',
            'assets/javascripts/rickshaw.min.js',
            'assets/javascripts/dashing-chartjs.coffee',
            #'assets/javascripts/application.coffee',
            'assets/javascripts/app.js',
            #'widgets/clock/clock.coffee',
            'widgets/number/number.coffee',
            'widgets/linechart/linechart.coffee',
        ]
        nizzle = True
        if not nizzle:
            scripts = ['assets/javascripts/application.js']

        output = []
        for path in scripts:
            output.append('// JS: %s\n' % path)
            if '.coffee' in path:
                log.info('Compiling Coffee for %s ' % path)
                contents = coffeescript.compile_file(path)
            else:
                f = open(path)
                contents = f.read()
                f.close()

            output.append(contents)

        if nizzle:
            f = open('/tmp/foo.js', 'w')
            for o in output:
                print(o, end="", file=f)
            f.close()

            f = open('/tmp/foo.js', 'rb')
            output = f.read()
            f.close()
            current_app.javascripts = output
        else:
            current_app.javascripts = ''.join(output)

    return Response(current_app.javascripts, mimetype='application/javascript')

@flask_app.route('/assets/application.css')
def application_css():
    scripts = [
        'assets/stylesheets/application.css',
    ]
    output = ''
    for path in scripts:
        output = output + open(path).read()
    return Response(output, mimetype='text/css')

@flask_app.route('/assets/images/<path:filename>')
def send_static_img(filename):
    directory = os.path.join('assets', 'images')
    return send_from_directory(directory, filename)

@flask_app.route('/views/<widget_name>.html')
def widget_html(widget_name):
    html = '%s.html' % widget_name
    path = os.path.join('widgets', widget_name, html)
    if os.path.isfile(path):
        f = open(path)
        contents = f.read()
        f.close()
        return contents

import queue

class EventsManager:
    def __init__(self):
        self.events_queue = {}
        self.last_events = {}
        self.using_events = True
        self.MAX_QUEUE_LENGTH = 20
        self.stopped = False


events_manager = EventsManager()

@flask_app.route('/events')
def events():
    if events_manager.using_events:
        event_stream_port = request.environ['REMOTE_PORT']
        current_event_queue = queue.Queue()
        events_manager.events_queue[event_stream_port] = current_event_queue
        current_app.logger.info('New Client %s connected. Total Clients: %s' %
                                (event_stream_port, len(events_manager.events_queue)))

        #Start the newly connected client off by pushing the current last events
        for event in events_manager.last_events.values():
            current_event_queue.put(event)
        return Response(pop_queue(current_event_queue), mimetype='text/event-stream')

    return Response(events_manager.last_events.values(), mimetype='text/event-stream')

def pop_queue(current_event_queue):
    while not events_manager.stopped:
        try:
            data = current_event_queue.get(timeout=0.1)
            yield data
        except queue.Empty:
            #This makes the server quit nicely - previously the queue threads would block and never exit.
            #  This makes it keep checking for dead application
            pass

def purge_streams():
    big_queues = [port for port, queue in events_manager.events_queue.items()
                  if queue.qsize() > events_manager.MAX_QUEUE_LENGTH]

    for big_queue in big_queues:
        current_app.logger.info('Client %s is stale. Disconnecting. Total Clients: %s' %
                                (big_queue, events_manager.events_queue.qsize()))
        del queue[big_queue]

def close_stream(*args, **kwargs):
    event_stream_port = args[2][1]
    del events_manager.events_queue[event_stream_port]
    log.info('Client %s disconnected. Total Clients: %s' % (event_stream_port, len(events_manager.events_queue)))


def run_sample_app():
    import socketserver
    socketserver.BaseServer.handle_error = close_stream
    import app
    app.run(flask_app, events_manager)


if __name__ == "__main__":
    run_sample_app()