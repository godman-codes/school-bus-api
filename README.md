# school-bus-api
This is a school bus tracking application API built with python flask framework and flasgger UI. This API gets a bus location through a mounted android device on the bus which the driver can log in to and can relay the location of the device as the driver's location.
This API has three modules:
- The school admin module.
- The driver module.
- The parent module. 
The admin module control most of the activities including registering drivers, bus, kids, parents, routes, trips etc.
The parent module gets the kid's trip and tracks it. It also gets notified when there is an important action like when the parent's child enters the bus as well as when the child leaves the bus.
The driver module gets scheduled trips associated with the user driver, logs in students' info as they enter and drop off the bus, get device location as bus location as well as start trips when its capacity is reached and ends trip after completing each trip.
For further info read the swagger documentation files in the docs folder.
