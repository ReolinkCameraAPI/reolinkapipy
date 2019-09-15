from Camera import Camera

c = Camera("192.168.1.112", "admin", "jUa2kUzi")
# print("Getting information", c.get_information())
c.open_video_stream()
