import time
from flask import Response, stream_with_context


class LogStreamer:
    """
    LogStreamer class to handle logging and streaming of log messages.
    This class is used to log messages and stream them to the client in real-time.
    It uses Flask's Response and stream_with_context to create a server-sent event (SSE) stream.
    """

    def __init__(self):
        self._messages = []

    def log(self, message: str, source: str = ""):
        """
        Log a message with a timestamp and optional source.
            :param message: The message to log.
            :param source: Optional source of the message (e.g., "StockMarketController").

            :return: None
        """
        # get the current time and format it
        timestamp = time.strftime("[%H:%M:%S] - ")
        date = time.strftime("[%d.%m.%Y]")
        # format the message with the timestamp and source
        prefix = f"[{source}] " if source else ""
        full_message = f"{timestamp}{prefix}{message} {date}"
        self._messages.append(full_message)  # add the message to the list

    def stream(self):
        """
        Stream the log messages to the client using server-sent events (SSE).
        This method creates a generator that yields log messages as they are added.
        The client can connect to this stream to receive real-time updates.

            :return: A Flask Response object that streams log messages.
        """
        def event_stream():
            last_index = 0

            while True:
                # Check if there are new messages to send
                if len(self._messages) > last_index:
                    # Send the new messages to the client
                    yield f"data: {self._messages[last_index]}\n\n"
                    last_index += 1
                time.sleep(1)
        return Response(stream_with_context(event_stream()), mimetype="text/event-stream")