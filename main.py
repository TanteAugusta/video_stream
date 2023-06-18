import cv2
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from pymavlink import mavutil

app = FastAPI()

origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app = FastAPI()


def video_frames():
    video_capture = cv2.VideoCapture(0)
    while True:
        _, frame = video_capture.read()
        if frame is None:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


def mavlink_frames():

    device = "/dev/tty0"
    baud = 57600

    connection = mavutil.mavlink_connection(device=device, baud=baud)

    while True:
        message = connection.recv_match()
        if message:
            yield (message)


@app.get('/video_feed')
def video_feed():
    return StreamingResponse(video_frames(),
                             media_type='multipart/x-mixed-replace; boundary=frame')


@app.get('/connection_data')
def video_feed():
    return StreamingResponse(mavlink_frames(),
                             media_type='multipart/x-mixed-replace; boundary=frame')


@app.get('/')
def home():
    return {'message': 'Welcome to the webcam streaming server.'}

