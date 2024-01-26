import reolinkapi
import json

if __name__ == "__main__":
    hostname = "watchdog1"

    try:
        cam = reolinkapi.Camera(hostname, username="userid", password="passwd")
    except:
        print(f"Failed to open camera {hostname}")
        exit(1)

    if not cam.is_logged_in():
        print(f"Login failed for {hostname}")
        exit(1)


    print( json.dumps( cam.get_information(), indent=4 ) )
    print( json.dumps( cam.get_network_general(), indent=4 ) )
    print( json.dumps( cam.get_network_ddns(), indent=4 ) )
    print( json.dumps( cam.get_network_ntp(), indent=4 ) )
    print( json.dumps( cam.get_network_email(), indent=4 ) )
    print( json.dumps( cam.get_network_ftp(), indent=4 ) )
    print( json.dumps( cam.get_network_push(), indent=4 ) )
    print( json.dumps( cam.get_network_status(), indent=4 ) )
    print( json.dumps( cam.get_recording_encoding(), indent=4 ) )
    print( json.dumps( cam.get_recording_advanced(), indent=4 ) )
    print( json.dumps( cam.get_general_system(), indent=4 ) )
    print( json.dumps( cam.get_performance(), indent=4 ) )
    print( json.dumps( cam.get_dst(), indent=4 ) )
    print( json.dumps( cam.get_online_user(), indent=4 ) )
    print( json.dumps( cam.get_users(), indent=4 ) )


